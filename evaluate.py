"""Recreate CardioRelay's retrospective audit from the bundled UCI tables.

This project is a prototype and is not medical advice.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parent
SEED = 42
TARGET_RECALL = 0.85
CAPACITY_FRACTIONS = (0.25, 0.50, 0.75)
PRIMARY_CAPACITY = 0.50
BOOTSTRAP_DRAWS = 3000
CONTINUOUS = ["age", "resting_bp"]
CATEGORICAL = ["sex", "chest_pain"]
FEATURES = CONTINUOUS + CATEGORICAL
SITES = [
    ("cleveland", "Cleveland holdout", "cleveland"),
    ("hungary", "Hungarian Institute", "hungarian"),
    ("switzerland", "Swiss cohort", "switzerland"),
    ("long-beach-va", "Long Beach VA", "va"),
]
POLICIES = [
    {"id": "logistic", "label": "CardioRelay", "description":
     "Logistic regression using four intake fields. The cutoff was fixed on Cleveland validation records."},
    {"id": "chest-pain", "label": "Chest-pain category only", "description":
     "Uses the Cleveland training disease rate for each recorded chest-pain category as its score."},
    {"id": "flag-all", "label": "Flag every record", "description":
     "Flags every archived record for review, which catches every positive case and maximizes review volume."},
    {"id": "flag-none", "label": "Flag no records", "description":
     "Flags no records for priority review and misses every archived positive case."},
]
CHEST_PAIN = {
    1.0: "Typical angina",
    2.0: "Atypical angina",
    3.0: "Non-anginal pain",
    4.0: "Asymptomatic category",
}


def read_site(file_suffix):
    """Retain published fields available before downstream testing."""
    path = ROOT / f"{file_suffix}_intake.csv"
    data = pd.read_csv(path, dtype=float)
    if not data["diagnosis"].isin(range(5)).all():
        raise ValueError(f"Missing or unexpected diagnosis in {path.name}.")
    frame = data[FEATURES].copy()
    frame.loc[frame["resting_bp"].le(0), "resting_bp"] = np.nan
    frame.loc[~frame["chest_pain"].isin(CHEST_PAIN), "chest_pain"] = np.nan
    frame.loc[~frame["sex"].isin([0.0, 1.0]), "sex"] = np.nan
    frame["positive"] = data["diagnosis"].gt(0)
    return frame


def intake_model():
    numeric = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    categorical = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore")),
    ])
    transform = ColumnTransformer([
        ("measurements", numeric, CONTINUOUS),
        ("categories", categorical, CATEGORICAL),
    ])
    return Pipeline([
        ("intake", transform),
        ("logistic", LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000)),
    ])


def symptom_score(frame, rates, fallback):
    return frame["chest_pain"].map(rates).fillna(fallback).to_numpy()


def recall_threshold(labels, score):
    """Largest attainable cutoff meeting the predefined validation recall."""
    positive_scores = np.sort(np.asarray(score)[np.asarray(labels)])[::-1]
    required = int(np.ceil(TARGET_RECALL * len(positive_scores)))
    if not required:
        raise ValueError("Threshold selection requires positive validation cases.")
    return float(positive_scores[required - 1])


def fraction(count, total):
    return float(count / total) if total else None


def wilson(count, total):
    if not total:
        return None
    z = 1.95996398454
    observed = count / total
    denominator = 1 + z**2 / total
    center = (observed + z**2 / (2 * total)) / denominator
    radius = z * np.sqrt(observed * (1 - observed) / total + z**2 / (4 * total**2)) / denominator
    return [max(0.0, float(center - radius)), min(1.0, float(center + radius))]


def summarize(labels, score, threshold, policy, *, add_ranking=True):
    flagged = score >= threshold
    tn, fp, fn, tp = map(int, confusion_matrix(labels, flagged, labels=[False, True]).ravel())
    positive = tp + fn
    negative = tn + fp
    n = positive + negative
    has_classes = positive > 0 and negative > 0
    return {
        **policy,
        "n": n,
        "positive": positive,
        "negative": negative,
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "recall": fraction(tp, positive),
        "fpr": fraction(fp, negative),
        "precision": fraction(tp, tp + fp),
        "accuracy": fraction(tp + tn, n),
        "flagRate": fraction(tp + fp, n),
        "recallCI": wilson(tp, positive),
        "fprCI": wilson(fp, negative),
        "auc": float(roc_auc_score(labels, score)) if has_classes and add_ranking else None,
        "ap": float(average_precision_score(labels, score)) if has_classes and add_ranking else None,
    }


def describe_groups(frame, score, threshold):
    categories = [
        ("sex-female", "Recorded female", frame["sex"].eq(0)),
        ("sex-male", "Recorded male", frame["sex"].eq(1)),
        ("age-under55", "Age under 55", frame["age"].lt(55)),
        ("age-55plus", "Age 55 and over", frame["age"].ge(55)),
    ]
    return [
        summarize(frame.loc[mask, "positive"], score[mask.to_numpy()], threshold,
                  {"id": key, "label": label}, add_ranking=False)
        for key, label, mask in categories
    ]


def describe_site(frame, site_id, site_label, model, rates, fallback, threshold, symptom_threshold):
    logistic_scores = model.predict_proba(frame[FEATURES])[:, 1]
    scores = [
        (logistic_scores, threshold),
        (symptom_score(frame, rates, fallback), symptom_threshold),
        (np.ones(len(frame)), 0.5),
        (np.zeros(len(frame)), 0.5),
    ]
    rows = [
        summarize(frame["positive"], score, cutoff, policy)
        for (score, cutoff), policy in zip(scores, POLICIES)
    ]
    return {
        "id": site_id,
        "label": site_label,
        "rows": rows,
        "groups": describe_groups(frame, logistic_scores, threshold),
        "missing": {name: int(frame[name].isna().sum()) for name in FEATURES},
    }, np.stack([logistic_scores, scores[1][0]])


def expected_true_flags(labels, score, budget):
    """Expected number of positives found by a top-budget review queue.

    Include every score strictly above the cutoff. Allocate the remaining
    slots uniformly among the exact ties at the cutoff. Outcomes are counted
    after each record's inclusion weight has been determined by scores alone.
    """
    if budget == 0:
        return 0.0
    cutoff_index = len(score) - budget
    cutoff = np.partition(score, cutoff_index)[cutoff_index]
    above = score > cutoff
    tied = score == cutoff
    slots = budget - np.count_nonzero(above)
    tie_weight = slots / np.count_nonzero(tied)
    return float(np.count_nonzero(above & labels) + tie_weight * np.count_nonzero(tied & labels))


def budget_counts(labels, scores, budget):
    positive = int(labels.sum())
    negative = len(labels) - positive
    rows = []
    for policy, score in zip(POLICIES[:2], scores):
        tp = expected_true_flags(labels, score, budget)
        fn = positive - tp
        fp = budget - tp
        tn = negative - fp
        rows.append({
            **policy, "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "recall": fraction(tp, positive), "fpr": fraction(fp, negative),
            "precision": fraction(tp, budget),
        })
    return rows


def paired_budget_bootstrap(labels, scores, budget, rng):
    """Resample intact cases, preserving both model scores for each draw."""
    differences = np.empty(BOOTSTRAP_DRAWS)
    positives = np.empty(BOOTSTRAP_DRAWS)
    for index in range(BOOTSTRAP_DRAWS):
        sample = rng.integers(len(labels), size=len(labels))
        actual = labels[sample]
        logistic, chest_pain = scores[:, sample]
        differences[index] = (
            expected_true_flags(actual, logistic, budget)
            - expected_true_flags(actual, chest_pain, budget)
        )
        positives[index] = actual.sum()
    return differences, positives


def recall_difference_interval(differences, positives):
    eligible = positives > 0
    if not eligible.any():
        return None
    return np.quantile(differences[eligible] / positives[eligible], [0.025, 0.975]).tolist()


def matched_review_budgets(cohorts):
    """Retrospective ranking stress test at capacities set before scoring."""
    sites = []
    rng = np.random.default_rng(SEED)
    external_primary = {
        "n": 0, "positive": 0, "reviewCount": 0,
        "logisticTP": 0.0, "chestPainTP": 0.0,
    }
    external_differences = np.zeros(BOOTSTRAP_DRAWS)
    external_positives = np.zeros(BOOTSTRAP_DRAWS)
    for site_id, site_label, labels, scores in cohorts:
        n = len(labels)
        positive = int(labels.sum())
        rows = []
        for capacity in CAPACITY_FRACTIONS:
            budget = int(np.floor(capacity * n))
            models = budget_counts(labels, scores, budget)
            tp_difference = models[0]["tp"] - models[1]["tp"]
            interval = None
            if capacity == PRIMARY_CAPACITY:
                differences, positives = paired_budget_bootstrap(labels, scores, budget, rng)
                interval = recall_difference_interval(differences, positives)
                if site_id != "cleveland":
                    external_primary["n"] += n
                    external_primary["positive"] += positive
                    external_primary["reviewCount"] += budget
                    external_primary["logisticTP"] += models[0]["tp"]
                    external_primary["chestPainTP"] += models[1]["tp"]
                    external_differences += differences
                    external_positives += positives
            rows.append({
                "capacity": capacity, "reviewCount": budget,
                "primary": capacity == PRIMARY_CAPACITY, "models": models,
                "recallDifference": fraction(tp_difference, positive), "recallDifferenceCI": interval,
            })
        sites.append({
            "id": site_id, "label": site_label, "n": n,
            "positive": positive, "negative": n - positive, "rows": rows,
        })
    external_primary["recallDifference"] = fraction(
        external_primary["logisticTP"] - external_primary["chestPainTP"],
        external_primary["positive"],
    )
    external_primary["recallDifferenceCI"] = recall_difference_interval(
        external_differences, external_positives,
    )
    return {
        "primaryCapacity": PRIMARY_CAPACITY,
        "capacityFractions": list(CAPACITY_FRACTIONS),
        "rounding": "floor",
        "tieMethod": (
            "Rank by score within each cohort and review floor(capacity × cohort size) records. "
            "When an exact score tie spans the last slot, each tied record receives an equal share "
            "of the remaining slots. This gives expected counts under uniform random tie-breaking."
        ),
        "intervalMethod": (
            f"At 50% capacity, use {BOOTSTRAP_DRAWS:,} paired case-bootstrap draws within each site. "
            "Each resampled case keeps both fixed scores and its outcome. Re-rank at the same "
            "capacity in every draw. Pool site totals for the external result without changing "
            "site sample sizes. Percentile intervals describe recall differences across these "
            "historical cohorts and do not quantify uncertainty at unobserved hospitals."
        ),
        "sites": sites,
        "externalPrimary": external_primary,
    }


def evaluate():
    # Stratify by the binary archive label. Only fit and validation are used
    # before thresholds are fixed. The holdout and external sites stay separate.
    cleveland = read_site("cleveland")
    development, internal_test = train_test_split(
        cleveland, test_size=0.20, random_state=SEED, stratify=cleveland["positive"],
    )
    train, validation = train_test_split(
        development, test_size=0.25, random_state=SEED, stratify=development["positive"],
    )
    model = intake_model().fit(train[FEATURES], train["positive"])
    symptom_rates = train.groupby("chest_pain")["positive"].mean()
    fallback_rate = float(train["positive"].mean())
    validation_scores = model.predict_proba(validation[FEATURES])[:, 1]
    validation_symptom = symptom_score(validation, symptom_rates, fallback_rate)
    threshold = recall_threshold(validation["positive"], validation_scores)
    symptom_threshold = recall_threshold(validation["positive"], validation_symptom)

    # This is the first measured performance on the locked test cohorts.
    results_by_site = []
    ranked_cohorts = []
    for site_id, site_label, file_suffix in SITES:
        frame = internal_test if site_id == "cleveland" else read_site(file_suffix)
        result, ranking_scores = describe_site(
            frame, site_id, site_label, model, symptom_rates, fallback_rate, threshold, symptom_threshold,
        )
        results_by_site.append(result)
        ranked_cohorts.append((site_id, site_label, frame["positive"].to_numpy(), ranking_scores))

    preprocess = model.named_steps["intake"]
    coefficients = model.named_steps["logistic"].coef_[0]
    return {
        "defaultModel": "logistic",
        "models": POLICIES,
        "threshold": threshold,
        "symptomThreshold": symptom_threshold,
        "validationTargetRecall": TARGET_RECALL,
        "seed": SEED,
        "environment": {"sklearn": sklearn.__version__, "numpy": np.__version__, "pandas": pd.__version__},
        "split": {
            "cleveland": len(cleveland),
            "fit": len(train),
            "validation": len(validation),
            "test": len(internal_test),
            "validationPositive": int(validation["positive"].sum()),
        },
        "validation": [
            summarize(validation["positive"], validation_scores, threshold, POLICIES[0]),
            summarize(validation["positive"], validation_symptom, symptom_threshold, POLICIES[1]),
        ],
        "sites": results_by_site,
        "matchedBudget": matched_review_budgets(ranked_cohorts),
        "modelCoefficients": dict(zip(preprocess.get_feature_names_out(), map(float, coefficients))),
        "symptomRates": {str(int(category)): float(rate) for category, rate in symptom_rates.items()},
        "datasetNote": (
            "UCI Heart Disease contains four historical cohorts of patients referred for cardiac workup. "
            "The positive label identifies archived angiographic disease, rather than a future event. "
            "A score is used only to replay a priority review policy. It is not a calibrated probability "
            "or evidence that this policy is safe to use in clinical practice."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results.json")
    args = parser.parse_args()
    results = evaluate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Saved {args.output}")
    for site in results["sites"]:
        logistic = site["rows"][0]
        print(f"{site['label']:20} n={logistic['n']:3} "
              f"missed={logistic['fn']:3} false alarms={logistic['fp']:3} "
              f"ROC AUC={logistic['auc']:.3f}")


if __name__ == "__main__":
    main()

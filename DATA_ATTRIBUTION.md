# UCI Heart Disease data

The four `*_intake.csv` snapshots are adapted from the [UCI Heart Disease archive](https://archive.ics.uci.edu/static/public/45/heart+disease.zip).

Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). *Heart Disease* [Dataset]. UCI Machine Learning Repository. [DOI 10.24432/C52P4X](https://doi.org/10.24432/C52P4X). The repository licenses the dataset under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). The full archive is identified by SHA-256 `b17cd273da9ce1caa4710fce80227ea454d4dbf9fcbc8e6a9121672751563adc`.

The original documentation credits Andras Janosi at the Hungarian Institute of Cardiology in Budapest, William Steinbrunn at University Hospital in Zurich, Matthias Pfisterer at University Hospital in Basel, and Robert Detrano at Cleveland Clinic Foundation and the VA Medical Center in Long Beach.

The original processed files have 14 columns and omit names and identifiers. The snapshots retain the first four fields (age, sex, chest-pain category, and resting blood pressure) and the last field (angiographic diagnosis code), in the original row order. A blank cell represents a `?` missing marker in the source. The evaluator groups diagnosis codes 1–4 as positive and retains 0 as negative.

| Snapshot | Archive member | Rows |
| --- | --- | ---: |
| `cleveland_intake.csv` | `processed.cleveland.data` | 303 |
| `hungarian_intake.csv` | `processed.hungarian.data` | 294 |
| `switzerland_intake.csv` | `processed.switzerland.data` | 123 |
| `va_intake.csv` | `processed.va.data` | 200 |

Chest-pain codes are 1 (typical angina), 2 (atypical angina), 3 (non-anginal pain) and 4 (asymptomatic category). The original sex field uses 0 (female) and 1 (male). It does not encode gender identity. Resting blood pressure is in mm Hg.

# Submit CardioRelay

The deadline is **Sunday, November 15, 2026 at 11:59 p.m. ET**. One person submits for the team. Veritas scores the latest submission received by the deadline. [Official project briefs and submission page](https://highschoolhackathon.org/briefs) · [Submission form](https://airtable.com/appypCyHN77hElIcS/shrXA5VBFdugmoXl6)

## Share the repository

1. Open the prepared [CardioRelay repository](https://github.com/dariusvarvas100-bot/CardioRelay). If it is empty, choose [uploading an existing file](https://github.com/dariusvarvas100-bot/CardioRelay/upload) in Quick setup. If it has files, choose **Add file → Upload files**. Select the updated files from this folder, excluding the hidden `.git` directory, then choose **Commit changes**. If Git is authenticated for GitHub, you can instead push the prepared commit from the local project directory:

   ```sh
   git push -u origin main
   ```

2. Confirm the files appear in the GitHub repository.
3. Open the GitHub link in a private window. Check that the README, code, data, and [one-page write-up](CardioRelay_Writeup.pdf) are visible. Clone or download the repo to run the [demo](demo.html). HTML opened as source on GitHub must be downloaded to use the interactive controls.
4. Upload the one-page PDF on the form. The optional captioned demo, `CardioRelay_Demo.mp4`, is provided separately and runs 89 seconds. You can share it as-is or use the script below to record your own walkthrough. Share the video from Google Drive with viewer access for anyone with the link, or upload it as unlisted to YouTube. Check playback in a private window. Any replacement must be under two minutes.
5. Fill in each contributor’s name, email, and school. Submit and save the confirmation. If the form link above fails to open, use the link in the organizer’s email.

## Draft form answers

| Field | Suggested answer |
|---|---|
| Project title | CardioRelay |
| Building as | Fill in solo or team. |
| Team name and members | Fill in the team name if applicable and each contributor’s full name, email, and school. |
| Track | AI + Health |
| Starting point | 4.1.2 Heart disease risk from checkup data |
| One-sentence pitch | CardioRelay helps a quality-improvement nurse see which archived heart disease cases a Cleveland-trained model misses at other hospitals and compare it with a simpler rule at the same review capacity. |
| Code | Paste the verified public GitHub repository URL. |
| Write-up | Upload CardioRelay_Writeup.pdf. |
| Demo video | Paste the verified video link if included. |
| What we added | CardioRelay first tests whether Cleveland cutoffs travel to three external hospitals. A separate experiment then gives both rankings the same review capacity. Across 308 slots, the four-field model caught 233 archived positives versus an expected 231.8 for the chest pain rule. The interval includes zero, and which rule looked better depended on the site. |
| Datasets, models, and AI tools | [UCI Heart Disease](https://doi.org/10.24432/C52P4X) (Cleveland, Hungarian Institute, Swiss, and Long Beach VA cohorts). Logistic regression and preprocessing in [scikit-learn](https://scikit-learn.org/), with [pandas](https://pandas.pydata.org/) and [NumPy](https://numpy.org/). [OpenAI Codex](https://openai.com/codex/) assisted with design, code, evaluation, and drafting the submission materials. Add any other tools you used. |
| New to AI? | Answer based on your or your team’s experience. |

## Record the demo in under two minutes

Open `demo.html` in a browser and the README in a second tab. Rehearse using both tabs in the dashboard. Check the displayed numbers before recording and use phrasing you can explain in follow-up questions.

| Time | Show | Say |
|---|---|---|
| 0:00–0:14 | Start with the headline. | “Picture a quality-improvement nurse with room to review only half a batch of referrals. CardioRelay uses archived records to show which cases each review rule would have caught or missed.” |
| 0:14–0:39 | Open **Fixed cutoffs** and select **Swiss cohort**. Switch between CardioRelay and the chest pain rule. | “At the two cutoffs chosen in Cleveland, CardioRelay misses 28 of 115 positives in Switzerland. The chest pain rule misses 15, but it sends 13 more records for review. We wanted to know how the rankings compared if the nurse had the same capacity either way.” |
| 0:39–1:13 | Open **Same review budget**, choose **50%**, and select **Swiss cohort**. Point to the identical slot counts and the two results. | “Now each rule gets 61 slots. CardioRelay catches 59 archived positives. The chest pain rule catches an expected 59.8. A fractional count comes from averaging over tied scores at the last slot. At the same workload, the gap is less than one expected case.” |
| 1:13–1:42 | Show the pooled comparison and its interval in the README. | “We fitted on 181 Cleveland records and chose cutoffs on a separate set. In the equal-budget follow-up, each rule got 308 slots across the outside sites. CardioRelay caught 233 positives versus about 232 for the chest pain rule. The uncertainty interval still allows either rule to do better.” |
| 1:42–1:57 | End on the limitations. | “These are archived records from people referred for cardiac workup. The next test would use recent, time-stamped records and the review capacity of a real clinic. This is a prototype and is not medical advice.” |

## Rehearse for questions

- **What is the original contribution?** The brief suggests cross-hospital testing and the original dataset authors did it. Our contribution is comparing the frozen cutoffs separately from the rankings under identical review capacity, then exposing both in a nurse-facing audit.
- **Why is the 85% target different from the test result?** We set the threshold using 28 positive Cleveland validation records. CardioRelay flagged 24 of those, then 20 of 28 on a different Cleveland test set. The external sites have their own case mixes and measurement practices. The observed change alone cannot tell us how much is due to sampling or which site differences mattered most.
- **Did you use hospital labels to choose a new threshold?** No. In the fixed-cutoff test each rule uses its Cleveland threshold. In the capacity test the available slots and each batch’s scores determine the ranking boundary. The recorded disease labels are used afterward to count hits, misses, and false flags. This is a batch-ranking simulation.
- **Why can the chest pain rule have fractional cases?** Its category scores often tie. If the last three slots go to a tie of ten records, each tied record has a 3-in-10 chance of selection. The average number of positives selected can therefore be fractional. The actual nurse would need a prospectively defined tie-break.
- **Did you prove the methods are equivalent? Could the same comparison favor another site?** The primary pooled estimate was +0.31 percentage points, with a 95% interval of −1.77 to +2.60 points. This leaves room for an advantage in either direction. At half capacity, the mean favored CardioRelay at Long Beach VA and favored the chest pain rule in Hungary and Switzerland. The pooled result weights positive cases across these three cohorts.
- **How should I read the uncertainty interval?** The bootstrap resamples within each site and keeps the two scores paired by record. It shows how the average difference can vary across similar drawn records from the same sites. It cannot establish transfer to a new hospital.
- **Did you plan the capacity test before seeing any results?** It was an exploratory follow-up prompted by the different workloads in the first test. The 25%, 50%, and 75% budgets and the primary 50% comparison were specified before running the follow-up. None of the external outcomes were used to refit the scores.
- **If you review half, why is Swiss recall only about half?** There are 115 archived positives among 123 records. With 61 slots, even a perfect ranking could catch at most 61 of those 115.
- **Why did you use recorded sex, and do the error counts show it caused the gap?** Recorded sex was one of the four intake fields. A subgroup gap in one archived cohort cannot tell us whether that feature, referral criteria, case mix, or another difference caused it. A follow-up should compare models with and without it on contemporary data and measure subgroup misses at the same review capacity.
- **Why report recall at a fixed budget if you already have AUROC?** AUROC asks how well scores rank a randomly chosen positive above a randomly chosen negative across the full score range. The nurse has a specific number of slots. A model can rank better overall and still catch fewer positives among the first records sent for review.
- **Who did the model miss?** At its fixed cutoff in Hungary, CardioRelay flagged none of 12 archived positives coded female and 69 of 94 coded male. Those denominators and the wide interval for the smaller group matter. The comparison motivates a follow-up audit and does not establish a cause.
- **What would make you keep the simpler rule?** If the model cannot catch more positive cases at a clinic’s actual review capacity, or if a larger contemporary evaluation shows an unacceptable subgroup miss rate, keep the simpler comparator while investigating. Check input availability and review workflow with the care team before testing prospectively.
- **What did Codex contribute?** Be specific about where the tool helped. Explain the split, baseline, operating cutoff, and capacity comparison yourself by walking through the code and dashboard.

If you advance, use the [five-minute live demo plan](judging-notes.md#five-minute-finals-rehearsal) to rehearse the longer presentation. The same notes map the project to the rubric and identify the presentation patterns taken from prior projects.

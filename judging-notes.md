# Presentation references

Veritas AI’s participant guide identifies the 2026 International High School Hackathon as its first edition. The organizer schedules the first awards for November 21, 2026. The **ScamCheck** packet is the organizer’s example submission with a fictional team. It shows how to combine a named user, original test question, baseline, and visible failure in a small project. [Official hackathon FAQ](https://highschoolhackathon.org/faq) · [Project briefs](https://highschoolhackathon.org/briefs)

| Reference | What CardioRelay takes from its structure |
|---|---|
| Veritas AI’s student project gallery, featuring Srihari’s Fellowship project on lung cancer detection from CT scans. This is a showcase project. | Give the reader the task and the output in the opening paragraph. Explain the role of a second review in plain language. [Veritas AI student projects](https://www.veritasai.com/student-projects) |
| **TuneIn**, the Texas 7th District winner of the 2025 Congressional App Challenge. The official announcement describes how it uses machine learning to improve access to speech and other important sounds. | Start with a specific user and show an input produce a discernible outcome. In CardioRelay, change the cohort or review rule and show how the missed cases and workload change. [Congressional App Challenge winner announcement](https://www.congressionalappchallenge.us/25-TX07/) |
| **WeCAViT**, winner of an IEEE third-place special award at the 2025 Regeneron ISEF. Its abstract compares an X-ray classifier with named benchmarks and identifies generalization to other datasets as future work. | State the reference baseline and separate performance within the source site from the question of transfer to unfamiliar sites. [ISEF abstract](https://abstracts.societyforscience.org/Home/FullAbstract?ProjectId=27195) · [Official award results](https://www.societyforscience.org/press-release/regeneron-isef-2025-special-awards-winners/) |
| **AIM-AI**, recipient of a third award at the 2023 Regeneron ISEF. Its submission states the number of held-out cases and shows how a model fits into a medical imaging workflow. | State what goes into the audit and what the nurse sees. Report the test denominator next to the result. [ISEF abstract and award](https://abstracts.societyforscience.org/Home/FullAbstract?ProjectId=24161) |

## Round 1 rubric

| Criterion | Points | What reviewers can inspect |
|---|---:|---|
| Technical execution | 30 | The evaluator reproduces the results from the four bundled intake snapshots. The demo shows the matching counts and responds to changes in site, review rule, and capacity. |
| Originality | 20 | The brief already suggests testing across hospitals. The additional question is what happens when two rankings get the same number of review slots. The audit shows that separately from cutoff transfer. |
| Impact and track fit | 20 | A quality-improvement nurse can see what a simulated review policy would cost in slots and missed archived positive cases. Misses and workload remain visible together. |
| Testing and honesty | 15 | Cleveland has distinct fitting, validation, and test sets. Three external sites stay out of both fit and cutoff selection. Matching capacity controls for workload. The report exposes score ties, uncertainty, small groups, and failure cases. |
| Communication | 15 | The one-page report states each experiment and its result. The demo changes a concrete input and lets a reviewer watch the result change. |

The live finals award 30 points each for demo and clarity and technical depth, plus 20 each for impact and Q&A. The final ranking weights the live round at 70% and the first round at 30%. [Veritas AI judging criteria](https://highschoolhackathon.org/judges)

## Five-minute finals rehearsal

| Time | What to show |
|---|---|
| 0:00–0:30 | State the nurse’s decision and the retrospective scope. Give a concrete example of a queue with space for half its records. |
| 0:30–1:30 | Show the Swiss cohort in **Fixed cutoffs**. Switch the rule to show how better recall can come with more reviews. |
| 1:30–2:40 | Switch to **Same review budget**, choose 50%, and explain the case counts and what changes when you switch sites. Use the UI to show that each rule has exactly the same number of slots. |
| 2:40–3:45 | Explain the Cleveland split, score construction, choice of cutoff, and how tie handling and the paired interval work. Point to the two different evaluation questions in the report. |
| 3:45–4:30 | Show a failure or subgroup finding. Name the denominator and one unknown that the archive cannot answer. |
| 4:30–5:00 | Define what you would test on recent data and what result would cause you to keep the simpler rule. |

Rehearse the [two-minute submission recording and Q&A](submission.md) before expanding to the live format. [Veritas AI finals format](https://highschoolhackathon.org/about)

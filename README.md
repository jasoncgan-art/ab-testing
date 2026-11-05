# A/B Test Analysis: Should We Ship the New Landing Page?

An end-to-end experiment analysis on a real public A/B test dataset
(Udacity e-commerce landing page test, Jan 2–24, 2017, N = 294,478).

## TL;DR
**Don't ship.** The new page converted at 11.88% vs 12.04% for the old page
(−0.16 pp, p = 0.19, 95% CI [−0.39 pp, +0.08 pp]). The difference is not
significant, and it is smaller than the minimum detectable effect (0.34 pp),
so the experiment cannot rule out a zero or small negative effect either.
The honest next step is a longer run or a bigger change, not a launch.

## Data
`data/ab_data.csv` (downloaded from the public GitHub mirror of the
Udacity dataset). Columns: user_id, timestamp, group, landing_page, converted.

Data quality issues found and fixed:
- 3,893 rows where `group` and `landing_page` disagree — dropped, they cannot
  be trusted to have received the assigned page.
- Duplicate user_ids — kept the first visit per user.
- Cleaned N = 290,584 (control 145,274 / treatment 145,310).

## Results

| Check | Result |
|---|---|
| SRM (randomization) | split 49.99% / 50.01%, chi2 = 0.00, p = 0.95 — clean |
| Baseline conversion (control) | 12.04% |
| Treatment conversion | 11.88% |
| Observed lift | −0.16 pp |
| MDE (80% power, alpha 0.05) | 0.34 pp — stated before looking at the result |
| Two-proportion z-test | z = −1.31, p = 0.19 |
| 95% CI for the difference | [−0.39 pp, +0.08 pp] |
| Chi-square test | chi2 = 1.70, p = 0.19 |
| Logistic regression (converted ~ group) | log-odds −0.015 (SE 0.011), OR 0.99, Wald p = 0.19 |

All three tests agree, as they should — the z-test, chi-square, and logistic
regression are three views of the same 2×2 table.

## Segments and time

| Segment | Control | Treatment | Diff |
|---|---|---|---|
| Weekday | 11.98% | 11.94% | −0.04 pp |
| Weekend | 12.20% | 11.72% | −0.48 pp |
| Early (Jan 2–12) | 11.90% | 11.88% | −0.02 pp |
| Late (Jan 13–24) | 12.16% | 11.88% | −0.28 pp |

No segment flips the story. The weekend gap is the largest but it is a
smaller slice of the data and was not significant on its own; it is a
follow-up question, not a conclusion. There is no novelty effect: the
treatment does not start high and fade.

## Why this analysis is trustworthy
- The MDE was computed **before** looking at the result, so the "not
  significant" call is not post-hoc.
- The SRM check confirms randomization worked — a broken split would have
  invalidated everything downstream.
- Three independent tests agree, and the confidence interval shows the true
  effect could be as low as −0.39 pp or as high as +0.08 pp — small either way.

## Reproduce
```bash
python3 src/download.py   # fetches data/ab_data.csv (15.9 MB, not in the repo)
python3 src/analyze.py
```
Dependencies: pandas, numpy, scipy. The data file is fetched from the public
mirror at
https://raw.githubusercontent.com/beery4010/Analyze-AB-Test-Results/master/ab_data.csv

# A/B Testing & Experiment Analysis — Spec

## Question
Should the company ship the new landing page? Answer with numbers, not vibes.

## Data
`data/ab_data.csv` — Udacity e-commerce A/B test (public dataset).
294,478 rows, Jan 2–24, 2017. Columns: user_id, timestamp, group
(control/treatment), landing_page (old_page/new_page), converted (0/1).
Overall conversion ~11.97%. Groups near 50/50 (control 147,202 / treatment 147,276).
Known dirt: 3,893 rows where group and landing_page disagree; 3,894 duplicate
user_ids (290,584 unique users).

## Steps (Jason builds each one, Muse grills before moving on)
0. **Clean.** Drop misaligned rows (group vs landing_page). Dedupe by user_id,
   keep first occurrence. Report cleaned N and group sizes. Grill point: why
   keep-first and not drop-all-dups?
1. **Sanity + EDA.** Overall conversion, conversion by group, daily volume,
   time range. Any day with weird volume or conversion?
2. **SRM check.** Chi-square on the group split vs 50/50. If the split is off,
   randomization is broken and everything after it is suspect.
3. **Power / MDE.** Before looking at the result: given baseline ~12% and the
   cleaned N, what is the minimum detectable effect at 80% power, alpha 0.05?
   State it first, then compare the observed lift to it.
4. **Primary test.** Two-proportion z-test on conversion, plus the 95% CI for
   the difference. Robustness: chi-square and a logistic regression with the
   group indicator. All three must agree.
5. **Segments + time.** Conversion by day (novelty effect?), weekday vs
   weekend, early vs late period. Any segment that flips the story?
6. **Decision + writeup.** Ship / don't ship / run longer, with the numbers.
   README carries a results table. Resume bullets only after grilling.

## Rules
- Measured numbers only. No result claims until computed.
- Nothing ships undefended: each step gets grilled before the next starts.
- Data is public and real (a real company's landing page test), not synthetic.
  Frame it that way on the resume: "public A/B test dataset (N=294k)".

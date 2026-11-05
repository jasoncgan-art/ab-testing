"""A/B test analysis: should the company ship the new landing page?

Data: data/ab_data.csv — Udacity e-commerce A/B test, N=294,478, Jan 2-24 2017.
Columns: user_id, timestamp, group (control/treatment),
landing_page (old_page/new_page), converted (0/1).

Run: python3 src/analyze.py
Only dependency beyond pandas/numpy: scipy.
"""
import numpy as np
import pandas as pd
from scipy import stats

DATA = "data/ab_data.csv"

# ---------- 0. Load + clean ----------
df = pd.read_csv(DATA, parse_dates=["timestamp"])
raw_n = len(df)
# Rows where group and landing page disagree cannot be trusted: drop them.
df = df[(df["group"] == "treatment") == (df["landing_page"] == "new_page")]
misaligned = raw_n - len(df)
# One row per user: keep the first visit.
df = df.drop_duplicates(subset="user_id", keep="first")
clean_n = len(df)

ctrl = df[df["group"] == "control"]
treat = df[df["group"] == "treatment"]
n_c, n_t = len(ctrl), len(treat)
p_c = ctrl["converted"].mean()
p_t = treat["converted"].mean()
p_pool = df["converted"].mean()

print(f"Raw rows: {raw_n} | misaligned dropped: {misaligned} | cleaned N: {clean_n}")
print(f"Control: n={n_c}, converted={ctrl['converted'].sum()}, p={p_c:.4f}")
print(f"Treatment: n={n_t}, converted={treat['converted'].sum()}, p={p_t:.4f}")
print(f"Overall conversion: {p_pool:.4f}")
print(f"Date range: {df['timestamp'].min().date()} to {df['timestamp'].max().date()}")

# ---------- 2. SRM check: is the split really 50/50? ----------
# Chi-square goodness of fit against a 50/50 split.
chi2_srm, p_srm = stats.chisquare([n_c, n_t], f_exp=[clean_n / 2, clean_n / 2])
print(f"\nSRM check: chi2={chi2_srm:.2f}, p={p_srm:.4f} "
      f"(split {n_c / clean_n:.4f} / {n_t / clean_n:.4f})")

# ---------- 3. Power / MDE, stated BEFORE the result ----------
# Two-sided, alpha 0.05, power 0.80, equal groups, normal approximation.
z_alpha = stats.norm.ppf(0.975)
z_beta = stats.norm.ppf(0.80)
# MDE on the absolute difference scale, using the baseline rate.
mde = (z_alpha + z_beta) * np.sqrt(2 * p_c * (1 - p_c) / n_c)
print(f"\nMDE at 80% power, alpha=0.05: {mde:.4f} ({mde * 100:.2f} pp) "
      f"on baseline {p_c:.4f}")
print(f"Observed lift: {p_t - p_c:+.4f} ({(p_t - p_c) * 100:+.2f} pp)")

# ---------- 4. Primary test ----------
# Two-proportion z-test (pooled SE) + 95% CI (unpooled SE).
se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / n_c + 1 / n_t))
z_stat = (p_t - p_c) / se_pool
p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
se_unpooled = np.sqrt(p_c * (1 - p_c) / n_c + p_t * (1 - p_t) / n_t)
ci_lo, ci_hi = (p_t - p_c) - 1.96 * se_unpooled, (p_t - p_c) + 1.96 * se_unpooled
print(f"\nTwo-proportion z-test: z={z_stat:.3f}, p={p_value:.4f}")
print(f"Difference (treatment - control): {p_t - p_c:+.4f}, "
      f"95% CI [{ci_lo:+.4f}, {ci_hi:+.4f}]")

# Robustness 1: chi-square test of independence on the 2x2 table.
table = pd.crosstab(df["group"], df["converted"])
chi2, p_chi, _, _ = stats.chi2_contingency(table)
print(f"Chi-square test: chi2={chi2:.3f}, p={p_chi:.4f}")

# Robustness 2: logistic regression, converted ~ group, fit by IRLS.
# With a single binary predictor this is a re-parameterization of the 2x2
# table; the Wald test on the group coefficient must agree with the z-test.
X = np.column_stack([np.ones(clean_n),
                     (df["group"] == "treatment").astype(float).values])
y = df["converted"].values.astype(float)
beta = np.zeros(2)
for _ in range(25):
    eta = X @ beta
    mu = 1 / (1 + np.exp(-eta))
    W = mu * (1 - mu)
    z = eta + (y - mu) / np.maximum(W, 1e-9)
    beta_new = np.linalg.solve(X.T @ (X * W[:, None]), X.T @ (z * W))
    if np.max(np.abs(beta_new - beta)) < 1e-8:
        beta = beta_new
        break
    beta = beta_new
eta = X @ beta
mu = 1 / (1 + np.exp(-eta))
W = mu * (1 - mu)
cov = np.linalg.inv(X.T @ (X * W[:, None]))
se_b1 = np.sqrt(cov[1, 1])
wald_z = beta[1] / se_b1
p_wald = 2 * (1 - stats.norm.cdf(abs(wald_z)))
print(f"Logistic regression: log-odds of treatment = {beta[1]:+.4f} "
      f"(SE {se_b1:.4f}), odds ratio = {np.exp(beta[1]):.4f}, "
      f"Wald z={wald_z:.3f}, p={p_wald:.4f}")

# ---------- 5. Segments + time ----------
df["date"] = df["timestamp"].dt.date
daily = df.groupby(["date", "group"])["converted"].agg(["mean", "count"]).unstack()
print("\nDaily conversion by group (first 5 days):")
print(daily.head().round(4).to_string())
# Weekday vs weekend.
df["is_weekend"] = df["timestamp"].dt.dayofweek >= 5
for label, sub in [("weekday", df[~df["is_weekend"]]),
                   ("weekend", df[df["is_weekend"]])]:
    pc = sub[sub["group"] == "control"]["converted"].mean()
    pt = sub[sub["group"] == "treatment"]["converted"].mean()
    print(f"{label}: control={pc:.4f} (n={len(sub[sub['group'] == 'control'])}), "
          f"treatment={pt:.4f} (n={len(sub[sub['group'] == 'treatment'])}), "
          f"diff={pt - pc:+.4f}")
# Early vs late period (split at the midpoint of the 23-day window).
mid = pd.Timestamp("2017-01-13")
for label, sub in [("early (Jan 2-12)", df[df["timestamp"] < mid]),
                   ("late (Jan 13-24)", df[df["timestamp"] >= mid])]:
    pc = sub[sub["group"] == "control"]["converted"].mean()
    pt = sub[sub["group"] == "treatment"]["converted"].mean()
    print(f"{label}: control={pc:.4f}, treatment={pt:.4f}, diff={pt - pc:+.4f}")

# ---------- 6. Decision ----------
print("\n--- Decision ---")
print(f"Observed lift {p_t - p_c:+.4f} is smaller than the MDE {mde:.4f} "
      f"and not significant (p={p_value:.3f}).")
print("The new page does not beat the old page on conversion. Do not ship "
      "on this evidence; the experiment was underpowered for an effect "
      "this small, so the honest options are run longer (bigger N) or "
      "test a bigger change.")

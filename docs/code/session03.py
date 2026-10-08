# Session 3 · Potential outcomes
# Python code extracted from sessions/03-potential-outcomes.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

yule = pd.read_stata("data/yule.dta")
print(smf.ols("paup ~ outrelief + old + pop", data=yule).fit().summary().tables[1])

# ---- step 2 ----
hiv = pd.read_stata("data/thornton_hiv.dta").dropna(subset=["got", "any"])
print(hiv.groupby("any")["got"].mean().round(3))

m = smf.ols("got ~ any", data=hiv).fit(cov_type="cluster",
                                        cov_kwds={"groups": hiv["villnum"]})
print(m.summary().tables[1])

# ---- step 3 ----
import itertools

ri = pd.read_stata("data/ri.dta")
y = ri["y"].to_numpy()
d = ri["d"].to_numpy()
obs = y[d == 1].mean() - y[d == 0].mean()

stats = []
for treated in itertools.combinations(range(8), 4):
    mask = np.zeros(8, dtype=bool); mask[list(treated)] = True
    stats.append(y[mask].mean() - y[~mask].mean())
stats = np.array(stats)

p = (np.abs(stats) >= abs(obs)).mean()
print(f"observed diff = {obs:.2f}, exact two-sided p = {p:.3f} over {len(stats)} assignments")

# ---- step 4 ----
rng = np.random.default_rng(1)
got = hiv["got"].to_numpy(); anyv = hiv["any"].to_numpy()
obs = got[anyv == 1].mean() - got[anyv == 0].mean()

perm = np.empty(1000)
for i in range(1000):
    a = rng.permutation(anyv)
    perm[i] = got[a == 1].mean() - got[a == 0].mean()

print("observed:", round(obs, 3))
print("largest |placebo| diff:", np.abs(perm).max().round(3))
print("p-value:", (np.abs(perm) >= abs(obs)).mean())

# Session 5 · Regression discontinuity
# Python code extracted from sessions/05-rdd.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

lmb = (pd.read_stata("data/close_elections_lmb.dta")
         .dropna(subset=["score", "lagdemvoteshare", "lagdemocrat"]))   # 11 rows lack a lagged vote share
lmb["dem_c"] = lmb.lagdemvoteshare - 0.5          # centered running variable

bins = lmb.groupby(pd.cut(lmb.lagdemvoteshare, np.arange(0, 1.01, 0.02)), observed=True)["score"].mean()
ax = bins.plot(marker="o", linestyle="")
ax.axvline(x=24.5, color="grey")                   # the 0.50 bin boundary
ax.set_xlabel("Democratic vote share, previous election (binned)")
ax.set_ylabel("ADA score of the representative")
plt.show()

# ---- step 2 ----
def fit(df, formula):
    return smf.ols(formula, data=df).fit(cov_type="cluster", cov_kwds={"groups": df["id"]})

all_ = fit(lmb, "score ~ lagdemocrat")
close = fit(lmb[(lmb.lagdemvoteshare > 0.48) & (lmb.lagdemvoteshare < 0.52)], "score ~ lagdemocrat")
print("all elections:  ", all_.params["lagdemocrat"].round(2), all_.bse["lagdemocrat"].round(2))
print("within ±2 points:", close.params["lagdemocrat"].round(2), close.bse["lagdemocrat"].round(2),
      " n =", int(close.nobs))

# ---- step 3 ----
lmb["dem_c2"] = lmb.dem_c**2
local = lmb[(lmb.lagdemvoteshare > 0.45) & (lmb.lagdemvoteshare < 0.55)]

specs = {
  "linear, all data":     fit(lmb,   "score ~ lagdemocrat * dem_c"),
  "linear, ±5 points":    fit(local, "score ~ lagdemocrat * dem_c"),
  "quadratic, all data":  fit(lmb,   "score ~ lagdemocrat * (dem_c + dem_c2)"),
  "quadratic, ±5 points": fit(local, "score ~ lagdemocrat * (dem_c + dem_c2)"),
}
for k, m in specs.items():
    print(f"{k:22s} {m.params['lagdemocrat']:6.2f}  (SE {m.bse['lagdemocrat']:.2f})")

# ---- step 4 ----
# pip install rdrobust
from rdrobust import rdrobust, rdplot
r = rdrobust(y=lmb["score"], x=lmb["lagdemvoteshare"], c=0.5, cluster=lmb["id"])
print(r)
rdplot(y=lmb["score"], x=lmb["lagdemvoteshare"], c=0.5)

# ---- step 5 ----
counts, edges = np.histogram(lmb.lagdemvoteshare.dropna(), bins=np.arange(0.40, 0.61, 0.01))
print(pd.Series(counts, index=edges[:-1].round(2)))

# pip install rddensity
from rddensity import rddensity
dens = rddensity(X=lmb["lagdemvoteshare"], c=0.5)
print(dens.test)           # t_jk is the jackknife test statistic, p_jk its p-value

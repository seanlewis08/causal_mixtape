# Session 4 · Matching and subclassification
# Python code extracted from sessions/04-matching.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

t = pd.read_stata("data/titanic.dta")
t["d"]    = (t["class"] == "1st class").astype(int)
t["surv"] = (t["survived"] == "yes").astype(int)
t["man"]  = (t["sex"] == "man").astype(int)
t["adult"]= (t["age"] == "adults").astype(int)

sdo = t.loc[t.d == 1, "surv"].mean() - t.loc[t.d == 0, "surv"].mean()
print("SDO:", round(sdo, 3))

cell = t.groupby(["man", "adult", "d"])["surv"].mean().unstack("d")
diff = cell[1] - cell[0]
w = t[t.d == 1].groupby(["man", "adult"]).size() / (t.d == 1).sum()
print(pd.DataFrame({"diff": diff.round(3), "treated_share": w.round(3)}))
print("Subclassified ATT:", round((diff * w).sum(), 3))

# ---- step 2 ----
nsw = pd.read_stata("data/nsw_mixtape.dta")
cps = pd.read_stata("data/cps_mixtape.dta")

exp = nsw.loc[nsw.treat == 1, "re78"].mean() - nsw.loc[nsw.treat == 0, "re78"].mean()
print("experimental effect on 1978 earnings:", round(exp, 0))

d = pd.concat([nsw[nsw.treat == 1], cps[cps.treat == 0]], ignore_index=True)
naive = d.loc[d.treat == 1, "re78"].mean() - d.loc[d.treat == 0, "re78"].mean()
print("NSW treated vs CPS controls:", round(naive, 0))

# ---- step 3 ----
d["age2"] = d.age**2;  d["age3"] = d.age**3;  d["educ2"] = d.educ**2
d["u74"]  = (d.re74 == 0).astype(int);  d["u75"] = (d.re75 == 0).astype(int)
d["interaction1"] = d.educ * d.re74

logit = smf.logit("treat ~ age + age2 + age3 + educ + educ2 + marr + nodegree + black "
                  "+ hisp + re74 + re75 + u74 + u75 + interaction1", data=d).fit(disp=0)
d["pscore"] = logit.predict(d)
print(d.groupby("treat")["pscore"].describe()[["mean", "min", "max"]].round(3))

# ---- step 4 ----
ov = d[(d.pscore > 0.1) & (d.pscore < 0.9)].copy()
print("units in overlap:", len(ov), " treated:", int(ov.treat.sum()))

# normalized IPW (ATE)
w1 = ov.treat / ov.pscore
w0 = (1 - ov.treat) / (1 - ov.pscore)
y1 = (w1 * ov.re78).sum() / w1.sum()
y0 = (w0 * ov.re78).sum() / w0.sum()
print("normalized IPW estimate:", round(y1 - y0, 0))

# non-normalized version for comparison
print("non-normalized IPW:", round((w1 * ov.re78).mean() - (w0 * ov.re78).mean(), 0))

# ---- step 5 ----
from sklearn.neighbors import NearestNeighbors

tr = d[d.treat == 1]; co = d[d.treat == 0]
nn = NearestNeighbors(n_neighbors=1).fit(co[["pscore"]].to_numpy())
_, idx = nn.kneighbors(tr[["pscore"]].to_numpy())
att = (tr.re78.to_numpy() - co.re78.to_numpy()[idx[:, 0]]).mean()
print("1-NN ATT on pscore:", round(att, 0))

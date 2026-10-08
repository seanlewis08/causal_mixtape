# Session 1 · Why causal inference, and regression as a tool
# Python code extracted from sessions/01-intro-regression.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

auto = pd.read_stata("data/auto.dta")
auto.head()

m1 = smf.ols("price ~ length", data=auto).fit()
print(m1.summary().tables[1])

# ---- step 2 ----
m2 = smf.ols("price ~ length + weight + headroom + mpg", data=auto).fit()
print(m2.params.round(2))

# ---- step 3 ----
aux = smf.ols("length ~ weight + headroom + mpg", data=auto).fit()
auto["length_resid"] = aux.resid

m3 = smf.ols("price ~ length_resid", data=auto).fit()
print(m3.params.round(2))

# the formula directly
cov = np.cov(auto["price"], auto["length_resid"], ddof=1)[0, 1]
var = auto["length_resid"].var(ddof=1)
print(cov / var)

# ---- step 4 ----
rng = np.random.default_rng(1)
n = 10_000
x = rng.normal(size=n)
u = rng.normal(size=n) * (1 + np.abs(x))      # heteroskedastic
y = 5.5 * x + 12 * u
sim = pd.DataFrame({"x": x, "y": y})

conv = smf.ols("y ~ x", data=sim).fit()
rob  = smf.ols("y ~ x", data=sim).fit(cov_type="HC1")
print("conventional SE:", round(conv.bse["x"], 3))
print("HC1 robust SE:  ", round(rob.bse["x"], 3))

# ---- step 5 ----
g = rng.integers(0, 50, size=n)                   # 50 clusters
group_shock = rng.normal(size=50)[g]
x = rng.normal(size=n) + group_shock
y = 2 * x + 5 * group_shock + rng.normal(size=n)
cl = pd.DataFrame({"x": x, "y": y, "g": g})

plain   = smf.ols("y ~ x", data=cl).fit(cov_type="HC1")
cluster = smf.ols("y ~ x", data=cl).fit(cov_type="cluster", cov_kwds={"groups": cl["g"]})
print(plain.bse["x"].round(3), cluster.bse["x"].round(3))

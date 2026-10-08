# Session 6 · Instrumental variables
# Python code extracted from sessions/06-iv.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from linearmodels.iv import IV2SLS

card = pd.read_stata("data/card.dta")
ctrl = "exper + black + south + married + smsa"

ols = smf.ols(f"lwage ~ educ + {ctrl}", data=card).fit()
print("OLS return to a year of schooling:", ols.params["educ"].round(4))

# ---- step 2 ----
fs = smf.ols(f"educ ~ nearc4 + {ctrl}", data=card).fit()
print("first stage:", fs.params["nearc4"].round(3), " t =", (fs.params["nearc4"] / fs.bse["nearc4"]).round(2))

rf = smf.ols(f"lwage ~ nearc4 + {ctrl}", data=card).fit()
print("reduced form:", rf.params["nearc4"].round(4))
print("Wald ratio:", (rf.params["nearc4"] / fs.params["nearc4"]).round(4))

# ---- step 3 ----
cc = card.dropna(subset=["lwage", "educ", "exper", "black", "south", "married", "smsa", "nearc4"])
iv = IV2SLS.from_formula(f"lwage ~ 1 + {ctrl} + [educ ~ nearc4]", data=cc).fit(cov_type="robust")
print(iv.summary.tables[1])
print(iv.first_stage.diagnostics[["f.stat", "partial.rsquared"]])

# ---- step 4 ----
# Large file (58 MB): read the local copy if you saved one, otherwise download from the book's repo
import os
url = "https://github.com/scunning1975/mixtape/raw/master/judge_fe.dta"
judge = pd.read_stata("data/judge_fe.dta" if os.path.exists("data/judge_fe.dta") else url)

controls = ("white + age + male + black + possess + robbery + DUI1st + aggAss + drugSell "
            "+ fel + mis + threePriors + F1 + F2 + F3 + M1 + M2 + M3 "
            "+ day + day2 + day3 + t1 + t2 + t3 + t4 + t5")
# `sum` and `t6` are dropped: they are linear combinations of the other controls,
# and one judge dummy is dropped because the eight sum to one.
judges = " + ".join(f"judge_pre_{i}" for i in range(1, 8))

ols = smf.ols(f"guilt ~ jail3 + {controls}", data=judge).fit()
iv  = IV2SLS.from_formula(f"guilt ~ 1 + {controls} + [jail3 ~ {judges}]", data=judge).fit(cov_type="robust")
print("OLS  jail3:", ols.params["jail3"].round(3), " SE", ols.bse["jail3"].round(3))
print("2SLS jail3:", iv.params["jail3"].round(3),  " SE", iv.std_errors["jail3"].round(3))
print(iv.first_stage.diagnostics[["f.stat"]])

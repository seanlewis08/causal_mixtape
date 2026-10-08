# Session 7 · Panel data and the 2×2 difference-in-differences
# Python code extracted from sessions/07-panel-did.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from linearmodels.panel import PanelOLS

sasp = pd.read_stata("data/sasp_panel.dta", convert_categoricals=False)

timevar = ["unsafe", "llength", "reg", "asq_cl", "appearance_cl", "provider_second",
           "asian_cl", "black_cl", "hispanic_cl", "othrace_cl", "hot", "massage_cl", "age_cl"]
fixed   = ["age", "asq", "bmi", "hispanic", "black", "other", "asian", "schooling",
           "cohab", "married", "divorced", "separated"]
sasp = sasp.dropna(subset=["lnw", "id"] + timevar + fixed)

pooled = smf.ols("lnw ~ " + " + ".join(timevar + fixed), data=sasp)\
            .fit(cov_type="cluster", cov_kwds={"groups": sasp["id"]})
print("pooled OLS, unsafe:", pooled.params["unsafe"].round(3), " SE", pooled.bse["unsafe"].round(3))

# ---- step 2 ----
# (a) demeaning by hand
dm = sasp.copy()
for v in ["lnw"] + timevar:
    dm[v] = sasp[v] - sasp.groupby("id")[v].transform("mean")
fe_dm = smf.ols("lnw ~ " + " + ".join(timevar), data=dm)\
           .fit(cov_type="cluster", cov_kwds={"groups": dm["id"]})

# (b) unit dummies (slow with many ids, but transparent)
fe_dummy = smf.ols("lnw ~ " + " + ".join(timevar) + " + C(id)", data=sasp).fit()

# (c) PanelOLS
p = sasp.set_index(["id", "session"])
fe_panel = PanelOLS.from_formula("lnw ~ " + " + ".join(timevar) + " + EntityEffects", data=p)\
             .fit(cov_type="clustered", cluster_entity=True)

print("demeaned:", fe_dm.params["unsafe"].round(3),
      " dummies:", fe_dummy.params["unsafe"].round(3),
      " PanelOLS:", fe_panel.params["unsafe"].round(3), " SE", fe_panel.std_errors["unsafe"].round(3))

# ---- step 3 ----
snow = pd.DataFrame({
    "company": ["SV", "SV", "Lambeth", "Lambeth"],
    "year":    [1849, 1854, 1849, 1854],
    "deaths":  [135, 147, 85, 19],
})
snow["treat"] = (snow.company == "Lambeth").astype(int)
snow["post"]  = (snow.year == 1854).astype(int)

by_hand = (19 - 85) - (147 - 135)
reg = smf.ols("deaths ~ treat * post", data=snow).fit()
print("by hand:", by_hand, "  regression:", reg.params["treat:post"].round(1))

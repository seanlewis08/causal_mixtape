# Session 9 · Synthetic control, and which design when
# Python code extracted from sessions/09-synth-wrapup.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pysyncon import Dataprep, Synth        # pip install pysyncon

tx = pd.read_stata("data/texas.dta", convert_categoricals=False)
names = tx.drop_duplicates("statefip").set_index("statefip")["state"]
TEXAS = 48
donors = [s for s in tx.statefip.unique() if s != TEXAS]

dp = Dataprep(
    foo=tx, dependent="bmprison", unit_variable="statefip", time_variable="year",
    treatment_identifier=TEXAS, controls_identifier=donors,
    predictors=["poverty", "income"], predictors_op="mean", time_predictors_prior=range(1985, 1994),
    special_predictors=[
        ("bmprison", range(1988, 1989), "mean"), ("bmprison", range(1990, 1991), "mean"),
        ("bmprison", range(1991, 1992), "mean"), ("bmprison", range(1992, 1993), "mean"),
        ("alcohol", range(1990, 1991), "mean"),  ("aidscapita", range(1990, 1992), "mean"),
        ("black", range(1990, 1992), "mean"),    ("perc1519", range(1990, 1991), "mean"),
    ],
    time_optimize_ssr=range(1985, 1994),
)
synth = Synth()
synth.fit(dataprep=dp, optim_method="BFGS", optim_initial="ols")   # ~20 s; the default Nelder-Mead can take many minutes
w = synth.weights(); w.index = [names[i] for i in w.index]
print(w[w > 0.01].round(3))

# ---- step 2 ----
Z0, Z1 = dp.make_outcome_mats(time_period=range(1985, 2001))
path = pd.DataFrame({"Texas": Z1, "Synthetic Texas": Z0 @ synth.W})
path["gap"] = path["Texas"] - path["Synthetic Texas"]
print(path.round(0))

fig, ax = plt.subplots(1, 2, figsize=(10, 4))
path[["Texas", "Synthetic Texas"]].plot(ax=ax[0]); ax[0].axvline(1993, color="grey", ls="--")
path["gap"].plot(ax=ax[1]); ax[1].axhline(0, color="grey"); ax[1].axvline(1993, color="grey", ls="--")
ax[0].set_ylabel("Black male prisoners"); ax[1].set_ylabel("Texas − synthetic"); plt.tight_layout()

# ---- step 3 ----
#| eval: false
def fit_state(st):
    d = Dataprep(foo=tx, dependent="bmprison", unit_variable="statefip", time_variable="year",
                 treatment_identifier=st, controls_identifier=[s for s in tx.statefip.unique() if s != st],
                 predictors=["poverty", "income"], predictors_op="mean", time_predictors_prior=range(1985, 1994),
                 special_predictors=dp.special_predictors, time_optimize_ssr=range(1985, 1994))
    s = Synth(); s.fit(dataprep=d, optim_method="BFGS", optim_initial="ols")
    Z0, Z1 = d.make_outcome_mats(time_period=range(1985, 2001)); g = Z1 - Z0 @ s.W
    pre  = np.sqrt((g.loc[1985:1993] ** 2).mean())
    post = np.sqrt((g.loc[1994:2000] ** 2).mean())
    return pd.Series({"pre_rmspe": pre, "post_rmspe": post, "ratio": post / pre})

# This loop fits 51 synthetic controls and takes several minutes.
placebo = pd.DataFrame({names[st]: fit_state(st) for st in tx.statefip.unique()}).T
placebo = placebo.sort_values("ratio", ascending=False)
print(placebo.head(10).round(1))
rank = int((placebo.index == "Texas").argmax()) + 1
print(f"Texas rank: {rank} of {len(placebo)}  ->  p = {rank/len(placebo):.3f}")

# ---- step 4 ----
placebo = pd.read_csv("data/texas_placebo_ratios.csv", index_col="state")
print(placebo.head(10))
rank = int((placebo.index == "Texas").argmax()) + 1
print(f"Texas rank: {rank} of {len(placebo)}  ->  p = {rank/len(placebo):.3f}")

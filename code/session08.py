# Session 8 · Difference-in-differences, deep dive
# Python code extracted from sessions/08-did-deep-dive.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

ab = pd.read_stata("data/abortion.dta", convert_categoricals=False)
yrs = list(range(1986, 2001))
ctrl = "acc + ir + pi + alcohol + crack + poverty + income + ur"
needed = ["lnr", "totpop", "fip", "year", "repeal",
          "acc", "ir", "pi", "alcohol", "crack", "poverty", "income", "ur"]

def event_study(df):
    df = df.dropna(subset=needed).copy()
    for y in yrs:
        df[f"rep_{y}"] = ((df.year == y) & (df.repeal == 1)).astype(int)
    f = "lnr ~ " + " + ".join(f"rep_{y}" for y in yrs) + " + C(fip) + C(year) + " + ctrl
    m = smf.wls(f, data=df, weights=df.totpop).fit(cov_type="cluster", cov_kwds={"groups": df["fip"]})
    out = pd.DataFrame({"coef": m.params[[f"rep_{y}" for y in yrs]].to_numpy(),
                        "se":   m.bse[[f"rep_{y}" for y in yrs]].to_numpy()}, index=yrs)
    return out

bf15 = ab[(ab.sex == 2) & (ab.race == 2) & (ab.age == 15)]     # black females 15–19
dd = event_study(bf15)
print(dd.round(3))

ax = dd["coef"].plot(marker="o")
ax.fill_between(dd.index, dd.coef - 1.96*dd.se, dd.coef + 1.96*dd.se, alpha=0.2)
ax.axhline(0, color="grey"); ax.axvspan(1986, 1992, alpha=0.1, color="orange")
ax.set_title("Repeal × year, black women 15–19 (ref. 1985)"); plt.show()

# ---- step 2 ----
bf25 = ab[(ab.sex == 2) & (ab.race == 2) & (ab.age == 25)]
placebo = event_study(bf25)
print(placebo.round(2))

both = ab[(ab.sex == 2) & (ab.race == 2) & (ab.age.isin([15, 25]))].dropna(subset=needed).copy()
both["younger"] = (both.age == 15).astype(int)
for y in yrs:
    both[f"rep_{y}"] = ((both.year == y) & (both.repeal == 1)).astype(int)
    both[f"ry_{y}"]  = both[f"rep_{y}"] * both.younger             # the DDD terms
    both[f"yy_{y}"]  = ((both.year == y) & (both.younger == 1)).astype(int)
both["fip_young"] = both.fip.astype(str) + "_" + both.younger.astype(str)

f = ("lnr ~ " + " + ".join(f"rep_{y}" for y in yrs) + " + " + " + ".join(f"ry_{y}" for y in yrs)
     + " + " + " + ".join(f"yy_{y}" for y in yrs) + " + C(fip_young) + C(year) + " + ctrl)
ddd = smf.wls(f, data=both, weights=both.totpop).fit(cov_type="cluster", cov_kwds={"groups": both["fip"]})
print(pd.DataFrame({"coef": ddd.params[[f"ry_{y}" for y in yrs]].to_numpy(),
                    "se":   ddd.bse[[f"ry_{y}" for y in yrs]].to_numpy()}, index=yrs).round(3))

# ---- step 3 ----
castle = pd.read_stata("data/castle.dta", convert_categoricals=False)
cs = castle.dropna(subset=["l_homicide", "post", "popwt", "sid", "year"])
twfe = smf.wls("l_homicide ~ post + C(sid) + C(year)", data=cs, weights=cs.popwt)\
          .fit(cov_type="cluster", cov_kwds={"groups": cs["sid"]})
print("TWFE post:", twfe.params["post"].round(4), " SE", twfe.bse["post"].round(4))

# adoption timing
castle["D"] = (castle.post > 0).astype(int)
first = castle[castle.D == 1].groupby("sid").year.min()
castle["g"] = castle.sid.map(first).fillna(0).astype(int)
print(castle.groupby("g").sid.nunique())

# ---- step 4 ----
years = sorted(castle.year.unique())
base = smf.ols("l_homicide ~ D + C(sid) + C(year)", data=castle).fit()
print("unweighted binary TWFE:", base.params["D"].round(4))

n    = castle.groupby("g").sid.nunique() / castle.sid.nunique()        # group shares
Dbar = {g: (np.array(years) >= g).mean() if g > 0 else 0 for g in n.index}  # share of periods treated

def dd_2x2(sub):
    """TWFE on a two-group subsample = the 2x2 DD for that comparison."""
    s = sub.copy()
    for v in ["D", "l_homicide"]:
        s[v + "_t"] = s[v] - s.groupby("sid")[v].transform("mean") - s.groupby("year")[v].transform("mean") + s[v].mean()
    return (s.D_t * s.l_homicide_t).sum() / (s.D_t ** 2).sum()

rows = []
G = [g for g in n.index if g > 0]
for k in G:
    rows.append((k, "never-treated", dd_2x2(castle[castle.g.isin([k, 0])]),
                 n[k] * n[0] * Dbar[k] * (1 - Dbar[k])))
    for l in G:
        if l <= k: continue
        nkl = n[k] / (n[k] + n[l])
        # k treated earlier; l (not yet treated) is the control in years before l adopts
        s_kl = ((n[k] + n[l]) * (1 - Dbar[l]))**2 * nkl * (1 - nkl) * (Dbar[k] - Dbar[l]) / (1 - Dbar[l]) * (1 - Dbar[k]) / (1 - Dbar[l])
        rows.append((k, f"later-treated ({l}) as control", dd_2x2(castle[castle.g.isin([k, l]) & (castle.year < l)]), s_kl))
        # l treated later; k (already treated) is the control in years from k's adoption on
        s_lk = ((n[k] + n[l]) * Dbar[k])**2 * nkl * (1 - nkl) * Dbar[l] / Dbar[k] * (Dbar[k] - Dbar[l]) / Dbar[k]
        rows.append((l, f"earlier-treated ({k}) as control", dd_2x2(castle[castle.g.isin([k, l]) & (castle.year >= k)]), s_lk))

bacon = pd.DataFrame(rows, columns=["treated", "control", "dd", "s"])
bacon["weight"] = bacon.s / bacon.s.sum()
bacon["type"] = bacon.control.str.split(" ").str[0]
print(bacon.sort_values("weight", ascending=False).head(8).round(3))
print("weighted sum of 2x2s:", (bacon.weight * bacon.dd).sum().round(4))
print(bacon.groupby("type").apply(lambda x: pd.Series({"weight": x.weight.sum(),
                                                       "avg_dd": (x.weight * x.dd).sum() / x.weight.sum()})).round(3))

# ---- step 5 ----
# Option A: an event study in event time, with never-treated states as the pure controls
cs2 = castle.copy()
cs2["rel"] = (cs2.year - cs2.g).clip(-5, 4)          # event time, binned at the ends
for k in range(-5, 5):
    if k == -1: continue                              # reference period
    cs2[f"ev_{'m' if k < 0 else 'p'}{abs(k)}"] = ((cs2.g > 0) & (cs2.rel == k)).astype(int)
ev = [c for c in cs2.columns if c.startswith("ev_")]
es = smf.wls("l_homicide ~ " + " + ".join(ev) + " + C(sid) + C(year)", data=cs2, weights=cs2.popwt)\
        .fit(cov_type="cluster", cov_kwds={"groups": cs2["sid"]})
print(pd.DataFrame({"coef": es.params[ev], "se": es.bse[ev]}).round(3))

# Option B: Callaway–Sant'Anna via the `csdid` or `differences` packages (pip install differences)
# from differences import ATTgt
# att = ATTgt(data=castle.set_index(["sid", "year"]), cohort_name="g").fit(formula="l_homicide")
# att.aggregate("event")

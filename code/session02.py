# Session 2 · Directed acyclic graphs
# Python code extracted from sessions/02-dags.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

rng = np.random.default_rng(42)
n = 10_000
female = rng.binomial(1, 0.5, n)
ability = rng.normal(size=n)
discrimination = female.copy()
occupation = 1 + 2 * ability + 0 * female - 2 * discrimination + rng.normal(size=n)
wage = 1 - 1 * discrimination + 1 * occupation + 2 * ability + rng.normal(size=n)

tb = pd.DataFrame(dict(female=female, ability=ability, discrimination=discrimination,
                       occupation=occupation, wage=wage))

# ---- step 2 ----
for f in ["wage ~ female",
          "wage ~ female + occupation",
          "wage ~ female + occupation + ability"]:
    print(f, "\n", smf.ols(f, data=tb).fit().params.round(3), "\n")

# ---- step 3 ----
rng = np.random.default_rng(3)
pop = pd.DataFrame({"beauty": rng.normal(size=10_000),
                    "talent": rng.normal(size=10_000)})
pop["score"] = pop.beauty + pop.talent
cutoff = pop.score.quantile(0.85)
pop["star"] = pop.score >= cutoff

print("population corr:", pop[["beauty", "talent"]].corr().iloc[0, 1].round(3))
print("stars corr:     ", pop.loc[pop.star, ["beauty", "talent"]].corr().iloc[0, 1].round(3))

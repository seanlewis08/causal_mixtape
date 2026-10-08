# Session 2 · Directed acyclic graphs
# R code extracted from sessions/02-dags.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
library(tidyverse)
library(estimatr)

set.seed(42)
n <- 10000
tb <- tibble(
  female         = rbinom(n, 1, 0.5),
  ability        = rnorm(n),
  discrimination = female,
  occupation     = 1 + 2 * ability + 0 * female - 2 * discrimination + rnorm(n),
  wage           = 1 - 1 * discrimination + 1 * occupation + 2 * ability + rnorm(n)
)

# ---- step 2 ----
lm_1 <- lm(wage ~ female, data = tb)
lm_2 <- lm(wage ~ female + occupation, data = tb)
lm_3 <- lm(wage ~ female + occupation + ability, data = tb)
modelsummary::modelsummary(list("Biased unconditional" = lm_1,
                                "Biased (collider)"    = lm_2,
                                "Unbiased conditional" = lm_3),
                           gof_omit = ".*")

# ---- step 3 ----
set.seed(3)
pop <- tibble(beauty = rnorm(10000), talent = rnorm(10000)) %>%
  mutate(score = beauty + talent,
         star  = score >= quantile(score, 0.85))

cor(pop$beauty, pop$talent)
with(filter(pop, star), cor(beauty, talent))

ggplot(pop, aes(beauty, talent, colour = star)) +
  geom_point(alpha = 0.3) + theme_minimal()

# ---- step 4 ----
library(dagitty); library(ggdag)

g <- dagitty("dag {
  female -> discrimination
  discrimination -> occupation
  discrimination -> wage
  ability -> occupation
  ability -> wage
  occupation -> wage
}")
adjustmentSets(g, exposure = "discrimination", outcome = "wage", effect = "total")
adjustmentSets(g, exposure = "discrimination", outcome = "wage", effect = "direct")
ggdag(g) + theme_dag()

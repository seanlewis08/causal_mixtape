# Session 5 · Regression discontinuity
# R code extracted from sessions/05-rdd.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
library(tidyverse); library(haven); library(estimatr)

lmb <- read_dta("data/close_elections_lmb.dta") %>%
  drop_na(score, lagdemvoteshare, lagdemocrat) %>%
  mutate(dem_c = lagdemvoteshare - 0.5)

lmb %>%
  mutate(bin = cut(lagdemvoteshare, seq(0, 1, 0.02))) %>%
  group_by(bin) %>% summarise(score = mean(score), x = mean(lagdemvoteshare)) %>%
  ggplot(aes(x, score)) + geom_point() + geom_vline(xintercept = 0.5) + theme_minimal()

# ---- step 2 ----
lm_robust(score ~ lagdemocrat, data = lmb, clusters = id)
lm_robust(score ~ lagdemocrat,
          data = filter(lmb, lagdemvoteshare > 0.48, lagdemvoteshare < 0.52),
          clusters = id)

# ---- step 3 ----
local <- filter(lmb, lagdemvoteshare > 0.45, lagdemvoteshare < 0.55)
lmb   <- mutate(lmb, dem_c2 = dem_c^2); local <- mutate(local, dem_c2 = dem_c^2)

list(
  "linear, all"     = lm_robust(score ~ lagdemocrat * dem_c, data = lmb,   clusters = id),
  "linear, ±5"      = lm_robust(score ~ lagdemocrat * dem_c, data = local, clusters = id),
  "quadratic, all"  = lm_robust(score ~ lagdemocrat * (dem_c + dem_c2), data = lmb,   clusters = id),
  "quadratic, ±5"   = lm_robust(score ~ lagdemocrat * (dem_c + dem_c2), data = local, clusters = id)
) %>% map_dbl(~ coef(.x)["lagdemocrat"])

# ---- step 4 ----
library(rdrobust)
r <- rdrobust(y = lmb$score, x = lmb$lagdemvoteshare, c = 0.5, cluster = lmb$id)
summary(r)
rdplot(y = lmb$score, x = lmb$lagdemvoteshare, c = 0.5)

# ---- step 5 ----
library(rddensity)
dens <- rddensity(X = lmb$lagdemvoteshare, c = 0.5)
summary(dens)
rdplotdensity(dens, lmb$lagdemvoteshare)

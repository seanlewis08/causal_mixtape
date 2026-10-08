# Session 6 · Instrumental variables
# R code extracted from sessions/06-iv.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
library(tidyverse); library(haven); library(estimatr); library(ivreg)

card <- read_dta("data/card.dta")
ols <- lm(lwage ~ educ + exper + black + south + married + smsa, data = card)
coef(ols)["educ"]

# ---- step 2 ----
fs <- lm(educ ~ nearc4 + exper + black + south + married + smsa, data = card)
rf <- lm(lwage ~ nearc4 + exper + black + south + married + smsa, data = card)
coef(fs)["nearc4"]; coef(rf)["nearc4"]
coef(rf)["nearc4"] / coef(fs)["nearc4"]

# ---- step 3 ----
iv <- ivreg(lwage ~ educ + exper + black + south + married + smsa |
              nearc4 + exper + black + south + married + smsa, data = card)
summary(iv, diagnostics = TRUE)

# ---- step 4 ----
judge_path <- if (file.exists("data/judge_fe.dta")) "data/judge_fe.dta" else
  "https://github.com/scunning1975/mixtape/raw/master/judge_fe.dta"
judge <- read_dta(judge_path)

ctrl <- ~ white + age + male + black + possess + robbery + DUI1st + aggAss + drugSell +
  fel + mis + sum + threePriors + F1 + F2 + F3 + M1 + M2 + M3 + day + day2 + day3 +
  t1 + t2 + t3 + t4 + t5 + t6
judges <- paste0("judge_pre_", 1:8, collapse = " + ")

ols <- lm(update(ctrl, guilt ~ jail3 + .), data = judge)
iv  <- ivreg(as.formula(paste("guilt ~ jail3 +", as.character(ctrl)[2],
                              "|", judges, "+", as.character(ctrl)[2])), data = judge)
coef(ols)["jail3"]; coef(iv)["jail3"]
# R drops collinear terms automatically; Python's linearmodels does not, hence the trimmed list above.

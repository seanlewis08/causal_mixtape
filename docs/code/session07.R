# Session 7 · Panel data and the 2×2 difference-in-differences
# R code extracted from sessions/07-panel-did.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
library(tidyverse); library(haven); library(fixest)

sasp <- read_dta("data/sasp_panel.dta")
timevar <- c("unsafe","llength","reg","asq_cl","appearance_cl","provider_second",
             "asian_cl","black_cl","hispanic_cl","othrace_cl","hot","massage_cl","age_cl")
fixed   <- c("age","asq","bmi","hispanic","black","other","asian","schooling",
             "cohab","married","divorced","separated")

f_pooled <- as.formula(paste("lnw ~", paste(c(timevar, fixed), collapse = " + ")))
pooled <- feols(f_pooled, data = sasp, cluster = ~id)
coeftable(pooled)["unsafe", ]

# ---- step 2 ----
f_fe <- as.formula(paste("lnw ~", paste(timevar, collapse = " + "), "| id"))
fe <- feols(f_fe, data = sasp, cluster = ~id)
coeftable(fe)["unsafe", ]

# the same thing by hand
dm <- sasp %>% group_by(id) %>%
  mutate(across(all_of(c("lnw", timevar)), ~ .x - mean(.x, na.rm = TRUE))) %>% ungroup()
coef(lm(as.formula(paste("lnw ~", paste(timevar, collapse = " + "))), data = dm))["unsafe"]

etable(pooled, fe, keep = "unsafe")

# ---- step 3 ----
snow <- tibble(company = c("SV","SV","Lambeth","Lambeth"),
               year = c(1849, 1854, 1849, 1854),
               deaths = c(135, 147, 85, 19)) %>%
  mutate(treat = as.integer(company == "Lambeth"), post = as.integer(year == 1854))

(19 - 85) - (147 - 135)
coef(lm(deaths ~ treat * post, data = snow))["treat:post"]

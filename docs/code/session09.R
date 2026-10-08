# Session 9 · Synthetic control, and which design when
# R code extracted from sessions/09-synth-wrapup.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
library(tidyverse); library(haven); library(tidysynth)   # or library(Synth)

tx <- read_dta("data/texas.dta")

out <- tx %>%
  synthetic_control(outcome = bmprison, unit = state, time = year,
                    i_unit = "Texas", i_time = 1993, generate_placebos = TRUE) %>%
  generate_predictor(time_window = 1985:1993, poverty = mean(poverty), income = mean(income)) %>%
  generate_predictor(time_window = 1988, bmprison_1988 = mean(bmprison)) %>%
  generate_predictor(time_window = 1990, bmprison_1990 = mean(bmprison), alcohol = mean(alcohol),
                     perc1519 = mean(perc1519)) %>%
  generate_predictor(time_window = 1991, bmprison_1991 = mean(bmprison)) %>%
  generate_predictor(time_window = 1992, bmprison_1992 = mean(bmprison)) %>%
  generate_predictor(time_window = 1990:1991, aidscapita = mean(aidscapita), black = mean(black)) %>%
  generate_weights(optimization_window = 1985:1993) %>%
  generate_control()

out %>% grab_unit_weights() %>% filter(weight > 0.01) %>% arrange(desc(weight))

# ---- step 2 ----
out %>% plot_trends()
out %>% plot_differences()

# ---- step 3 ----
out %>% plot_placebos()
out %>% plot_mspe_ratio()
out %>% grab_signficance()      # (sic) returns the rank-based p-value

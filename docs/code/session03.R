# Session 3 · Potential outcomes
# R code extracted from sessions/03-potential-outcomes.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
library(tidyverse); library(haven); library(estimatr)

yule <- read_dta("data/yule.dta")
lm(paup ~ outrelief + old + pop, data = yule) %>% summary()

# ---- step 2 ----
hiv <- read_dta("data/thornton_hiv.dta") %>% drop_na(got, any)
hiv %>% group_by(any) %>% summarise(got = mean(got), n = n())

lm_robust(got ~ any, data = hiv, clusters = villnum)

# ---- step 3 ----
ri <- read_dta("data/ri.dta")
y <- ri$y; d <- ri$d
obs <- mean(y[d == 1]) - mean(y[d == 0])

combos <- combn(8, 4)
stats <- apply(combos, 2, function(idx) mean(y[idx]) - mean(y[-idx]))
p <- mean(abs(stats) >= abs(obs))
c(observed = obs, p_value = p, n_assignments = ncol(combos))

# ---- step 4 ----
set.seed(1)
obs <- with(hiv, mean(got[any == 1]) - mean(got[any == 0]))
perm <- replicate(1000, {
  a <- sample(hiv$any)
  mean(hiv$got[a == 1]) - mean(hiv$got[a == 0])
})
c(observed = obs, max_placebo = max(abs(perm)), p = mean(abs(perm) >= abs(obs)))

ggplot(tibble(perm), aes(perm)) + geom_histogram(bins = 40) +
  geom_vline(xintercept = obs, colour = "red") + theme_minimal()

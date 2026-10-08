# Session 4 · Matching and subclassification
# R code extracted from sessions/04-matching.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
library(tidyverse); library(haven)

t <- read_dta("data/titanic.dta") %>%
  mutate(d = as.integer(class == 1),
         man = as.integer(sex == 1), adult = as.integer(age == 1))
# haven keeps Stata's numeric codes; attributes(t$sex)$labels shows
# 1 = man, and age 1 = adults, class 1 = 1st class, survived 1 = yes

sdo <- with(t, mean(survived[d == 1]) - mean(survived[d == 0]))

att <- t %>%
  group_by(man, adult) %>%
  summarise(diff = mean(survived[d == 1]) - mean(survived[d == 0]),
            n_treated = sum(d == 1), .groups = "drop") %>%
  mutate(w = n_treated / sum(n_treated))
att
sum(att$diff * att$w)

# ---- step 2 ----
nsw <- read_dta("data/nsw_mixtape.dta")
cps <- read_dta("data/cps_mixtape.dta")

with(nsw, mean(re78[treat == 1]) - mean(re78[treat == 0]))

d <- bind_rows(filter(nsw, treat == 1), filter(cps, treat == 0))
with(d, mean(re78[treat == 1]) - mean(re78[treat == 0]))

# ---- step 3 ----
d <- d %>% mutate(age2 = age^2, age3 = age^3, educ2 = educ^2,
                  u74 = as.integer(re74 == 0), u75 = as.integer(re75 == 0),
                  interaction1 = educ * re74)
logit <- glm(treat ~ age + age2 + age3 + educ + educ2 + marr + nodegree + black +
               hisp + re74 + re75 + u74 + u75 + interaction1,
             family = binomial(), data = d)
d$pscore <- predict(logit, type = "response")
d %>% group_by(treat) %>% summarise(mean = mean(pscore), min = min(pscore), max = max(pscore))

ggplot(d, aes(pscore, fill = factor(treat))) +
  geom_histogram(bins = 50, position = "identity", alpha = 0.5) + theme_minimal()

# ---- step 4 ----
ov <- d %>% filter(pscore > 0.1, pscore < 0.9) %>%
  mutate(w1 = treat / pscore, w0 = (1 - treat) / (1 - pscore))

y1 <- with(ov, sum(w1 * re78) / sum(w1))
y0 <- with(ov, sum(w0 * re78) / sum(w0))
y1 - y0

with(ov, mean(w1 * re78) - mean(w0 * re78))

# ---- step 5 ----
library(MatchIt)
m <- matchit(treat ~ age + age2 + age3 + educ + educ2 + marr + nodegree + black +
               hisp + re74 + re75 + u74 + u75 + interaction1,
             data = d, method = "nearest", distance = "glm", replace = TRUE)
md <- match.data(m)
lm(re78 ~ treat, data = md, weights = weights)
summary(m)$sum.matched[, c("Means Treated", "Means Control")]

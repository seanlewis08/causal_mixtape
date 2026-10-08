# Session 1 · Why causal inference, and regression as a tool
# R code extracted from sessions/01-intro-regression.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
library(tidyverse)
library(haven)
library(estimatr)

auto <- read_dta("data/auto.dta")
glimpse(auto)

m1 <- lm(price ~ length, data = auto)
summary(m1)

# ---- step 2 ----
m2 <- lm(price ~ length + weight + headroom + mpg, data = auto)
coef(m2)

# ---- step 3 ----
auto <- auto %>%
  mutate(length_resid = resid(lm(length ~ weight + headroom + mpg, data = auto)))

m3 <- lm(price ~ length_resid, data = auto)
coef(m3)

cov(auto$price, auto$length_resid) / var(auto$length_resid)

# ---- step 4 ----
set.seed(1)
n <- 10000
x <- rnorm(n)
u <- rnorm(n) * (1 + abs(x))
y <- 5.5 * x + 12 * u
sim <- tibble(x, y)

conv <- lm(y ~ x, data = sim)
rob  <- lm_robust(y ~ x, data = sim, se_type = "HC1")
sqrt(diag(vcov(conv)))["x"]
rob$std.error["x"]

# ---- step 5 ----
g <- sample(0:49, n, replace = TRUE)
group_shock <- rnorm(50)[g + 1]
x <- rnorm(n) + group_shock
y <- 2 * x + 5 * group_shock + rnorm(n)
cl <- tibble(x, y, g)

lm_robust(y ~ x, data = cl, se_type = "HC1")$std.error["x"]
lm_robust(y ~ x, data = cl, clusters = g)$std.error["x"]

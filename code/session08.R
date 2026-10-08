# Session 8 · Difference-in-differences, deep dive
# R code extracted from sessions/08-did-deep-dive.qmd
# Run from the repository root so that data/ paths resolve.

# ---- step 1 ----
library(tidyverse); library(haven); library(fixest)

ab <- read_dta("data/abortion.dta")
bf15 <- ab %>% filter(sex == 2, race == 2, age == 15)

dd <- feols(lnr ~ i(year, repeal, ref = 1985) + acc + ir + pi + alcohol + crack +
              poverty + income + ur | fip + year,
            data = bf15, weights = ~totpop, cluster = ~fip)
coeftable(dd)[grepl("year::", rownames(coeftable(dd))), 1:2]
iplot(dd, main = "Repeal × year, black women 15–19 (ref. 1985)")

# ---- step 2 ----
bf25 <- ab %>% filter(sex == 2, race == 2, age == 25)
placebo <- feols(lnr ~ i(year, repeal, ref = 1985) + acc + ir + pi + alcohol + crack +
                   poverty + income + ur | fip + year,
                 data = bf25, weights = ~totpop, cluster = ~fip)
iplot(placebo, main = "Placebo: black women 25–29")

both <- ab %>% filter(sex == 2, race == 2, age %in% c(15, 25)) %>%
  mutate(younger = as.integer(age == 15), fip_young = paste(fip, younger))
ddd <- feols(lnr ~ i(year, repeal, ref = 1985) + i(year, repeal * younger, ref = 1985) +
               i(year, younger, ref = 1985) + acc + ir + pi + alcohol + crack +
               poverty + income + ur | fip_young + year,
             data = both, weights = ~totpop, cluster = ~fip)
iplot(ddd, i.select = 2, main = "DDD: repeal × year × younger")

# ---- step 3 ----
castle <- read_dta("data/castle.dta")
twfe <- feols(l_homicide ~ post | sid + year, data = castle, weights = ~popwt, cluster = ~sid)
coeftable(twfe)

castle <- castle %>% group_by(sid) %>%
  mutate(g = if (any(post > 0)) min(year[post > 0]) else 0) %>% ungroup()
count(distinct(castle, sid, g), g)

# ---- step 4 ----
library(bacondecomp)
castle <- mutate(castle, D = as.integer(post > 0))
bd <- bacon(l_homicide ~ D, data = castle, id_var = "sid", time_var = "year")
# prints the weight and average estimate by comparison type
bd %>% group_by(type) %>% summarise(weight = sum(weight), avg_est = weighted.mean(estimate, weight))
ggplot(bd, aes(weight, estimate, shape = type, colour = type)) + geom_point(size = 3) +
  geom_hline(yintercept = sum(bd$estimate * bd$weight)) + theme_minimal()

# ---- step 5 ----
library(did)
castle_cs <- castle %>% mutate(g_cs = ifelse(g == 0, 0, g))
att <- att_gt(yname = "l_homicide", tname = "year", idname = "sid", gname = "g_cs",
              data = castle_cs, control_group = "nevertreated", weightsname = "popwt")
es <- aggte(att, type = "dynamic", min_e = -5, max_e = 4)
summary(es); ggdid(es)
aggte(att, type = "simple")

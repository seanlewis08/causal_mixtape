pkgs <- c("tidyverse", "haven", "estimatr", "fixest", "modelsummary",
          "dagitty", "ggdag", "MatchIt", "rdrobust", "rddensity",
          "ivreg", "did", "bacondecomp", "Synth", "tidysynth")
new <- pkgs[!(pkgs %in% installed.packages()[, "Package"])]
if (length(new)) install.packages(new)

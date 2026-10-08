# Mixtape Workshops

A chapter-by-chapter workshop series for Scott Cunningham's free textbook
[*Causal Inference: The Mixtape*](https://mixtape-1ed.netlify.app/), built as a
Quarto website with every walkthrough in both Python and R.

- `index.qmd`, `setup.qmd`, `facilitating.qmd` — site front matter
- `sessions/` — one page per 60-minute session (walkthrough, exercises, solutions, facilitator notes)
- `glossary.qmd` — every acronym and term, in plain words
- `slides/` — one reveal.js deck per session, with diagrams in `slides/img/`
- `code/` — the Python and R code from each session as plain files
- `data/` — the datasets (from the book's repo and the `causaldata` package)
- `_freeze/` — cached chunk output
- `docs/` — rendered site (GitHub Pages serves this folder)

## Build

```bash
quarto render          # writes docs/
quarto preview         # live-reloading local server
```

Walkthrough chunks are executed at render time (knitr engine; Python via `reticulate`) and the
results are cached in `_freeze/`, which is committed. Rendering from the cache needs only Quarto;
re-running a page needs R, Python and the packages listed in `setup.qmd`.

## Publish on GitHub Pages

1. Push to GitHub.
2. In the repo settings, under **Pages**, set the source to **Deploy from a branch**, branch `main`, folder `/docs`.
3. Update `site-url` and `repo-url` in `_quarto.yml` and the clone URL in `setup.qmd`.

Re-run `quarto render` and commit `docs/` whenever the content changes.

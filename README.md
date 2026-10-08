# Mixtape Workshops

A chapter-by-chapter workshop series for Scott Cunningham's free textbook
[*Causal Inference: The Mixtape*](https://mixtape-1ed.netlify.app/), built as a
Quarto website with every walkthrough in both Python and R.

- `index.qmd`, `setup.qmd`, `facilitating.qmd` — site front matter
- `sessions/` — one page per 60-minute session (walkthrough, exercises, solutions, facilitator notes)
- `slides/` — one reveal.js deck per session
- `code/` — the Python and R code from each session as plain files
- `data/` — the datasets (from the book's repo and the `causaldata` package)
- `docs/` — rendered site (GitHub Pages serves this folder)

## Build

```bash
quarto render          # writes docs/
quarto preview         # live-reloading local server
```

Code is displayed, not executed, at build time (`execute: enabled: false` in `_quarto.yml`),
so rendering needs only Quarto. To run the analyses, see `setup.qmd`.

## Publish on GitHub Pages

1. Push to GitHub.
2. In the repo settings, under **Pages**, set the source to **Deploy from a branch**, branch `main`, folder `/docs`.
3. Update `site-url` and `repo-url` in `_quarto.yml` and the clone URL in `setup.qmd`.

Re-run `quarto render` and commit `docs/` whenever the content changes.

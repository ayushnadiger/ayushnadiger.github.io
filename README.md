# Ayush Nadiger

Personal academic website: https://ayushnadiger.github.io/

The published site contains the homepage and six project pages, with the original Latin Modern typography and paper-like layout. The two active projects have provisional research overviews, vector figures, model assumptions, and references; the other project pages contain full HTML manuscripts. There are no PDFs or legacy redirect pages.

`tools/build_projects.py` rebuilds the homepage and six project pages using Python, lxml, and Pandoc. Retained TeX sources and browser-native figures live under `assets/papers/`.

`tools/project_content/` contains the active research-page bodies. `tools/build_research_figures.py` reproduces their four SVG figures with matplotlib and numpy. Its retained inputs in `tools/research_data/` come from the 2 November 2026 exact phase-only routing note and the asynchronous-observability revision-9 fresh matched cohort. The diagrams are explicitly labeled schematics. The BB72 plot uses the complete local measurement record and the early-noise-only ablation from the same 32 herald histories; it does not pool older cohorts.

Only the pages, styles, figures, favicon, search metadata, and ownership-verification file are published. `_config.yml` excludes the build tool, this README, and manuscript source files from the public site.

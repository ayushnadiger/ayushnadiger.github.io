# Ayush Nadiger

Personal academic website: https://ayushnadiger.github.io/

The published site contains the homepage and six project pages, with the original Latin Modern typography and paper-like layout. Active projects are marked Ongoing; the other project pages contain full HTML manuscripts. There are no PDFs or legacy redirect pages.

`tools/build_projects.py` rebuilds the homepage and six project pages using Python, lxml, and Pandoc. Retained TeX sources and browser-native figures live under `assets/papers/`.

Only the pages, styles, figures, favicon, search metadata, and ownership-verification file are published. `_config.yml` excludes the build tool, this README, and manuscript source files from the public site.

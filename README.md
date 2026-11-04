# Ayush Nadiger

Personal academic website: https://ayushnadiger.github.io/

The site has a homepage and six project pages. Four project pages contain full manuscripts rendered in HTML. The two ongoing projects have shorter research overviews with figures and references.

`tools/build_projects.py` builds the homepage and project pages with Python, lxml, and Pandoc. The TeX sources and figures for the manuscripts are in `assets/papers/`, and the bodies of the ongoing-project pages are in `tools/project_content/`.

`tools/build_research_figures.py` regenerates the four figures on the ongoing-project pages from the data in `tools/research_data/`, using matplotlib and numpy. Two of the figures are schematics. The other two show the hybrid-repeater routing calculation and the BB72 scheduling simulation (32 herald histories, full local measurement record and early-noise ablation).

`_config.yml` keeps the build tools, this README, and the TeX sources off the published site.

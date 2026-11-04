# Ayush Nadiger

Personal academic website: https://ayushnadiger.github.io/

Static HTML and CSS, preserving the original Latin Modern typography and paper-like layout.

- `index.html`: affiliation and six projects in the requested order.
- `projects/`: project overviews followed by the full HTML manuscripts; active work is marked Ongoing.
- `assets/papers/`: retained TeX sources and browser-native figures.
- `css/paper.css`: responsive manuscript typography and contents navigation.
- `tools/build_projects.py`: rebuilds the homepage and project pages. Requires Python, lxml, and Pandoc.

Run `python tools/build_projects.py` after changing project metadata or manuscript text. GitHub Pages serves the generated HTML directly. Readers include linked references, numbered equations, original figures, and MathJax mathematics. The site contains no PDFs.

Old Research, Projects, Papers, and CV URLs redirect to Projects. Existing note and other project URLs remain available. The site header contains only the name/home link.

# Ayush Nadiger: quantum error correction and quantum architectures

I study quantum error correction and fault-tolerant architectures under physical hardware and network constraints at the University of Massachusetts Amherst. My current work investigates how codes and schedules should accommodate probabilistic entanglement and finite memory coherence. I am an M.S. student in ECE and a graduate research assistant with Filip Rozpędek, work on hybrid repeaters with Filip and Stav Haldar, and am a member of Don Towsley's ACQuIRE lab.

[Research site](https://ayushnadiger.github.io/) · [GitHub](https://github.com/ayushnadiger) · [Google Scholar](https://scholar.google.com/citations?user=pOxwKVIAAAAJ&hl=en) · [arXiv](https://arxiv.org/search/?searchtype=author&query=Nadiger%2C+A)

## Selected public work

- [Geometry-controlled correlated electric-field noise in enclosed ion traps from billiard return spectra](https://arxiv.org/abs/2608.24770), arXiv:2608.24770
- [Potential Energy Savings from Quantum Computing-Based Route Optimization](https://arxiv.org/abs/2604.16718), arXiv:2604.16718
- [Randomized-Accelerated FEAST: A Hybrid Approach for Large-Scale Eigenvalue Problems](https://arxiv.org/abs/2512.01257), arXiv:2512.01257

## About this repository

This repository hosts my static research site. I designed it to read like a short scientific paper, not a portfolio template.

### Pages
- `index.html`: affiliation paragraph and one-line research hooks
- `research.html`: questions, results, project status, and public preprints
- `papers.html`: compatibility redirect to the Research bibliography
- `notes.html`: expository and exploratory notes
- `assets/Ayush_Nadiger_CV.pdf`: downloadable academic CV
- `cv.html`: compatibility redirect to the PDF
- `tools/build_cv.py`: editable source for rebuilding the PDF
- `projects/asynchronous-qec.html`: current asynchronous-QEC research direction

Old `papers.html`, `cv.html`, `projects.html`, `writing.html`, and `contact.html` routes are retained as `noindex` redirects. Navigation is Research · CV (PDF) · Email.

Rebuild the CV with `python tools/build_cv.py`.

### Search and machine-readable metadata
- `robots.txt` explicitly allows ordinary search crawlers plus OAI-SearchBot.
- `sitemap.xml` lists canonical public pages.
- The homepage contains `Person` JSON-LD and explicit identity links.
- Each public project has its own title, description, canonical URL, and plain-text explanation.

Canonical URLs use `https://ayushnadiger.github.io/`. If a custom domain is added later, update the canonical host, sitemap, and identity links together.

# Ayush Nadiger — research site

Static research site designed to read like a short scientific paper rather than a portfolio template.

## Pages
- `index.html` — front matter / selected work
- `research.html` — current research program and archive
- `papers.html` — public bibliography
- `notes.html` — expository and exploratory notes
- `cv.html` — compact web CV

Old `projects.html`, `writing.html`, and `contact.html` routes are retained as `noindex` redirects.

## Search / LLM discoverability
- `robots.txt` explicitly allows ordinary search crawlers plus OAI-SearchBot.
- `sitemap.xml` lists canonical public pages.
- The homepage contains `Person` JSON-LD and explicit identity links.
- Each real project has a focused title, description, canonical URL, and plain-text explanation.

Canonical URLs currently use `https://lostree9.github.io/`. Replace the hostname when a custom domain is connected.

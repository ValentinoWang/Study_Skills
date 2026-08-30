# Study_Skills

A small library of reusable learning skills and interactive case-based lessons.

## Website

This repository is prepared for GitHub Pages using `main/docs` as the publishing source.

Expected site URL after Pages is enabled:

- https://valentinowang.github.io/Study_Skills/

## Structure

```text
Study_Skills/
├── skills/
│   └── case-driven-active-learning/
│       ├── SKILL.md
│       ├── assets/
│       └── templates/
└── docs/
    ├── .nojekyll
    ├── index.html
    └── lessons/
        └── welcome.html
```

## Publishing a new lesson

Put each finished single-file HTML lesson in:

```text
docs/lessons/<lesson-slug>.html
```

Then add a card/link for it in `docs/index.html` and push to `main`.

No server, database, Node.js build, or virtual machine is required for these static lessons.

## One-time GitHub Pages setting

In the repository open:

`Settings → Pages → Build and deployment`

Choose:

- **Source:** Deploy from a branch
- **Branch:** `main`
- **Folder:** `/docs`

After saving, GitHub Pages will publish the site and future changes under `docs/` will update it automatically.

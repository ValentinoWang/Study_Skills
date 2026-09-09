# Study_Skills

A small library of reusable learning skills and publishable learning pages.

## Website

This repository is prepared for GitHub Pages using `main/docs` as the publishing source.

Expected site URL:

- https://valentinowang.github.io/Study_Skills/

## Available skills

### `math-cs-concept-tutor`

Teach computer-science and software-engineering concepts to learners with a mathematics background.

Core responsibilities:

- separate **abstraction hierarchy** from **learning prerequisites**;
- explain concepts from intuition → mechanism → mathematical model;
- enforce structured expression and default word budgets;
- map concepts into real engineering scenarios;
- select Mermaid / Graphviz / D2 / LaTeX / tables / charts / explanatory images according to information type;
- end with one reasoning-based scenario question and reference answer.

Path:

```text
skills/math-cs-concept-tutor/SKILL.md
```

### `learning-page-design-publisher`

Turn finished or mostly-finished learning content into polished, structured, responsive, printable, publishable static learning pages.

Core responsibilities:

- content decomposition and information hierarchy;
- visual design and typography;
- HTML layout and interaction;
- offline-first diagram/formula rendering;
- desktop / mobile / print QA;
- canonical artifact consistency;
- archive + `docs/lessons` publishing;
- homepage registration;
- GitHub Pages verification.

Path:

```text
skills/learning-page-design-publisher/SKILL.md
```

## How the two skills work together

```text
Need to understand a concept
    → math-cs-concept-tutor

Content is ready; need a beautiful web page
    → learning-page-design-publisher

Need both
    → math-cs-concept-tutor
    → learning-page-design-publisher
```

In short:

> `math-cs-concept-tutor` decides **what to explain and how to make it understandable**; `learning-page-design-publisher` decides **how to turn that content into a well-designed, stable, publishable page**.

## Structure

```text
Study_Skills/
├── skills/
│   ├── math-cs-concept-tutor/
│   │   └── SKILL.md
│   └── learning-page-design-publisher/
│       ├── SKILL.md
│       ├── assets/
│       │   └── lesson-template.html
│       ├── lessons/
│       ├── examples/
│       └── templates/
├── tools/
│   ├── build-lessons.py
│   ├── check-lesson-consistency.py
│   └── check-term-depth.py
└── docs/
    ├── .nojekyll
    ├── index.html
    └── lessons/
```

## Publishing a learning page

The canonical publishing workflow is:

```text
content / lesson data
→ canonical template
→ render QA
→ skills/learning-page-design-publisher/examples/<slug>.html
→ docs/lessons/<slug>.html
→ docs/index.html
→ main
→ GitHub Pages
```

Build and verify:

```bash
python3 tools/build-lessons.py
python3 tools/build-lessons.py --check
python3 tools/check-lesson-consistency.py
```

For active-learning pages that contain structured terminology cards, also run:

```bash
python3 tools/check-term-depth.py
```

No server, database, Node.js build, or virtual machine is required for the current static-page workflow.

## One-time GitHub Pages setting

In the repository open:

`Settings → Pages → Build and deployment`

Choose:

- **Source:** Deploy from a branch
- **Branch:** `main`
- **Folder:** `/docs`

After saving, GitHub Pages will publish the site and future changes under `docs/` will update it automatically.

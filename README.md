# Study_Skills

A small library of reusable learning skills and publishable learning pages.

## Website

GitHub Pages publishes `main/docs`:

- https://valentinowang.github.io/Study_Skills/

## Skills

### `math-cs-concept-tutor`

For mathematics-background learners studying computer science and software engineering.

Key rules:

- separate abstraction hierarchy from learning prerequisites;
- **define unfamiliar terminology before it is used for reasoning**;
- explain intuition → mechanism → mathematical model → real engineering case;
- use the representation that matches the information structure rather than maximizing diagrams;
- keep formulas native/copyable instead of turning them into images;
- finish with a reasoning-based scenario question and reference answer.

Path: `skills/math-cs-concept-tutor/SKILL.md`

### `learning-page-design-publisher`

Turns finished learning content into structured, polished, responsive, printable GitHub Pages lessons.

Key rules:

- terminology-first reading order;
- collapsed term cards still expose a one-line definition;
- visual hierarchy comes from typography, spacing, tables, callouts and layout—not image count;
- formulas, code and commands stay native/copyable;
- desktop / mobile / print QA;
- GitHub Pages build + final artifact readback.

Path: `skills/learning-page-design-publisher/SKILL.md`

## How they work together

```text
Need to understand a concept
    → math-cs-concept-tutor

Content is ready; need a learning page
    → learning-page-design-publisher

Need both
    → math-cs-concept-tutor
    → learning-page-design-publisher
```

## Current publishing architecture

Canonical content and publishing are deliberately separated:

```text
skills/learning-page-design-publisher/lessons/<slug>.json
                    +
skills/learning-page-design-publisher/term-overrides.yml
                    ↓
               canonical data
                    ↓ mirror
      docs/_data/lessons/<slug>.json
      docs/_data/term_overrides.yml
                    ↓
          docs/_layouts/lesson.html
                    ↓
          docs/lessons/<slug>.html
          (small Jekyll entry file)
                    ↓
             GitHub Pages
                    ↓
         rendered static HTML
```

The shared layout enforces:

```text
Hero
→ terminology primer
→ main explanation
→ concept map
→ case
→ mapping
→ exercise
→ hints / answer
```

This prevents lessons from using terms such as `Runtime`, `HMR`, `E2E`, `readback`, `HEAD`, `CORS`, etc. before the learner has been given a minimal definition.

## Repository structure

```text
Study_Skills/
├── skills/
│   ├── math-cs-concept-tutor/
│   │   └── SKILL.md
│   └── learning-page-design-publisher/
│       ├── SKILL.md
│       ├── term-overrides.yml
│       ├── assets/
│       ├── lessons/
│       ├── examples/
│       └── templates/
├── tools/
│   ├── backwash-term-gates.py
│   ├── build-lessons.py
│   ├── check-lesson-consistency.py
│   ├── check-term-depth.py
│   └── check-term-gate.py
└── docs/
    ├── _data/
    │   ├── lessons/
    │   └── term_overrides.yml
    ├── _layouts/
    │   └── lesson.html
    ├── index.html
    └── lessons/
```

`docs/.nojekyll` must **not** exist because GitHub Pages/Jekyll is now the shared lesson renderer.

## Backwash / build / verification

Synchronize all current lessons after a terminology or layout change:

```bash
python3 tools/backwash-term-gates.py
```

Read-only checks:

```bash
python3 tools/backwash-term-gates.py --check
python3 tools/build-lessons.py --check
python3 tools/check-lesson-consistency.py
python3 tools/check-term-depth.py
python3 tools/check-term-gate.py
```

To validate a real GitHub Pages `_site` or downloaded Pages artifact:

```bash
python3 tools/check-term-gate.py --built-site /path/to/_site
```

The artifact check verifies that the final rendered HTML—not merely the repository source—places the terminology section before the main explanation and contains the required core terms.

## GitHub Pages setting

Repository setting:

`Settings → Pages → Build and deployment`

- **Source:** Deploy from a branch
- **Branch:** `main`
- **Folder:** `/docs`

GitHub Pages then runs Jekyll and publishes the generated static site.

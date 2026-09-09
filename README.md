# Study_Skills

A small library of reusable learning skills and interactive case-based lessons.

## Website

This repository is prepared for GitHub Pages using `main/docs` as the publishing source.

Expected site URL after Pages is enabled:

- https://valentinowang.github.io/Study_Skills/

## Available skills

### `case-driven-active-learning`

Turn real materials, incidents, engineering cases, policies, or repository changes into an active-learning lesson with minimal prerequisite knowledge, case reconstruction, learner attempt, Hint 1/2/3, final answer, reflection, transfer, interactive HTML, QA, archive, and GitHub Pages publishing.

Path:

```text
skills/case-driven-active-learning/SKILL.md
```

### `math-cs-concept-tutor`

Teach computer-science and software-engineering concepts to learners with a mathematics background. It separates abstraction hierarchy from prerequisite dependency, uses first-principles explanations and mathematical models, maps concepts into real engineering scenarios, and selects Mermaid / Graphviz / D2 / LaTeX / tables / charts / explanatory images according to the information structure.

Path:

```text
skills/math-cs-concept-tutor/SKILL.md
```

The two skills are complementary:

```text
concept / mechanism understanding
    → math-cs-concept-tutor

real material → complete interactive case lesson
    → case-driven-active-learning

need both
    → math-cs-concept-tutor
    → case-driven-active-learning
```

## Structure

```text
Study_Skills/
├── skills/
│   ├── case-driven-active-learning/
│   │   ├── SKILL.md
│   │   ├── assets/
│   │   ├── examples/
│   │   ├── lessons/
│   │   └── templates/
│   └── math-cs-concept-tutor/
│       └── SKILL.md
├── tools/
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

# Structured microcourse publishing contract (v1)

This is a content/rendering extension, not a change to either SKILL's teaching policy. Use `lesson-microcourse` for a complete collection of single-judgment units; it does not turn repository work into a live quiz.

## Identity

The sole course source remains `lessons/<slug>.json`. `tools/build-lessons.py` mirrors the same bytes into `docs/_data/lessons`, creates the standard lesson wrapper, and reads `lesson-manifest.json`. Declare `layout: lesson-microcourse` and `term_source: lesson`. Courses with no rendered equations need not declare a mathematical rendering mode. If a course contains displayed mathematics, declare the publisher's applicable math contract (such as `portable_html`) and satisfy its equation and layout gates. Do not add decorative equations to satisfy an inapplicable mode.

Do not maintain a second manuscript inside JavaScript or an isolated standalone page.

## Data

Existing metadata (`TITLE`, `SUBTITLE`, `META_DESCRIPTION`, `DOMAIN`, `MODE`, `DURATION`, `DIFFICULTY`, `DATE`) and `TERMS_HTML` retain their meanings. The new `MICROCOURSE_VERSION: 1` enables these documented fields:

- `INTRO`: audience, assumptions, privacy and evidence boundary.
- `MODULES`: `id`, `title`, `units`, `goal`; classification/navigation only.
- `UNITS`: each has `id`, `module`, `title`, `goal`, prior-unit `prerequisites`, `objects` (`name`, `meaning`, `location`, `example`), `baseline`, ordered `trace`, `conclusion`, one `change`, explicit `kept`, `question`, `hint`, `answer`, one `confusion`, minimal `repair`, `verify`, and `sources` IDs.
- `SYNTHESIS_HTML`: a reviewed comparison/synthesis after the units. A table or prose trace is not registered as a formal figure. Future formal figures must use the existing learning-figure model and gates.
- `CORRECTIONS`: reviewed model corrections, not a learner weakness record.
- `GLOSSARY`: `category`, `unit`, `text`; a lookup index, not prerequisites to read all at once.
- `LABS`: `title`, `before`, `code`, `after`; explicitly authorized, bounded experiments.
- `SOURCES`: `id`, `title`, `url`, `scope`; source claims are separated from teaching assumptions. Sample numbers must be labeled teaching settings, never fabricated measurements.

Plain text is escaped in the layout. Only the already-reviewed `TERMS_HTML` and `SYNTHESIS_HTML` are rendered as HTML. Actual commands use `<pre><code>`; mathematical expressions must follow the publisher's math contract.

## Interaction

The first unit is open by default; JavaScript enhances native details to show one unit at a time. Each prediction precedes separate closed hint and answer controls. Users may request the answer directly. Notes save only on explicit Save, to a lesson/version-scoped localStorage key; no network upload, analytics or automatic grading is used. Help exposure is preserved alongside self-assessment and is not represented as independent mastery. Do not persist account identifiers, credentials, precise personal network records or real learning weaknesses in the public repository.

Without JavaScript all content, native details and source links remain readable; enhanced navigation and storage are unavailable. Printing expands student units, hides their inline feedback and emits a separate answer appendix from the same `UNITS`. Print-media validation is distinct from paginated PDF validation.

## Validation

Run `python tools/check-microcourses.py` for source identity, structure, dependency ordering, references, prediction contracts and privacy-safe template requirements. After Jekyll build, run `python tools/check-microcourses.py --built-site PATH --output PATH` for Chromium desktop, 390px, 320px, all unit overflow checks, initially hidden answers, help tracking, explicit note save/restore, glossary filtering, no-JS readability and print-media checks. This validates observable page behavior, not learning outcomes or every factual claim. The semantic review and source attribution remain necessary.

# Learning Figure v2 regression suite

Run `python tools/test-learning-figure-regressions.py` at the repository root.
Requires the pinned Python packages, Chromium, and both Noto CJK font families.

`red/` contains unchanged historical overlapping diagrams; never update them to the repaired versions.
The tests measure their actual browser text, with and without authored safe rectangles.
`green/ownership.figure.json` exercises legitimate parent containment; the three production models exercise sequence and comparison.

Tests reject omitted/unowned/hidden/deleted text, wrong owners, modified facts, collisions,
line/head enlargement, unsupported path/mask/rotation, tiny display scale, invalid models and late placement.
Teaching simulator tests cover A/B symmetry, same effect with different notification ID,
different purchases with equal amounts, rollback-before-commit and lost-response retries.

A passing regression suite is not a production payment certification, human acceptance, full WCAG audit, or public-site proof.
Run static generation identity and built-site browser checks separately; review screenshots and print pagination before sealing.

#!/usr/bin/env python3
"""Validate term-first and variable-first learning gates.

Checks both the global terminology primer and optional long-form section
prerequisites declared in lesson-manifest.json. For long-form lessons, every
declared variable/identifier must appear in the visible primer area before the
first numbered mechanism step. The same rule is rechecked against a built Pages
artifact when --built-site is supplied.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_SKILL = ROOT / "skills/learning-page-design-publisher"
LESSON_DIR = PAGE_SKILL / "lessons"
REGISTRY = PAGE_SKILL / "term-overrides.yml"
MANIFEST = PAGE_SKILL / "lesson-manifest.json"
LAYOUT_DIR = ROOT / "docs/_layouts"
ENTRY_DIR = ROOT / "docs/lessons"

REQUIRED = {
    "frontend-fast-feedback-pipeline-20260910": [
        "Runtime", "Vite Development Server", "Hot Module Replacement", "Hot Reload",
        "Incremental Compilation", "Mock API", "API Proxy", "Target Runtime",
        "Production Build", "Docker Build", "End-to-End Testing", "Deployment Readback",
    ],
    "software-delivery-lifecycle-ai-coding-20260910": [
        "AI Agent", "Software Delivery Lifecycle", "Feedback Loop", "Hot Module Replacement",
        "Smoke Test", "Quality Assurance", "End-to-End Testing", "Release Candidate",
        "Acceptance", "User Acceptance Testing", "Continuous Integration",
        "Continuous Delivery", "Artifact", "Observability", "Rollback",
    ],
    "git-three-state-divergence-20260831": [
        "Commit / SHA", "Blob Object ID", "Branch", "HEAD", "git fetch", "origin/main",
        "git checkout", "Working Tree", "Git worktree", "ahead / behind",
        "Fast-forward Merge", "Merge Conflict",
    ],
    "tencent-cloud-dns-icp-mainland-origin-20260831": [
        "Domain Name System", "DNS Resource Records", "Transmission Control Protocol",
        "Transport Layer Security", "Server Name Indication", "HTTP Host / Reverse Proxy",
        "Application Programming Interface", "Cloud Virtual Machine",
        "Domain Real-name Verification", "Internet Content Provider", "Origin / Same-Origin Policy",
        "Cross-Origin Resource Sharing", "Health Check / Observability",
    ],
    "sub2api-hong-kong-ingress-network-path-20260910": [
        "Network Path", "Ingress / Egress", "Forward Proxy", "Reverse Proxy", "Origin Server",
        "Round-Trip Time", "Time to First Byte", "TLS Termination", "Server-Sent Events",
        "WebSocket", "Proxy Buffering", "WireGuard Tunnel", "System Proxy", "TUN Interface",
    ],
}


def load_manifest() -> dict[str, dict]:
    if not MANIFEST.exists():
        return {}
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("lesson-manifest.json must contain an object")
    return data


def registry_sections(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"(?m)^([a-z0-9][a-z0-9-]+):\n", text))
    out: dict[str, str] = {}
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[match.group(1)] = text[match.start():end]
    return out


def built_site_from_args() -> pathlib.Path | None:
    if "--built-site" not in sys.argv:
        return None
    i = sys.argv.index("--built-site")
    if i + 1 >= len(sys.argv):
        raise SystemExit("--built-site requires a path")
    return pathlib.Path(sys.argv[i + 1]).resolve()


def layout_for(manifest: dict[str, dict], slug: str) -> str:
    return str(manifest.get(slug, {}).get("layout", "lesson"))


def wrapper(manifest: dict[str, dict], slug: str) -> str:
    return f"---\nlayout: {layout_for(manifest, slug)}\nlesson: {slug}\n---\n"


def contains_term(text: str, term: str) -> bool:
    return term.lower() in text.lower()


def primer_prefix(html: str) -> str:
    split = re.search(r"<h3>\s*1[\.、．]", html, re.I)
    return html[: split.start()] if split else html


def extract_section(html: str, section_id: str) -> str:
    m = re.search(
        rf'<section\b[^>]*\bid=["\']{re.escape(section_id)}["\'][^>]*>(.*?)</section>',
        html,
        re.I | re.S,
    )
    return m.group(1) if m else ""


def check_declared_prerequisites(slug: str, cfg: dict, *, built_html: str | None = None) -> list[str]:
    failures: list[str] = []
    src_rel = cfg.get("supplement_source_dir")
    if not src_rel:
        if cfg.get("global_prerequisites") or cfg.get("section_prerequisites"):
            failures.append(f"{slug}: prerequisite contract requires supplement_source_dir")
        return failures
    src_dir = ROOT / str(src_rel)

    global_cfg = cfg.get("global_prerequisites") or {}
    if global_cfg:
        source = src_dir / str(global_cfg.get("file", ""))
        if not source.is_file():
            failures.append(f"{slug}: missing global prerequisite source {source.relative_to(ROOT)}")
        else:
            source_text = source.read_text(encoding="utf-8")
            if "先学会读" not in source_text and "先认" not in source_text:
                failures.append(f"{slug}: global prerequisite source lacks a visible primer heading")
            for term in global_cfg.get("terms", []):
                if not contains_term(source_text, str(term)):
                    failures.append(f"{slug}: global prerequisite missing {term}")
        if built_html is not None:
            sid = str(global_cfg.get("section_id", "symbols"))
            section = extract_section(built_html, sid)
            if not section:
                failures.append(f"{slug}: built page missing prerequisite section #{sid}")
            else:
                for term in global_cfg.get("terms", []):
                    if not contains_term(section, str(term)):
                        failures.append(f"{slug}: built prerequisite section missing {term}")

    section_cfg = cfg.get("section_prerequisites") or {}
    for section_id, spec in section_cfg.items():
        if not isinstance(spec, dict):
            failures.append(f"{slug}/{section_id}: prerequisite spec must be an object")
            continue
        source = src_dir / str(spec.get("file", ""))
        if not source.is_file():
            failures.append(f"{slug}/{section_id}: missing source {source.relative_to(ROOT)}")
            continue
        source_text = source.read_text(encoding="utf-8")
        prefix = primer_prefix(source_text)
        if "本节先认词" not in prefix and "本节先认变量" not in prefix and "本节先认词 / 先认变量" not in prefix:
            failures.append(f"{slug}/{section_id}: missing visible '本节先认词 / 先认变量' primer")
        for term in spec.get("terms", []):
            if not contains_term(prefix, str(term)):
                failures.append(f"{slug}/{section_id}: {term} is used without being declared in the section primer")

        if built_html is not None:
            section = extract_section(built_html, str(section_id))
            if not section:
                failures.append(f"{slug}: built page missing section #{section_id}")
                continue
            built_prefix = primer_prefix(section)
            for term in spec.get("terms", []):
                if not contains_term(built_prefix, str(term)):
                    failures.append(f"{slug}/{section_id}: built primer missing {term}")
    return failures


def main() -> int:
    failures: list[str] = []
    manifest = load_manifest()
    source_slugs = {p.stem for p in LESSON_DIR.glob("*.json")}
    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.is_file() else ""
    sections = registry_sections(text)

    print("global terminology coverage")
    for slug in sorted(source_slugs):
        cfg = manifest.get(slug, {})
        term_source = cfg.get("term_source", "registry")
        lesson = json.loads((LESSON_DIR / f"{slug}.json").read_text(encoding="utf-8"))
        if term_source == "lesson":
            block = str(lesson.get("TERMS_HTML", ""))
        else:
            block = sections.get(slug, "")
        lower = block.lower()
        missing = [t for t in REQUIRED.get(slug, []) if t.lower() not in lower]
        details = block.count("<details>")
        glosses = block.count('class="term-gloss"')
        primer_visible = "先认词" in block or "先认" in block
        ok = bool(block) and primer_visible and not missing and details > 0 and glosses == details
        print(f"  {'OK  ' if ok else 'FAIL'} {slug}: source={term_source}, cards={details}, glosses={glosses}, missing={missing}")
        if not block:
            failures.append(f"{slug}: no terminology primer from declared term_source={term_source}")
        if not primer_visible:
            failures.append(f"{slug}: no visible terminology primer")
        if missing:
            failures.append(f"{slug}: missing required terms: {', '.join(missing)}")
        if details == 0 or glosses != details:
            failures.append(f"{slug}: every collapsed term card must expose one term-gloss")

        entry = ENTRY_DIR / f"{slug}.html"
        if not entry.is_file() or entry.read_text(encoding="utf-8") != wrapper(manifest, slug):
            failures.append(f"{slug}: published entry does not match configured layout wrapper")
        layout = LAYOUT_DIR / f"{layout_for(manifest, slug)}.html"
        if not layout.is_file():
            failures.append(f"{slug}: missing configured layout {layout.relative_to(ROOT)}")

    built = built_site_from_args()
    print("\nlong-form prerequisite contracts")
    for slug, cfg in sorted(manifest.items()):
        built_html = None
        if built is not None:
            page = built / "lessons" / f"{slug}.html"
            if not page.is_file():
                failures.append(f"{slug}: missing rendered page")
            else:
                built_html = page.read_text(encoding="utf-8")
        local = check_declared_prerequisites(slug, cfg, built_html=built_html)
        print(f"  {'OK  ' if not local else 'FAIL'} {slug}: prerequisite problems={len(local)}")
        failures.extend(local)

    if built is not None:
        print("\nrendered global terminology gate")
        for slug in sorted(source_slugs):
            page = built / "lessons" / f"{slug}.html"
            if not page.is_file():
                continue
            html = page.read_text(encoding="utf-8")
            terms = extract_section(html, "terms")
            missing = [t for t in REQUIRED.get(slug, []) if not contains_term(terms, t)]
            details = terms.count("<details>")
            glosses = terms.count('class="term-gloss"')
            ok = bool(terms) and not missing and details > 0 and glosses >= details
            print(f"  {'PASS' if ok else 'FAIL'} {slug}: cards={details}, glosses={glosses}, missing={missing}")
            if not ok:
                failures.append(f"{slug}: rendered global term gate failed; missing={missing}")

    print()
    if failures:
        print(f"TERM / PREREQUISITE GATE FAIL: {len(failures)} problem(s)")
        for f in failures:
            print("  -", f)
        return 1
    print("TERM / PREREQUISITE GATE PASS: terms and declared variables are visible before reasoning use.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)

#!/usr/bin/env python3
"""检查所有 active lesson 是否来自当前 canonical 模板。

canonical = assets/lesson-template.html 的 <style> 与 <script> 两块。
版本号由内容派生（hash），不是手写声明——手写声明防不住"改了忘了改声明"。
"""
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "skills/case-driven-active-learning/assets/lesson-template.html"
LESSON_DIRS = [ROOT / "docs/lessons", ROOT / "skills/case-driven-active-learning/examples"]
# 不是课程、不参与设计系统统一的页面
EXEMPT = {"welcome.html"}


def blocks(path):
    s = path.read_text(encoding="utf-8")
    style = "".join(re.findall(r"<style(?![^>]*data-lesson-extra)[^>]*>(.*?)</style>", s, re.S))
    script = "".join(re.findall(r"<script(?![^>]*src=)[^>]*>(.*?)</script>", s, re.S))
    extra = "".join(re.findall(r"<style[^>]*data-lesson-extra[^>]*>(.*?)</style>", s, re.S))
    return style.strip(), script.strip(), extra.strip()


def fp(*parts):
    return hashlib.sha256("\x00".join(parts).encode("utf-8")).hexdigest()[:8]


def main():
    t_style, t_script, _ = blocks(TEMPLATE)
    canonical = fp(t_style, t_script)
    print(f"canonical template: {TEMPLATE.relative_to(ROOT)}")
    print(f"canonical version : {canonical}  (style {len(t_style)}B + script {len(t_script)}B)\n")

    failures = []
    for d in LESSON_DIRS:
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.html")):
            if f.name in EXEMPT:
                print(f"  SKIP  {f.relative_to(ROOT)}  (exempt: 非课程页)")
                continue
            style, script, extra = blocks(f)
            got = fp(style, script)
            ok = got == canonical
            mark = "OK  " if ok else "DRIFT"
            note = ""
            if not ok:
                bits = []
                if style != t_style:
                    bits.append(f"style {len(style)}B≠{len(t_style)}B")
                if script != t_script:
                    bits.append(f"script {len(script)}B≠{len(t_script)}B")
                note = "  [" + ", ".join(bits) + "]"
                failures.append(f.relative_to(ROOT))
            if extra:
                note += f"  (+{len(extra)}B lesson-extra)"
            print(f"  {mark} {f.relative_to(ROOT)}  {got}{note}")

    print()
    if failures:
        print(f"FAIL: {len(failures)} 个课程页未使用当前 canonical 模板：")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PASS: 所有 active lesson 都来自当前 canonical 模板。")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:  # 允许 | head 截断
        sys.exit(0)

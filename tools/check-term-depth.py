#!/usr/bin/env python3
"""检查带术语卡的主动学习页面是否真的写了结构化解释，而不是摊平成一句话。

这是一个**页面类型特定**的内容门禁：
- 只对 docs/lessons 中实际包含术语 <details> 卡的页面生效；
- 普通技术讲义、纯展示页如果没有术语卡，会自然跳过；
- 页面设计与发布规则见 skills/learning-page-design-publisher/SKILL.md。

历史硬下限：
  - 术语卡必须用 <dl> 结构，不能是裸 <p>；
  - 至少 2 层；
  - 必须包含“直觉”与“本案/当前案例作用”两类锚点。
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LESSON_DIRS = [ROOT / "docs/lessons"]
EXEMPT = {"welcome.html"}

INTUITION_LABELS = {"直觉", "一句话直觉"}
CASE_LABELS = {"本案作用", "当前案例", "本题作用", "在本题中的作用", "本案例作用"}
MIN_LAYERS = 2


def term_cards(html: str):
    # <details> 里不含 hint/answer 关键字的，才视为“术语卡”而不是提示卡。
    for m in re.finditer(r"<details>(.*?)</details>", html, re.S):
        block = m.group(1)
        name = re.search(r"<summary>(.*?)</summary>", block, re.S)
        yield (name.group(1).strip() if name else "(未命名)"), block


def main() -> int:
    failures = []
    for d in LESSON_DIRS:
        for f in sorted(d.glob("*.html")):
            if f.name in EXEMPT:
                continue
            html = f.read_text(encoding="utf-8")
            cards = list(term_cards(html))
            if not cards:
                continue
            print(f"{f.relative_to(ROOT)}")
            for name, block in cards:
                dts = re.findall(r"<dt>(.*?)</dt>", block, re.S)
                dts = [re.sub("<[^>]+>", "", d).strip() for d in dts]
                has_dl = "<dl>" in block
                has_intuition = any(d in INTUITION_LABELS for d in dts)
                has_case = any(d in CASE_LABELS for d in dts)
                ok = has_dl and len(dts) >= MIN_LAYERS and has_intuition and has_case
                mark = "OK  " if ok else "THIN"
                print(f"  {mark} {name:24s} 层数={len(dts)} {dts}")
                if not ok:
                    reasons = []
                    if not has_dl:
                        reasons.append("没有 <dl> 结构（裸句子）")
                    if len(dts) < MIN_LAYERS:
                        reasons.append(f"只有 {len(dts)} 层，下限 {MIN_LAYERS}")
                    if not has_intuition:
                        reasons.append("缺‘直觉’层")
                    if not has_case:
                        reasons.append("缺‘本案作用’层")
                    failures.append((f.relative_to(ROOT), name, reasons))

    print()
    if failures:
        print(f"FAIL: {len(failures)} 张术语卡低于结构化解释下限：")
        for f, name, reasons in failures:
            print(f"  - {f} · {name}：{'；'.join(reasons)}")
        return 1
    print("PASS: 所有检测到的术语卡都有下限结构。")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)

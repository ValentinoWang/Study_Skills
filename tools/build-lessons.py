#!/usr/bin/env python3
"""由 canonical 模板 + 课程数据机械生成课程页。

设计系统（CSS/JS/章节骨架）只有一个来源：assets/lesson-template.html。
课程之间只允许内容不同。模板升级后重跑本脚本即可让所有课程一起迁移，
不存在"改了模板但忘了迁移旧课程"的静默漂移。

用法：
    python3 tools/build-lessons.py           # 生成
    python3 tools/build-lessons.py --check   # 只校验产物是否与应生成内容一致（不写盘）
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills/case-driven-active-learning"
TEMPLATE = SKILL / "assets/lesson-template.html"
DATA_DIR = SKILL / "lessons"
TARGETS = [ROOT / "docs/lessons", SKILL / "examples"]

PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


def render(template: str, data: dict, slug: str) -> str:
    missing = sorted(set(PLACEHOLDER.findall(template)) - set(data))
    if missing:
        raise SystemExit(f"[{slug}] 数据缺少占位符: {', '.join(missing)}")
    out = PLACEHOLDER.sub(lambda m: data[m.group(1)], template)
    left = PLACEHOLDER.findall(out)
    if left:
        raise SystemExit(f"[{slug}] 渲染后仍有未替换占位符: {sorted(set(left))}")
    return out


def main() -> int:
    check_only = "--check" in sys.argv
    template = TEMPLATE.read_text(encoding="utf-8")
    data_files = sorted(DATA_DIR.glob("*.json"))
    if not data_files:
        raise SystemExit(f"没有课程数据：{DATA_DIR}")

    stale = []
    for df in data_files:
        slug = df.stem
        data = json.loads(df.read_text(encoding="utf-8"))
        html = render(template, data, slug)
        for target_dir in TARGETS:
            target_dir.mkdir(parents=True, exist_ok=True)
            out = target_dir / f"{slug}.html"
            current = out.read_text(encoding="utf-8") if out.exists() else None
            if current == html:
                status = "same"
            elif check_only:
                status = "STALE"
                stale.append(out.relative_to(ROOT))
            else:
                out.write_text(html, encoding="utf-8")
                status = "written"
            print(f"  {status:8s} {out.relative_to(ROOT)}  ({len(html)}B)")

    if stale:
        print(f"\nFAIL: {len(stale)} 个产物与「模板 + 数据」不一致，请重新运行本脚本生成。")
        return 1
    print("\nOK" if check_only else "\n生成完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())

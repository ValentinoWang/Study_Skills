#!/usr/bin/env python3
"""Backwash existing lesson sources after introducing the terminology-first gate.

The canonical lesson source is lessons/*.json. This migration is intentionally
idempotent: it can run on every build and only adds/rephrases definitions when
an old lesson still has the known gap.
"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
LESSON_DIR = ROOT / "skills/learning-page-design-publisher/lessons"


def card(summary: str, intuition: str, strict: str, current: str, boundary: str | None = None) -> str:
    parts = [
        f"<details><summary>{summary}</summary><div class=\"body\"><dl>",
        f"<dt>直觉</dt><dd>{intuition}</dd>",
        f"<dt>严格一点</dt><dd>{strict}</dd>",
        f"<dt>当前案例</dt><dd>{current}</dd>",
    ]
    if boundary:
        parts.append(f"<dt>边界</dt><dd>{boundary}</dd>")
    parts.append("</dl></div></details>")
    return "".join(parts)


def summaries(html: str) -> list[str]:
    return re.findall(r"<summary>(.*?)</summary>", html, re.S)


def has_summary(html: str, needle: str) -> bool:
    n = needle.lower()
    return any(n in re.sub(r"<[^>]+>", "", s).lower() for s in summaries(html))


def insert_grid_start(html: str, payload: str) -> str:
    marker = '<div class="grid">'
    i = html.find(marker)
    if i < 0:
        return payload + html
    i += len(marker)
    return html[:i] + "\n" + payload + "\n" + html[i:]


def insert_grid_end(html: str, payload: str) -> str:
    if '<div class="grid">' not in html:
        return html + payload
    i = html.rfind("</div>")
    return html[:i] + "\n" + payload + "\n" + html[i:]


def replace_detail(html: str, summary_text: str, replacement: str) -> str:
    pattern = re.compile(
        r"<details><summary>" + re.escape(summary_text) + r"</summary><div class=\"body\">.*?</div></details>",
        re.S,
    )
    return pattern.sub(replacement, html, count=1)


def ensure_intro(html: str) -> str:
    if "先认词" in html[:300]:
        return html
    return (
        "<p><strong>先认词：</strong>下面这些词会直接参与后面的判断。先看标题下的一句话直觉，"
        "需要严格定义和边界时再展开；不要先背缩写。</p>" + html
    )


def migrate_frontend(data: dict) -> None:
    html = data["TERMS_HTML"]

    if "HMR / Hot Reload · 热更新" in html:
        replacement = "".join([
            card(
                "Runtime · 运行时",
                "程序已经启动之后，真正执行代码、保存状态并调用平台能力的环境。",
                "Runtime 不是源码，也不是发布包本身；它是代码实际运行时所处的执行环境，例如浏览器、Flutter Debug Runtime、微信小程序运行环境。",
                "开发态复用已经运行的 Runtime，才能避免每改一点都从头启动整套应用。",
                "开发 Runtime 通过不等于目标平台 Runtime 或生产环境已经通过。",
            ),
            card(
                "Hot Module Replacement (HMR) · 热模块替换",
                "应用不整体重启，只把发生变化的前端模块替换进去。",
                "HMR 由开发服务器追踪模块依赖，向正在运行的页面发送更新；能否保留状态取决于框架和模块边界。",
                "Vite 驱动的 Web / H5 前端可用 HMR 获得秒级样式和逻辑反馈。",
                "HMR 是开发反馈机制，不是生产构建，也不能证明真实后端和目标平台行为。",
            ),
            card(
                "Hot Reload · 热重载",
                "把变化后的代码注入正在运行的调试应用，并尽量保留当前页面和状态。",
                "Flutter Hot Reload 会把更新后的 Dart 代码送入调试 Runtime，再重建受影响的 Widget Tree；它与 Web 领域的 HMR 目标相似，但实现机制不同。",
                "Flutter 日常 UI 和大部分 Dart 逻辑调整优先 Hot Reload，不必每次重新 release build。",
                "涉及原生插件初始化、入口代码或某些状态变化时，可能需要 Hot Restart 或完整重启。",
            ),
        ])
        html = replace_detail(html, "HMR / Hot Reload · 热更新", replacement)

    end_cards: list[str] = []
    if not has_summary(html, "End-to-End"):
        end_cards.append(card(
            "End-to-End Testing (E2E) · 端到端测试",
            "从真实入口开始，一路跨过前端、接口、鉴权、后端和数据等多个组件，验证完整用户链路。",
            "E2E 测试关注跨组件协作是否正确，通常比单元测试和定向页面检查更慢、更依赖环境。",
            "日常小改只跑受影响链路；合并候选或发布前再执行必要的全量 E2E。",
            "E2E 覆盖广但成本高，不能替代更快、更精确的低层测试。",
        ))
    if not has_summary(html, "Readback"):
        end_cards.append(card(
            "Deployment Readback · 部署读回（readback）",
            "发布完成后，从真正的线上环境重新读一次版本、页面、接口或健康状态，确认用户实际拿到的是刚发布的东西。",
            "Readback 是发布后的独立验证：不相信“部署命令返回成功”就结束，而是从部署目标反向读取可观察证据。",
            "例如读取线上 commit/version、请求真实 URL、检查 /health 或关键页面，证明验收过的候选确实已经在线。",
            "readback 证明‘线上是什么’，不等于已经覆盖所有长期运行风险；后续仍需要监控和告警。",
        ))
    if end_cards:
        html = insert_grid_end(html, "".join(end_cards))

    data["TERMS_HTML"] = ensure_intro(html)
    data["TERMS_CHECKLIST_LABEL"] = (
        "我能先用自己的话解释 Runtime、HMR、Hot Reload、增量编译、Mock、Proxy、"
        "Target Runtime、Production Build、E2E、Docker Build 和部署读回分别解决什么问题。"
    )
    data["ORIENTATION_HTML"] = data["ORIENTATION_HTML"].replace(
        "Production Build、Docker、全量 E2E 和线上 readback",
        "Production Build、Docker、全量端到端测试（E2E）和线上部署读回（readback）",
    ).replace(
        "容器和部署读回",
        "容器和部署后的线上读回（readback）",
    )


def migrate_delivery(data: dict) -> None:
    html = data["TERMS_HTML"]
    prefix: list[str] = []
    if not has_summary(html, "AI Agent"):
        prefix.append(card(
            "AI Agent · 人工智能代理",
            "不是只回答一句话的聊天模型，而是能围绕目标连续调用工具、读写文件、执行测试并产出证据的自动执行者。",
            "在软件交付里，Agent 可以实现代码、运行确定性检查、整理失败证据，但它的自述不能替代独立门禁。",
            "本课讨论‘AI 做绝大多数检查’时，指的是可受约束、可审计的 Agent 工作流。",
            "Agent 可以自动执行检查，但高风险验收授权仍应绑定明确的人或治理主体。",
        ))
    if not has_summary(html, "Hot Module Replacement"):
        prefix.append(card(
            "Hot Module Replacement (HMR) · 热模块替换",
            "开发页面已经运行时，只替换发生变化的模块，快速看到结果。",
            "HMR 是快速开发反馈机制，典型由 Vite 等开发服务器提供。",
            "它属于日常 Feedback Loop，帮助缩短修改到观察结果的时间。",
            "HMR 通过不代表 Production Build、完整 QA 或线上发布通过。",
        ))
    if not has_summary(html, "Smoke Test"):
        prefix.append(card(
            "Smoke Test · 冒烟测试",
            "先跑少量最关键检查，确认系统基本活着、主链路没有立刻坏掉。",
            "冒烟测试是快速、窄覆盖的健康检查，通常放在更昂贵测试之前。",
            "API smoke 可以先验证服务可达、鉴权和关键接口，再决定是否进入更重的测试。",
            "冒烟通过只说明最基本链路可用，不等价于完整回归通过。",
        ))
    if prefix:
        html = insert_grid_start(html, "".join(prefix))
    html = html.replace(
        "HMR、定向测试、API smoke、少量 Playwright",
        "HMR、定向测试、API 冒烟测试（smoke test）和少量 Playwright",
    ).replace(
        "AI/CI 应承担绝大多数 QA",
        "AI Agent 与自动化流水线应承担绝大多数 QA",
    )
    data["TERMS_HTML"] = ensure_intro(html)


def migrate_git(data: dict) -> None:
    html = data["TERMS_HTML"]
    prefix: list[str] = []
    if not has_summary(html, "git checkout"):
        prefix.append(card(
            "git checkout · 检出 / 切换",
            "让某个 Git 工作目录真正摊开指定分支或提交对应的文件。",
            "checkout 会改变当前工作目录对应的 HEAD / 文件状态；它和‘知道远端在哪里’是两回事。",
            "106 的 origin/main 已经更新，但实际 checkout 仍在另一条分支，所以线上工作目录没有自动变成最新 main。",
        ))
    if not has_summary(html, "git fetch"):
        prefix.append(card(
            "git fetch · 获取远端信息",
            "去远端看看最新提交在哪里，并更新本地保存的远端跟踪信息，但不替你切换当前代码。",
            "fetch 会下载对象并更新诸如 origin/main 的远程跟踪引用，通常不会改当前 working tree。",
            "106 fetch 后知道 GitHub main 在 84382576，但当前 HEAD 仍可停在 c5e35ae。",
        ))
    if not has_summary(html, "Git worktree"):
        prefix.append(card(
            "Git worktree · 额外工作目录",
            "同一个 Git 仓库同时开多个独立目录，让不同分支并行摊开工作。",
            "git worktree 共享对象数据库，但每个 worktree 有自己的 checkout / HEAD 和工作目录。",
            "案例里的临时 worktree 是独立工作目录，不能和普通 working tree 这个概念混成一个词。",
        ))
    if not has_summary(html, "Fast-forward"):
        prefix.append(card(
            "Fast-forward Merge · 快进合并",
            "如果目标分支没有自己分叉，只要把分支指针向前移动就能完成合并。",
            "当两边都从共同祖先后独立产生提交时，就不再是单纯 fast-forward，可能需要真正 merge 并处理冲突。",
            "本地前端与 main 各自发展很久且试算产生大量冲突，因此不是简单快进。",
        ))
    if prefix:
        html = insert_grid_start(html, "".join(prefix))
    html = html.replace(
        "Commit 是封存的一版代码，SHA 是它的身份证。",
        "Commit 是封存的一版代码；SHA（Secure Hash Algorithm，这里指提交哈希标识）像它的身份证。",
    )
    data["TERMS_HTML"] = ensure_intro(html.replace("点击展开。", "先读摘要，需要时再展开。"))


def migrate_dns(data: dict) -> None:
    html = data["TERMS_HTML"]
    html = html.replace("<summary>DNS 解析</summary>", "<summary>Domain Name System (DNS) · 域名系统 / 解析</summary>")
    html = html.replace("<summary>TLS / HTTPS</summary>", "<summary>Transport Layer Security (TLS) / HTTPS · 传输层安全</summary>")
    html = html.replace("<summary>CORS</summary>", "<summary>Cross-Origin Resource Sharing (CORS) · 跨源资源共享</summary>")
    html = html.replace(
        "A/AAAA/CNAME 等记录提供名称映射",
        "A（IPv4 地址）、AAAA（IPv6 地址）、CNAME（别名）等记录提供名称映射",
    ).replace(
        "SNI 匹配的域名",
        "服务器名称指示（Server Name Indication, SNI）匹配的域名",
    ).replace(
        "浏览器 DevTools",
        "浏览器开发者工具（DevTools）",
    )
    prefix: list[str] = []
    if not has_summary(html, "Application Programming Interface"):
        prefix.append(card(
            "Application Programming Interface (API) · 应用程序接口",
            "前端或其他程序用固定请求方式向后端能力要数据、触发操作。",
            "Web API 通常由 URL、HTTP 方法、参数、鉴权和响应共同构成契约。",
            "本课的 api.xxx.com 是浏览器真正要访问的后端入口，DNS/TLS 通过后还要验证 API 自身。",
        ))
    if not has_summary(html, "Cloud Virtual Machine"):
        prefix.append(card(
            "Cloud Virtual Machine (CVM) · 云服务器",
            "云厂商提供的一台可远程运行 Linux/Windows 和服务进程的虚拟服务器。",
            "腾讯云把其云服务器产品称为 CVM；服务器地域会影响中国大陆备案/接入要求。",
            "案例里的 106 是中国大陆 CVM，因此域名能解析到它不代表平台准入已经满足。",
        ))
    if prefix:
        html = insert_grid_start(html, "".join(prefix))
    data["TERMS_HTML"] = ensure_intro(html)


MIGRATORS = {
    "frontend-fast-feedback-pipeline-20260910": migrate_frontend,
    "software-delivery-lifecycle-ai-coding-20260910": migrate_delivery,
    "git-three-state-divergence-20260831": migrate_git,
    "tencent-cloud-dns-icp-mainland-origin-20260831": migrate_dns,
}


def main() -> int:
    changed = 0
    for path in sorted(LESSON_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        before = json.dumps(data, ensure_ascii=False, sort_keys=True)
        migrator = MIGRATORS.get(data.get("LESSON_ID"))
        if migrator:
            migrator(data)
        data["TERMS_HTML"] = ensure_intro(data.get("TERMS_HTML", ""))
        after = json.dumps(data, ensure_ascii=False, sort_keys=True)
        if after != before:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            changed += 1
            print(f"updated {path.relative_to(ROOT)}")
        else:
            print(f"same    {path.relative_to(ROOT)}")
    print(f"\nterm-gate backwash complete: {changed} source file(s) changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

---
name: learning-figure
description: >
  为 Study_Skills 教程选择并生成机制图、Pages 原生流程图、科学数据图和数学关系图，提升图文层级与可读性，
  适配 GitHub Pages 静态渲染、中文、窄屏、无 JS 与打印。机制图采用 v2 结构化生成与几何验收；
  线性教学结构采用 JSON→Jekyll 语义 HTML；小型折线/散点/柱图采用可追溯构建期导出器。
metadata:
  version: "2.2.0"
---

# Learning Figure

## 1. 职责与入口

Tutor 定义学习问题、术语、业务事实与数据口径；本 Skill 选择视觉表达并生成受控图；Publisher 负责正文位置、Jekyll 构建与发布。
目标是让读者更快看清**关系、顺序、边界和证据**，不是把教程做成论文缩略图，也不是用图片数量衡量美观。

```text
学习问题 → 选择图型/证据 → canonical model
        → 构建期静态产物或语义 HTML
        → 默认可见定义/读图顺序/结论/边界
        → 桌面/窄屏/无 JS/打印 → Publisher → Pages readback
```

先读 [visual-design.md](references/visual-design.md)。涉及 GitHub Pages 时读 [github-pages.md](references/github-pages.md)；
线性流程读 [page-flows.md](references/page-flows.md)；定量图读 [scientific-charts.md](references/scientific-charts.md)。

## 2. 按学习任务选路

| 要回答的问题 | 当前执行路线 | 机械验收边界 |
|---|---|---|
| 谁向谁发送、先后/冲突 | v2 `sequence` | 模型、模拟、实际字体测量、对象/连线几何 |
| 状态前后怎样变化 | v2 `comparison` | 同字段逐行对照、几何与镜像身份 |
| 对象属于哪个边界 | v2 `ownership` | 显式一层归属与几何 |
| 2–7 步线性机制、诊断门、学习/执行流程 | Pages-native `pipeline` | schema、Jekyll data identity、桌面/手机/无 JS/打印 DOM |
| 少量数值的趋势、关系、类别比较 | chart-kit `line/scatter/bar` | 数据合同、构建期 SVG/表格、导出身份；科学语义独立审阅 |
| 分布、热力图、置信区间、复杂数学图 | 专用科学绘图代码 + 审阅 | 不属于现有通用生成器；不得冒充自动 PASS |
| Git DAG、依赖图、非线性拓扑 | 暂不硬套 page-flow | `BLOCKED_UNSUPPORTED`，直到有受控 graph/DAG 图型 |

简单比较优先 HTML table；单一结论优先 callout；公式优先 Publisher 的数学呈现。
复杂结构可以先用 Mermaid/Graphviz/D2 思考，但 GitHub Markdown 能显示不等于 Pages 已完成渲染和验收。

## 3. 所有图共有的教学合同

每张图必须明确：

- `question`：它替读者解决哪个认知问题；
- `reading_order`：应该先看什么、再看什么；
- `takeaway`：读图后能得到的最小结论；
- `boundary`：图不能推出什么；
- 证据类型与来源。

术语、变量、坐标轴、单位、图例和承担推理作用的字段必须在图形推理之前默认可见地解释。
SVG title/desc、alt、tooltip、下载文件不能替代正文定义。

实测数据必须记录来源、样本/重复单位、聚合、变换和不确定性；禁止补造实验数据、隐藏不利点、把缺测填零，或把平滑/插值冒充原始观测。

## 4. v2 机制图：精确连接关系

唯一可编辑源：

```text
skills/learning-figure/figures/<lesson>/<id>.figure.json
```

作者写 actor/message/state change，不手写坐标。SVG、移动文字步骤和页面数据由同一模型生成；不能直接修改派生 SVG、删标签、缩字或放宽门禁。
字段在 `bindings` 中绑定 label、中文含义、例值、来源和默认可见 `definition_id`。

```text
模型/引用验证 → 教学模拟断言 → 实际字体测量 → 确定性换行/节点扩展
→ 连线/箭头 → SVG + 同模型移动步骤 → 构建期 include → 真实页面验收
```

任意 path/filter/mask/clip、旋转、外部资源和脚本不属于 v2 自动几何支持范围。
详见 [v2-contract.md](references/v2-contract.md)、[geometry-and-guards.md](references/geometry-and-guards.md)、[qa-and-release.md](references/qa-and-release.md)。

## 5. Pages 原生流程图：线性教学结构

唯一人工来源：

```text
skills/learning-figure/page-figures/<lesson>/<id>.flow.json
```

适合“一个动作怎样流动”“故障要穿过哪些门”“一条链路的职责从哪里到哪里”。
模型只写 2–7 个语义步骤；Jekyll 构建成 `.lpf-v1` HTML/CSS，不依赖客户端 JavaScript、CDN 或在线生图服务。

在 `lesson-manifest.json` 中登记：

```json
{
  "page_figures": [
    {
      "id": "example-flow",
      "model": "skills/learning-figure/page-figures/example/example-flow.flow.json",
      "slot": "after-map"
    }
  ]
}
```

当前标准 `lesson` layout 支持 `after-orient / after-map / after-case / after-mapping`。
2–5 步桌面线性排列；6–7 步桌面三列，避免文字被压窄；手机纵向；打印纵向。
完整合同见 [page-flows.md](references/page-flows.md)。

本轮实际回洗记录见 [tutorial-backwash-20260915.md](references/tutorial-backwash-20260915.md)：
Agent 运行环、香港 ingress 路径、DNS/ICP 诊断门已接入；已有等价总图的课程不重复绘制。

## 6. 科学数据图：可追溯网页导出

人工维护 `<id>.chart.json`，从 [convergence.chart.json](examples/convergence.chart.json) 起步。
`scripts/render-chart.py` 生成 SVG、同源数据表、轴/图例解释、Jekyll include、独立预览和摘要报告。
数据图通过 `<img>` 隔离，不把 Matplotlib 的 path/clipPath 塞进 v2 几何检查。

```bash
python -m pip install -r tools/learning-figures-requirements.txt
python skills/learning-figure/scripts/render-chart.py \
  skills/learning-figure/examples/convergence.chart.json \
  --out /tmp/learning-chart --web-path /assets/figures/figure-lab
python skills/learning-figure/scripts/test-render-chart.py
```

通用模板当前只支持 `line/scatter/bar`，最多三系列、每系列三十点；缺测和未实现的不确定性区间会受阻，不静默省略。
更复杂图按 [scientific-charts.md](references/scientific-charts.md) 写专用脚本与独立审阅。

## 7. GitHub Pages 交付原则

三个渲染面必须分开理解：GitHub Markdown 预览、Jekyll 构建、最终浏览器。
默认采用**构建期静态优先**：核心定义、图形、数据和结论在禁用 JavaScript 后仍存在。

- v2 SVG：受控 inline SVG，继续走完整对象几何检查；
- page-flow：Jekyll 语义 HTML/CSS；
- scientific chart：构建期 SVG 作为 `<img>`，同时提供 HTML 定义与同源数据表。

项目 Pages 资源使用 `relative_url`，不把 `/Study_Skills` 写死到生成模型里。
完整规则见 [github-pages.md](references/github-pages.md)。

## 8. 必执行命令

从仓库根目录：

```bash
python -m pip install -r tools/learning-figures-requirements.txt
python -m playwright install chromium

# canonical / mirror / manifest / v2 / page-flow 静态合同
python tools/build-lessons.py --check
python tools/check-lesson-consistency.py
python tools/check-learning-figures.py
python tools/test-learning-figure-regressions.py
python skills/learning-figure/scripts/test-render-chart.py

# 真实 Jekyll candidate
jekyll build --source docs --destination /tmp/learning-figure-site --baseurl /Study_Skills
python tools/check-learning-figures-render.py \
  --built-site /tmp/learning-figure-site --output /tmp/v2-evidence
python tools/check-learning-page-flows-render.py \
  --built-site /tmp/learning-figure-site --output /tmp/page-flow-evidence
```

浏览器验收覆盖桌面、390/320、无 JS 与打印媒体。打印媒体通过不等于分页 PDF 通过；本地 candidate 通过也不等于公开 Pages 已读回。

## 9. 回洗已有教程的规则

先扫描“承担核心推理的手写 SVG / diagram / 长段落”，再问：

1. 它是否已经有等价图？有则不重复。
2. 新图是否真的压缩了关系/顺序/边界？只复述正文则删除。
3. 图型是否匹配信息结构？DAG 不得画成线性 pipeline，数据不得画成概念卡片。
4. 能否建立 canonical model 和生成/检查链？不能则先补能力，不直接堆手画资产。
5. 定义是否早于图？图有没有明确结论和边界？

优先迁移“关键推理依赖、目前手写、且没有结构化来源”的图，不以一次性把全部旧图换掉为目标。

## 10. 完成定义

分别记录：模型/数据、派生身份、语义正确性、几何或 DOM、页面集成、视觉审阅、分页打印、公开读回。
状态只用 PASS / FAIL / BLOCKED / NOT_RUN / 有理由的 NOT_APPLICABLE；必要项受阻或未运行不能升格成通过。

`seal-learning-figure-release.py` 不伪造人工签名；validation workflow 验证 candidate，但当前仍独立于原生 branch-based Pages 的部署前置闸门。
图文件在 main 不等于图已经出现在公开课程页，必须以对应 commit 的 Pages build 和 readback 为准。

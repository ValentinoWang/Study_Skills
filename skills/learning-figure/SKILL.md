---
name: learning-figure
description: >
  为 Study_Skills 教程选择并生成机制图、科学数据图和数学关系图，提升图文层级与可读性，
  适配 GitHub Pages 静态渲染、中文、窄屏、无 JS 与打印。机制图采用 v2 结构化生成与几何验收；
  小型折线/散点/柱图提供可追溯的构建期导出器；区分数据、静态、视觉与发布证据。
metadata:
  version: "2.1.0"
---

# Learning Figure

## 1. 职责与入口

Tutor 定义学习问题、术语、业务事实与数据口径；本 Skill 选择视觉表达并生成图；Publisher 负责正文插入、页面构建与发布。
目标是让读者看清关系、变化和证据，而不是把教程做成论文缩略图或图片画册。

```text
学习问题 → 图型与证据选择 → 单一源模型 → 构建期静态产物
        → 定义/读图提示/结论 → 桌面/窄屏/无 JS/打印 → Publisher
```

先读 [visual-design.md](references/visual-design.md)；涉及页面交付时读
[github-pages.md](references/github-pages.md)。不要为了“科研风”安装整套外部 skills 或引入在线生图依赖。

## 2. 按教学任务选路，不把建议当成已实现能力

| 教学任务 | 当前执行路线 | 验收边界 |
|---|---|---|
| 谁向谁发送、先后/冲突 | v2 `sequence` | 结构模型、教学模拟、全对象几何检查 |
| 状态前后怎样变化 | v2 `comparison` | 同字段逐行对照 |
| 对象属于哪个边界 | v2 `ownership` | 显式一层归属 |
| 少量数值的趋势/关系/类别比较 | `scripts/render-chart.py` 的 `line/scatter/bar` | 数据合同、静态导出与字节身份；独立页面和视觉审阅 |
| 分布、热力图、置信区间、复杂数学/算法图 | 按 [scientific-charts.md](references/scientific-charts.md) 设计专用图 | 不在现有自动生成器的已支持范围；不得报告自动 PASS |

简单比较优先 HTML 表格；单一结论优先 callout；公式优先 Publisher 的数学呈现。
复杂流程可先用 Mermaid/Graphviz/D2 明确结构，再在构建期输出图；不能把 Mermaid 代码块在仓库里能显示，当成 Pages 已适配。

## 3. 每张图的教学合同

明确 `question`、`takeaway`、`reading_order`、`boundary` 和证据类型。
术语、坐标轴、单位、图例和承担推理作用的字段要在图形推理之前默认可见地解释。
SVG title/desc、alt、tooltip、下载文件不替代这些定义。数学背景不等于熟悉工程变量。

证据必须区分教学构造与实测；实测记录来源、样本/重复单位、聚合、变换和不确定性。
不得补造实验数据、隐藏不利点、把缺测填零，或把平滑/插值曲线描述成原始观测。

## 4. 机制图：v2 受控模型

唯一可编辑源为 `figures/<lesson>/<id>.figure.json`。作者描述 actor/message/state change，不编写坐标。
SVG、窄屏步骤与页面数据同源；不手改派生图、不删标签、不缩小到不可读、不放宽门禁。
字段在 `bindings` 中绑定中文含义、例值、来源和默认可见的 `definition_id`。

```text
模型/引用验证 → 教学模拟断言 → 实际字体测量 → 换行/节点扩展
→ 独立消息与结果行 → 端点/箭头 → SVG + 同模型步骤 → 构建期插入 → 实际页面验收
```

所有文字有 label ID、role、owner；主动发现全对象并比较预期清单。正常所属包含合法，穿入非所属节点失败。
布局仍不可行时硬失败，不能把新图元全部标成装饰绕过检测。
任意 path/filter/mask/clip、旋转、外部资源和脚本不属于 v2 自动几何支持范围。

详细合同：[v2-contract.md](references/v2-contract.md)、
[geometry-and-guards.md](references/geometry-and-guards.md)、
[qa-and-release.md](references/qa-and-release.md)。`profiles/readable-v2.json` 是机制图阈值唯一来源。

## 5. 科学数据图：可运行的网页导出路线

人工维护 `<id>.chart.json`，格式从 [convergence.chart.json](examples/convergence.chart.json) 起步。
导出器生成 SVG、同源数据表、默认可见轴/图例定义、Jekyll include、独立预览和带摘要的报告。
数据图使用隔离的 `<img>`，不将 Matplotlib 的 path/clipPath 冒充 v2 可检查的 inline 场景。

从仓库根目录运行：

```bash
python -m pip install -r skills/learning-figure/scripts/requirements-chart.txt
python skills/learning-figure/scripts/render-chart.py \
  skills/learning-figure/examples/convergence.chart.json \
  --out /tmp/learning-chart --web-path /assets/figures/figure-lab
python skills/learning-figure/scripts/test-render-chart.py
# 相同命令加 --check，比较源模型、导出器、CSS 与产物身份，不重写文件。
```

`line/scatter/bar` 最多三系列、每系列最多三十点；缺测、不确定性区间等返回受阻，不能静默丢掉。
完整数据/接入合同见 [scientific-charts.md](references/scientific-charts.md)。
这一路线是导出工具，不是自动向课程/manifest 注册和部署的工具。

## 6. 机制图与页面验收命令

从仓库根目录：

```bash
python -m pip install -r tools/learning-figures-requirements.txt
# Linux 安装 fonts-noto-cjk；浏览器可用系统 Chromium 或 Playwright Chromium。
python -m playwright install chromium
python tools/build-learning-figures.py
python tools/build-lessons.py --check
python tools/check-learning-figures.py
python tools/test-learning-figure-regressions.py
python tools/check-learning-figures-render.py --built-site /path/to/site --output /path/to/evidence
```

必须保留三张机制图、两张历史遮字红例和正常包含反例。SVG 是矢量输出，不等于布局正确。
实际字号/间距按 CSS 像素检查；颜色需与文字、线型、点形等冗余编码。

导航被环境禁止时，显式选择离线模式并记录真实范围；离线预览不是 Jekyll 产物或公开站点。
数据图的导出测试不替代上述 v2 回归；v2 检查也不覆盖 `.lf-chart` 的数据与绘图正确性。

## 7. 完成定义

分开记录：模型/数据、静态身份、覆盖/几何、页面集成、视觉审阅、分页打印、公开读回。
状态为 PASS / FAIL / BLOCKED / NOT_RUN / 有理由的 NOT_APPLICABLE；必要项受阻或未运行不得提升为通过。
图必须与正文解释同处阅读路径；文件在 main 不等于它已出现在课程页。

`seal-learning-figure-release.py` 只接受绑定精确摘要的独立审阅记录；不创建人工签名、不自动部署。
当前 validation workflow 与原生 branch-based Pages 并行，不是部署前置闸门。
新增 chart-kit 需要执行本节对应的独立导出/浏览器检查，不能借用机制图工作流的绿色状态。

---
name: learning-figure
description: >
  生成与验收 Study_Skills 教学机制图。v2 用结构化模型、浏览器文字测量、所属关系和全对象覆盖，
  代替自由坐标与手画保护框。支持时序图、状态对照图和对象归属图；区分静态、渲染、视觉与发布证据。
---

# Learning Figure v2

## 1. 职责和唯一来源

Tutor 定义学习问题、符号、业务事实；本 Skill 生成受约束图形；Publisher 决定图文插入与发布。

新图唯一可编辑源为 `figures/<lesson>/<id>.figure.json`。SVG、窄屏步骤和页面数据都由同一个模型生成。
不能为了排版手改派生 SVG、删标签、改变业务值、缩小到不可读或放宽门禁。

详细实现合同见 [v2-contract.md](references/v2-contract.md)，规则与误报边界见
[geometry-and-guards.md](references/geometry-and-guards.md)，验收和部署边界见
[qa-and-release.md](references/qa-and-release.md)。这三份与工具实现共同使用。

## 2. 必须先完成的教学契约

每图明确 `question`、`takeaway`、`reading_order`、`boundary`、`evidence_type`。
每个工程字段在 `bindings` 中绑定中文含义、例值、来源和默认可见的 `definition_id`。
作者描述 actor/message/state change，不编写位置坐标。箭头只能表示模型明确的发送方到接收方。

一个词仅在 SVG 的 title/desc、tooltip 或隐藏内容中出现，不算已教过。
数学背景不等于熟悉工程变量；不要用更多缩写解释缩写。

## 3. 支持范围与失败策略

本轮受控图型是 `sequence`、`comparison`、`ownership`。首轮采用测量后换行、独立事件行与固定泳道，
不承诺任意图的通用自动布局。布局仍不可行时硬失败，不无限重试、不删除事实。

真实数据图须采用独立审阅流程，记录数据、单位、样本、聚合与统计定义；不能把模拟数据冒充实测。
本轮 v2 自动生成器只接受 `teaching-example` / `schematic`，不支持的数据图返回受阻。
任意 path、filter、mask、clip、旋转、外部资源和脚本不在自动几何支持范围内，不能跳过后 PASS。

## 4. 生成步骤

```text
模型和引用验证 → 教学模拟断言 → 实际字体测量 → 换行/节点扩展
→ 独立消息与结果行 → 端点与显式箭头头部 → SVG + 同模型文字步骤
→ 默认可见定义之后构建期插入 → 实际页面验收
```

所有可见文字必须有 label ID、role、owner；检查器主动发现全部文字，并与预期清单比较。
缺标不是豁免，删字和隐藏也不是修复。节点包含自身文字是合法关系；伸进非所属卡片是失败。
辅助泳道也有预期清单，不能把所有新图元标成装饰以逃避检测。

SVG 是矢量输出，不等于布局正确。实际字号与间距按 CSS 像素检查，不能只看 SVG 源单位。
颜色可与文字、线型冗余表达同一含义；禁止同一编码在局部作用域产生歧义。

## 5. 必执行命令

从仓库根目录：

```bash
python -m pip install -r tools/learning-figures-requirements.txt
# Linux：安装 fonts-noto-cjk；浏览器可用系统 chromium 或 Playwright Chromium
python -m playwright install chromium
python tools/build-learning-figures.py
python tools/build-lessons.py --check
python tools/check-learning-figures.py
python tools/test-learning-figure-regressions.py
# 对真实 Jekyll 构建目录，而不是拼接预览：
python tools/check-learning-figures-render.py --built-site /path/to/site --output /path/to/evidence
```

导航被环境禁止时，可以明确使用 `--offline` 渲染原 HTML 与同一产物的 CSS 字节。
报告必须写“离线构建产物检查”，不得冒充公开 URL 或真实网络验收。

## 6. 完成定义

分别记录模型/静态、覆盖与几何、页面集成、视觉审阅、分页打印、公开读回。
状态只使用 PASS / FAIL / BLOCKED / NOT_RUN / 有理由的 NOT_APPLICABLE。
必要项 BLOCKED 或 NOT_RUN 不得升格为通过。截图基线不自动批准。

当前三张图以及历史两张遮字 SVG 必须参与回归。错误样例失败、正确样例通过，还要证明正常包含不误报。
`seal-learning-figure-release.py` 只接受绑定精确报告摘要的独立审阅记录，不创建人工签名、不自动部署。
当前自定义 validation workflow 与原生 branch-based Pages 并行；它不是 Pages 部署前置闸门。
不能删掉失败检查后声称已阻止坏图上线。

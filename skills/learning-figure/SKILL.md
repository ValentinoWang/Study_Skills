---
name: learning-figure
description: >
  为 Study_Skills 学习网页设计、生成和审查教学图。它把 paper-figure-sentinel、
  paper-figure-harness 与 nature-figure 中可复用的“图意先行、矢量源、几何 QA、red/green guard”
  原则改造成教学网页版本；不把论文投稿的 Python/R 后端选择、毫米尺寸和 TIFF 规范机械搬到 HTML。
---

# Learning Figure

## 0. 角色定位

本 Skill 位于：

```text
math-cs-concept-tutor
  决定：哪里需要图、图必须解释什么、图中哪些变量先定义
                    ↓
learning-figure
  决定：图型、视觉层级、矢量源、标签、几何安全区和图形 QA
                    ↓
learning-page-design-publisher
  决定：图放在哪里、怎样响应式、怎样构建、怎样读回最终 HTML
```

它不是“把文字换成好看的图片”。一张教学图只有在**减少认知跳跃**时才值得存在。

---

# 1. Teaching Figure Contract · 教学图契约

画图前先写清楚：

```text
figure_id:
section_id:
learning_question:
takeaway:
reader_prerequisites:
concrete_example:
reading_order:
relation_semantics:
figure_kind:
mobile_strategy:
evidence_type:
```

各字段含义：

- `learning_question`：读者现在具体卡在哪个问题；
- `takeaway`：看完图后应能说出的一个结论；
- `reader_prerequisites`：图中承担推理作用的术语、变量、ID、状态；
- `concrete_example`：图里使用的具体值，如 `version=7 → 8`；
- `reading_order`：从左到右、从上到下，或按编号 ①②③；
- `relation_semantics`：箭头到底表示调用、传数据、时间先后、状态变化还是因果；
- `figure_kind`：流程、时序、状态、边界、比较、数据图等；
- `mobile_strategy`：`stack`、`scroll` 或 `responsive`；
- `evidence_type`：`teaching-example`、`measured-data`、`schematic`。

**图中的专业标签必须晚于正文定义，或在图旁默认可见地定义。**

---

# 2. 图型选择

| 要解释的信息 | 首选图型 |
|---|---|
| 组件/系统边界 | boundary / architecture schematic |
| 谁先做什么 | sequence / timeline |
| 状态如何变化 | state transition |
| 数据从哪里到哪里 | data-flow |
| 两个方案差异 | before/after / comparison |
| 并发、重试、回调 | event timeline / sequence |
| 数值分布、性能变化 | quantitative chart |
| 纯文字层级 | HTML table / callout，不强制画图 |

不要为了“可视化”把表格硬画成图。

---

# 3. 来源规范：借鉴论文图，但不把网页论文化

本 Skill 吸收以下可复用原则：

- `paper-figure-sentinel`：SVG 矢量源、标签与箭头安全区、语义组件、可复现 guard；
- `paper-figure-harness`：稳定失败类型、red/green 关系、错误信息要指导修复；
- `nature-figure`：一图一个核心结论、证据有主次、直接标签优先、真实数据必须可追溯。

但教学网页不继承以下论文专属约束：

- 不要求每张图先选择 Python 或 R；
- 不默认要求 PDF/TIFF、毫米尺寸、期刊字号；
- 不把浏览器 HTML/SVG 当作“论文截图替代品”的问题套到学习页面；
- 不为了 Nature 风格压低网页字号或牺牲移动端可读性。

---

# 4. SVG 默认策略

机制图、流程图、架构图和状态图默认优先 SVG。

原因：

- 文本和线条缩放清晰；
- 坐标、父面板、箭头和安全区可机械检查；
- Git diff / hash 可追踪；
- 可以在 HTML 中以 `<img>`、`<object>` 或 inline SVG 使用。

推荐：

```text
declarative figure contract
→ SVG source
→ static geometry QA
→ public SVG mirror
→ HTML embedding
→ final browser readback
```

SVG 根节点至少包含：

```xml
<svg
  role="img"
  data-figure-id="..."
  viewBox="0 0 ..."
  aria-labelledby="...">
  <title id="...">...</title>
  <desc id="...">...</desc>
</svg>
```

承担术语含义的文字节点使用：

```xml
<text data-term="version">version = 7</text>
```

这样 QA 能把图中文字与课程前置定义关联起来。

---

# 5. 几何安全规则

对 schematic 类 SVG，优先建立可检查的语义几何，而不是靠肉眼坐标修补。

可选标记：

```xml
<rect data-protect="text" ... />
<line data-connector="request" ... />
<g data-semantic="server-panel">...</g>
```

硬规则：

1. connector 不得穿过 `data-protect="text"` 的内部安全区；
2. 箭头不能无标签地同时承担多种关系语义；
3. 文字、指标、节点不得无意越出命名父面板；
4. 原始矩形、弧线若承担语义，应有 `data-semantic` 或属于明确语义分组；
5. 图例/颜色在同一局部作用域内不能一义多码或一码多义；
6. 图在最终 HTML 尺寸下仍必须可读。

边界相接不算“穿过文本”；检查应针对 protected interior，而不是机械禁止所有相交。

---

# 6. 可读性与移动端

教学图是网页内容，不是论文版面。

默认：

- 普通标签在最终显示尺寸下应接近正文可读级别；
- 不用极浅灰作为主要文字；
- 红/绿不应是唯一编码；
- 颜色之外优先再提供文字、线型、位置等编码；
- 图下面保留一句 takeaway 和必要的读图顺序。

`mobile_strategy`：

### stack

适合可拆成上下阶段的图。手机端改成纵向逻辑。

### scroll

适合必须保持二维关系的架构/时序图。只允许**图容器内部**横向滚动，不允许整页横向滚动。

### responsive

适合结构能自然缩放且文字仍可读的简单图。

如果缩放后字太小，即使 `width:100%` 没溢出，也算失败。

---

# 7. 图中术语与正文的顺序

必须满足：

```text
definition_position(term)
<
figure_reasoning_use(term)
```

manifest 中每张图使用 `requires` 声明图所依赖的术语/变量。

SVG 中带 `data-term` 的技术标签：

```text
set(svg.data-term)
⊆
set(manifest.figure.requires)
```

同时：

```text
set(manifest.figure.requires)
⊆
section prerequisite closure
```

图的 alt/desc 不是术语定义的替代品；关键定义必须在正文默认阅读路径可见。

---

# 8. 数据图的额外规则

如果 `evidence_type = measured-data`：

必须交代：

- 数据来源；
- 单位；
- 样本/次数；
- 聚合方式；
- 误差条/区间；
- 是否为真实运行数据。

如果是演示数据，明确标记：

```text
teaching-example
```

禁止用“看起来像实测曲线”的模拟图暗示真实性能结果。

`nature-figure` 的统计、数据溯源和主次层级原则在这里适用；论文投稿尺寸和后端独占规则不自动继承。

---

# 9. Figure Guard Promotion

只有稳定失败类型才值得进入自动门禁。

一个 guard 保留前必须回答：

```text
failure_class:
recurs_beyond_current_figure:
red_case:
green_case:
false_positive_scope:
repair_guidance:
gate_level:
evidence_output:
```

推荐长期守住：

- 图引用了未先定义的术语；
- canonical SVG 与 public SVG 漂移；
- SVG 缺 title/desc/viewBox；
- connector 穿过 protected text safe zone；
- 移动策略未声明；
- 图源改变但页面仍引用旧产物；
- measured-data 图缺少数据来源/单位说明。

不要为“一次把 x=217 改成 x=219”增加永久规则。

---

# 10. 与 Publisher 的机器合同

课程 manifest 的 `figures` 推荐结构：

```json
{
  "figures": [
    {
      "id": "optimistic-lock-race",
      "section_id": "deep2",
      "question": "两个人都读到 v7，为什么第二个保存会冲突？",
      "takeaway": "A 先把服务器推进到 v8 后，B 携带的 expected version=7 已过期。",
      "source": "skills/learning-figure/figures/<lesson>/optimistic-lock-race.svg",
      "public_path": "docs/assets/figures/<lesson>/optimistic-lock-race.svg",
      "requires": ["version"],
      "mobile_strategy": "scroll",
      "evidence_type": "teaching-example"
    }
  ]
}
```

`build-lessons.py` 负责 source → public mirror。

`check-learning-figures.py` 负责：

- manifest 字段；
- source/public identity；
- SVG 基础结构；
- `data-term` 与 prerequisites；
- figure 是否真正出现在目标章节；
- stable geometry guard。

---

# 11. 最终检查

交付前逐项确认：

- [ ] 图回答一个明确的学习问题；
- [ ] takeaway 是一句完整结论；
- [ ] 专业标签已先定义；
- [ ] 箭头语义明确；
- [ ] 图中有具体值，而不是全是抽象框；
- [ ] 图没有替代必要的文字解释；
- [ ] SVG 有 title/desc/viewBox；
- [ ] canonical/public 图一致；
- [ ] connector 不穿过 text safe zone；
- [ ] 手机策略已声明并在最终页面验证；
- [ ] measured-data 与 teaching-example 明确区分；
- [ ] final Pages artifact 中图真的存在、可读。

一句话：

> **教学图不是装饰；它是把一次状态变化、一次调用、一次冲突或一个边界变成“看得见的推理”。**

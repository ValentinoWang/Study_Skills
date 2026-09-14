---
name: learning-page-design-publisher
description: >
  将已完成或基本完成的学习内容、讲义、案例、题目、技术说明和教学图转换成结构清楚、响应式、
  可打印、可交互的学习网页；负责术语/变量/图中标签首现、内容拆块、figure source/public mirror、
  GitHub Pages 构建、浏览器 QA、归档和发布。
---

# Learning Page Design Publisher

## 0. 角色定位

本 Skill 是 Study_Skills 的**页面设计、渲染与发布层**。

```text
math-cs-concept-tutor
  决定：讲什么、前置是什么、术语/变量怎么定义、哪里值得画图
                    ↓
learning-figure
  决定：图型、矢量源、视觉层级、几何安全区和 figure QA
                    ↓
learning-page-design-publisher
  决定：定义和图先在哪里出现、如何生成、怎样响应式、如何 QA、如何发布和读回
```

Publisher 不得为了模板方便、文件缩小或提交省事，把完整讲义换成缩略稿；也不得为了“更好看”把教学图变成与正文脱节的装饰资产。

---

# 1. Canonical 发布架构

默认短课：

```text
skills/learning-page-design-publisher/lessons/<slug>.json
skills/learning-page-design-publisher/term-overrides.yml
                    ↓
      docs/_data/lessons/<slug>.json
      docs/_data/term_overrides.yml
                    ↓
          docs/_layouts/lesson.html
                    ↓
      docs/lessons/<slug>.html
```

长讲义、特殊布局和教学图必须显式登记在：

```text
skills/learning-page-design-publisher/lesson-manifest.json
```

manifest 可以声明：

- `layout`：Jekyll layout；
- `term_source`：术语来自 registry 还是 lesson；
- `supplement_source_dir` / `supplement_pages_dir`：长章节 canonical/mirror；
- `global_prerequisites`：全课变量/符号预备；
- `section_prerequisites`：每章在推理前必须出现的术语、变量和 ID；
- `figures`：教学图契约、源文件、公开路径、依赖术语和移动策略。

**生成器、consistency、term gate、term depth、figure gate 都读取同一 manifest。**

---

# 2. 上游内容交接合同

Publisher 接收内容时至少确认：

```text
目标读者已知什么
每章学习目标
每章前置概念
每章新增术语 / 变量 / 字段 / ID / 状态取值
定义出现位置
完整例子 / trace
教学图合同（若有）
练习与答案
建议学习时长及活动构成（若有时长）
```

若这些内容缺失，Publisher 不能用排版或图片掩盖教学缺口。

---

# 3. 术语、变量与图中标签首现守门

入门课必须满足：

```text
definition_position(x) < first_reasoning_use(x)
```

这里 `x` 包括：

- 缩写与工程概念；
- 变量、函数名和参数；
- `xxx_id` 字段；
- 状态取值；
- SQL 占位符；
- 公式符号；
- 单位和性能指标；
- **教学图中带技术语义的标签**。

长讲义默认阅读顺序：

```text
Hero
→ 全局核心术语
→ 全景 / 知识地图
→ 必要的“怎么读变量 / 伪代码”
→ 每章自己的先认词 / 先认变量
→ 教学图 / 机制 / trace / 反例
→ 小题
→ 综合题 / 提示 / 答案
```

图的 alt、SVG title/desc、tooltip 都不能替代正文中的关键定义。

---

# 4. 多章节课程的统一来源

长课程允许拆成多个源文件，但必须满足：

```text
canonical supplement source
      == byte mirror ==
Pages include source
```

普通运行：

```bash
python3 tools/build-lessons.py
```

不得把 manifest 声明的特殊 layout 重新覆盖成默认 `lesson`。

`build-lessons.py --check` 和 consistency 必须能发现 wrapper、supplement、layout 漂移。

---

# 5. Teaching Figure Publishing Contract · 教学图发布合同

## 5.1 Canonical source

教学图的可编辑源必须位于 Skill/canonical 区，而不是只存在 `docs/`：

```text
skills/learning-figure/figures/<lesson>/<figure>.svg
                    ↓ mirror
docs/assets/figures/<lesson>/<figure>.svg
```

manifest 中的 `figures` 至少声明：

```json
{
  "id": "optimistic-lock-race",
  "section_id": "deep2",
  "question": "两个人都读到 v7，为什么第二次保存会冲突？",
  "takeaway": "A 推进到 v8 后，B 携带的 expected version=7 已过期。",
  "source": "skills/learning-figure/figures/<lesson>/optimistic-lock-race.svg",
  "public_path": "docs/assets/figures/<lesson>/optimistic-lock-race.svg",
  "requires": ["version"],
  "mobile_strategy": "scroll",
  "evidence_type": "teaching-example"
}
```

## 5.2 Source-of-truth

若使用 SVG：

```text
canonical SVG = editable source of truth
public SVG = deterministic mirror
```

若未来使用 Mermaid/D2/Graphviz：

```text
declarative source = editable source of truth
generated SVG = build artifact
```

禁止同时手工修改“源”和“生成结果”，然后把两份都当唯一来源。

## 5.3 HTML embedding

每张复杂图在正文中至少有：

```html
<figure data-figure-id="...">
  <div class="learning-figure-scroll">
    <img ... alt="短描述">
  </div>
  <figcaption>读图顺序 + takeaway</figcaption>
</figure>
```

复杂关系还应提供默认可见或可展开的文字说明，保证不依赖视觉才能理解关键顺序和结论。

## 5.4 响应式

`mobile_strategy` 必须声明：

- `stack`：手机改为纵向阶段；
- `scroll`：二维关系必须保留，只允许图容器内部横向滚动；
- `responsive`：可以直接缩放且文字仍可读。

仅设置 `width:100%` 但导致标签缩到不可读，不算响应式成功。

---

# 6. Figure QA · 图形质量门

复用 `paper-figure-sentinel` / `paper-figure-harness` 的稳定失败类型，但改成学习网页口径。

静态检查至少覆盖：

1. figure manifest 字段完整；
2. canonical/public SVG 字节一致；
3. SVG 有 `viewBox`、`role="img"`、`title`、`desc`；
4. SVG 中 `data-term` 标签都已包含在 figure `requires`；
5. figure `requires` 都属于该章节的 prerequisite closure；
6. 页面正文真的引用这张图；
7. connector 不穿过 `data-protect="text"` 的内部安全区；
8. `mobile_strategy` 合法；
9. measured-data 图有来源/单位合同。

稳定 geometry guard 应有 red/green 关系；不要为一次坐标事故增加永久规则。

默认执行：

```bash
python3 tools/check-learning-figures.py
python3 tools/test-learning-figure-regressions.py
```

---

# 7. 可见教学文本长度与时长

使用 Visible Learning Text Length (VLTL) 衡量用户真正看到的教学自然语言。

图题、figcaption、读图说明和文字替代计入教学文本；SVG 源码和坐标不计入。

不以 HTML/CSS/JS 字节数、图片数量、文件大小或标题数量估算学习时长。

---

# 8. 信息结构决定表达形式

```text
关系 / 过程      → Mermaid / Graphviz / D2 / SVG
比较 / 矩阵      → table
单一结论         → callout
数学关系         → 原生 MathML / LaTeX renderer
代码执行语义     → <pre><code>
解释 / 因果      → 正文 + 步骤
```

教学图不是装饰 KPI。图必须多解释一层关系、顺序、边界或状态变化。

---

# 9. 公式与代码呈现

MathML 根节点不能被普通布局接管。需要横向滚动时滚动外层 wrapper。

代码块出现前必须确认其中承担推理作用的变量、参数、字段和占位符已经解释。代码块不是定义区。

同理：**图也不是定义区。**

---

# 10. 三层证据

## 10.1 Artifact Identity

回答：两份产物是不是同一份字节？

证据：blob OID、SHA、digest、mirror byte equality。

## 10.2 Semantic Correctness

回答：结构、教学合同、图意是否正确？

证据：schema、consistency、term gate、figure gate、业务/内容审阅。

## 10.3 Rendered Correctness

回答：最终浏览器真正显示和执行是否正确？

证据：GitHub Pages artifact + 浏览器 render、DOM、交互、图的最终尺寸和打印 readback。

```text
same bytes
≠ semantic correct
≠ rendered correct
```

---

# 11. 默认 `/full` 闭环

```text
内容审计
→ 上游学习合同检查
→ 术语 / 变量 / figure prerequisite gate
→ 页面拆块与 figure contract
→ canonical lesson + manifest + supplements + figure sources
→ build-lessons 同步
→ consistency / term-depth / term-gate / figure-gate / math-safety
→ GitHub Pages build
→ 桌面 / 手机 / 打印浏览器 QA
→ artifact readback
→ remote main
```

只给 HTML、只看源码、只看到 deployment success，都不算 `/full` 完成。

---

# 12. 构建与门禁

默认执行：

```bash
python3 tools/backwash-term-gates.py --check
python3 tools/build-lessons.py --check
python3 tools/check-lesson-consistency.py
python3 tools/check-term-depth.py
python3 tools/check-term-gate.py
python3 tools/check-learning-figures.py
python3 tools/test-learning-contract-regressions.py
python3 tools/test-learning-figure-regressions.py
python3 tools/check-math-render-safety.py
```

拿到 `_site` / Pages artifact 后继续：

```bash
python3 tools/check-term-gate.py --built-site /path/to/_site
python3 tools/check-math-render-safety.py --built-site /path/to/_site
```

静态检查只能证明可机械验证条件，不能单独证明“读者一定看懂”。

---

# 13. 发布状态必须分层

| 状态 | 证据 |
|---|---|
| 源码已提交 | remote main 包含目标 commit |
| 构建已完成 | 对应 commit Pages build 成功 |
| 部署已完成 | 对应 artifact deploy 成功 |
| 页面内容已核实 | 公开页面 / 构建 artifact 包含预期章节和图 |
| 页面交互已验证 | 浏览器中的折叠、作答、移动端、图形尺寸、打印等检查 |

不能把“图文件在 main”写成“图已经出现在课程页”。

---

# 14. 响应式与浏览器 QA

至少验证：

1. Pages build success；
2. 桌面约 1280px；
3. 手机约 390px；
4. A4 打印；
5. 页面根元素无意外横向滚动；
6. 表格、代码、图、公式只在自己的容器滚动；
7. 长中文标题不溢出；
8. 术语 / 变量 / 图中标签定义早于推理；
9. 图在最终尺寸下文字可读；
10. 图中箭头不穿过关键文字；
11. manifest 声明的所有图都存在于最终页面；
12. Hint Ladder 与 Final Answer 正确；
13. identity、semantic、render 三类证据分开记录。

---

# 15. 存量课程回洗

Skill、manifest、layout、figure contract 或门禁升级后：

```text
扫描 canonical lessons
→ build-lessons --check
→ consistency
→ term / prerequisite depth
→ term / prerequisite gate
→ figure gate
→ math safety
→ Pages build
→ 最终 artifact readback
```

必须保留三个核心回归条件：

1. 未定义变量 / ID 不能被误判为通过；
2. rebuild 不能让长讲义退回默认 layout 或丢 supplement；
3. figure source/public 漂移、图中未声明技术标签、connector 穿字必须能被守门。

---

# 16. 禁止行为

禁止：

1. 先堆黑话后补词典；
2. 公式 / 伪代码 / 技术图先出现，变量定义后出现；
3. 用图片替代必要的机制解释；
4. 只改 public SVG，不改 canonical figure source；
5. 图中新增技术标签却不更新 prerequisites；
6. 生成器忽略 lesson manifest；
7. 用 blob/hash 一致宣称教学正确；
8. 只看到 Pages deployment success 就宣布完成；
9. 为了好看缩小图中文字到不可读；
10. 用模拟数据图暗示真实测量结论。

---

# 17. 成功标准

## 教学成功

- 第一次看到术语、变量、ID 和图中标签就知道它在当前系统里指什么；
- 代码块、公式和图都能翻译回业务含义；
- 图帮助学习者看见一次调用、一次状态变化、一次冲突或一个边界；
- 学习者可以追踪真实状态变化并自己排错。

## 工程成功

- canonical lesson / supplement / figure / manifest / Pages mirror 一致；
- wrapper layout 与 manifest 一致；
- remote main、Pages artifact、公开页面可追溯到同一候选；
- 最终 artifact 通过真实浏览器 readback。

一句话：

> **上游定义“学什么”；learning-figure 把关键关系画成可见推理；Publisher 保证这些图不会在生成、响应式和发布环节失真。**

---
name: learning-page-design-publisher
description: >
  将已完成或基本完成的学习内容、讲义、案例、题目、技术说明和教学图转换成结构清楚、响应式、
  可打印、可交互的学习网页；负责术语/变量首现、数学与代码表达契约、figure source/public mirror、
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
  决定：内容怎样进入页面、数学/代码怎样区分、怎样响应式、怎样 QA、怎样发布和读回
```

Publisher 不能用排版掩盖内容缺口，也不能为了“统一风格”把数学表达式当代码渲染，或把数学符号拆成 flex/grid token。

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

长讲义、特殊布局、教学图和数学模式统一登记：

```text
skills/learning-page-design-publisher/lesson-manifest.json
```

manifest 可声明：

- `layout`：Jekyll layout；
- `term_source`：术语来自 registry 还是 lesson；
- `math_mode`：数学表达合同；当前简单数学课程使用 `portable_html`；
- `supplement_source_dir` / `supplement_pages_dir`：长章节 canonical/mirror；
- `global_prerequisites` / `section_prerequisites`：术语、变量、ID 的首现约束；
- `figures` / `page_figures`：教学图模型、位置和依赖。

生成器、consistency、term gate、figure gate、math gate 必须读取同一 manifest。

---

# 2. 上游内容交接合同

Publisher 接收内容时至少确认：

```text
目标读者已知什么
每章学习目标
每章前置概念
新增术语 / 变量 / 字段 / ID / 状态取值
定义出现位置
完整例子 / trace
数学对象与代码标识符的区分
教学图合同（若有）
练习与答案
建议学习时长
```

入门课必须满足：

```text
definition_position(x) < first_reasoning_use(x)
```

这里 `x` 包括缩写、工程概念、变量、函数参数、`xxx_id`、状态、单位、公式符号和图中技术标签。

---

# 3. 数学、代码、正文是三种不同语言

## 3.1 核心分类

```text
真实代码标识符 / CLI / JSON / regex / path  → <code> / <pre><code>
行内数学对象与关系                        → .math-inline
块级简单公式                              → .math-display + .formula-scroll
复杂二维数学（分式/矩阵/根式/积分等）     → MathML / 受控 LaTeX renderer
普通解释                                  → 正文
```

**数学表达式禁止仅因“技术感”被放进 `<code>`。**

错误：

```html
<code>πθ(a|c,g)</code>
<code>A_exec ⊂ A</code>
```

这会继承 monospace、灰底、padding 和代码换行策略，最终变成“灰色药丸”。

正确：

```html
<span class="math-inline">
  π<sub>θ</sub>(<var>a</var> | <var>c</var>, <var>g</var>)
</span>
```

真正的代码仍使用：

```html
<code>read_file</code>
<code>operation_id</code>
<code>project://rules</code>
```

## 3.2 简单块公式：正常排版流，不做 token 布局

默认结构：

```html
<div class="formula-scroll">
  <div class="math-display" role="math"
       aria-label="A exec 等于 A schema 与 A auth 的交集">
    <var>A</var><sub>exec</sub>
    <span class="rel">=</span>
    <var>A</var><sub>schema</sub>
    ∩
    <var>A</var><sub>auth</sub>
  </div>
</div>
```

硬规则：

- `.math-display` 必须使用浏览器正常 inline formatting context；
- **禁止 `display:flex / inline-flex / grid`；**
- **禁止用 `gap` 给每一个括号、逗号、运算符做 spacing；**
- 只给真正的关系符（如 `=`、`∼`）通过 `.rel` 少量留白；
- 括号、逗号应跟随正常数学排版，不单独变成布局单元；
- `var/sub/sup` 保持语义与可复制文本；
- `.math-display` 必须在 `.formula-scroll` 内；
- 必须有 `role="math"` 和可读的 `aria-label`；
- 不依赖 JS 才能看到公式；
- 不得再显示第二份 plaintext / MathML fallback。

历史失败模式：

```css
.portable-equation {
  display: flex;
  gap: .34em;
}
```

这种实现会把 `(`、`)`、`,`、`=` 等每个 token 当 flex item，强行拉开数学间距。**该 renderer 已废弃，门禁必须拒绝 `.portable-equation`。**

## 3.3 行内数学

行内数学使用：

```html
<span class="math-inline">
  <var>s</var><sub>t+1</sub> = <var>T</var>(<var>s</var><sub>t</sub>, <var>a</var><sub>t</sub>)
</span>
```

要求：

- 无灰底；
- 无 code padding；
- 数学变量可斜体；
- 下标、上标按数学字号缩放；
- 不得把 `.math-inline` 挂在 `<code>` 上。

## 3.4 Math-heavy table

数学表格不能为了适配手机把符号列压到不可读。

使用：

```html
<div class="table math-table">
  <table>...</table>
</div>
```

规则：

- table 保留最小可读宽度；
- `.table` wrapper 负责横向滚动；
- 手机端宁可滚动，也不通过极小字体、单字符换行或窄列破坏公式；
- 打印时再解除最小宽度限制。

---

# 4. 复杂数学结构

只有分式、矩阵、根式、积分、多层上下标等会被简单 HTML 明显损坏的结构，才使用原生 MathML 或受控 LaTeX renderer。

MathML 规则：

- 横向滚动只能放外层 wrapper；
- 不得给 `math` 根节点设置 `display:flex/grid/block` 或 overflow；
- 不得同时显示 MathML 与可见 fallback；
- 必须把 Chromium 与至少一个独立渲染引擎（优先 WebKit/Safari）的真实显示作为独立证据；
- 没有对应环境时记 `BLOCKED / NOT_RUN`，不能拿源码正确代替跨浏览器正确。

---

# 5. Teaching Figure v2 发布合同

图的唯一人工来源是：

```text
skills/learning-figure/figures/<lesson>/<id>.figure.json
```

不是派生 SVG。

manifest 只登记图 id、model、section/slot/after_id；构建器同步模型旁 SVG、`docs/assets/figures`、includes 和数据。任一漂移必须重建。

图的 QA 与数学 QA 分开：

```text
learning-figure.css → 图 / 页面流程图
learning-math.css   → 数学排版
```

不得再让 figure stylesheet 隐式承担数学 renderer 职责；lesson 样式链可以 import 两者，但职责必须独立。

---

# 6. 三层证据

## Artifact Identity

回答“源码和 mirror 是否同一份字节”。

证据：blob SHA、digest、byte equality。

## Semantic Correctness

回答“内容、定义、数学/代码分类、图意是否正确”。

证据：schema、consistency、term gate、figure gate、math gate、内容审阅。

## Rendered Correctness

回答“最终浏览器里到底显示成什么”。

证据：Pages artifact + 浏览器 DOM / screenshot / print readback。

```text
same bytes
≠ semantic correct
≠ rendered correct
```

---

# 7. 默认 `/full` 闭环

```text
内容审计
→ 术语 / 变量 / 数学对象 / figure prerequisite
→ canonical lesson + manifest
→ build-lessons 同步
→ consistency / term / figure / math gates
→ 候选 Jekyll build
→ 桌面 / 390px / 打印 render QA
→ remote main
→ GitHub Pages build / deploy
→ 同一 commit artifact readback
→ 公开页面 readback
```

只看到“源码已提交”或“Pages deployment success”都不能等价成 rendered correctness。

---

# 8. 门禁

默认运行：

```bash
python3 tools/build-lessons.py --check
python3 tools/check-lesson-consistency.py
python3 tools/check-term-depth.py
python3 tools/check-term-gate.py
python3 tools/check-learning-figures.py
python3 tools/check-math-render-safety.py
python3 tools/test-learning-contract-regressions.py
python3 tools/test-learning-figure-regressions.py
```

拿到 `_site` 后再运行：

```bash
python3 tools/check-term-gate.py --built-site /path/to/_site
python3 tools/check-math-render-safety.py --built-site /path/to/_site
python3 tools/check-learning-figures-render.py --built-site /path/to/_site --output /path/to/evidence
```

`check-math-render-safety.py` 对 `math_mode: portable_html` 必须至少阻止：

1. 原生 block MathML 回流；
2. 废弃 `.portable-equation` flex-token renderer；
3. `.math-display` 脱离 `.formula-scroll`；
4. 缺 `role=math` / `aria-label`；
5. `.math-inline/.math-display` 挂在 `<code>`；
6. 明显数学表达式被写成 inline `<code>` 灰色 pill；
7. `.math-display` 使用 flex/grid/gap；
8. 可见双层 fallback；
9. math stylesheet 缺少数学表格可读宽度策略。

必须保留历史 red cases：

```text
公式 token 被 flex gap 拉散
数学对象变成灰色 code pill
手机数学表格被压成单字符窄列
MathML + fallback 重复显示
公式脱离 scroll wrapper
```

---

# 9. 响应式与浏览器 QA

至少验证：

1. 桌面约 1280px；
2. 手机约 390px；
3. A4 print；
4. 页面根元素无意外横向滚动；
5. 长块公式只在 `.formula-scroll` 内滚动；
6. 数学表格只在 `.table` 内滚动；
7. 数学变量、下标、括号、逗号没有异常大间距；
8. 行内数学没有灰色 code 背景；
9. 手机端公式不被拆成散落 token；
10. 手机端数学表格不通过压缩字体/列宽换取“无滚动”；
11. 图中文字可读、connector 不穿字；
12. Hint / Answer 交互可用；
13. identity / semantic / render 证据分开记录。

---

# 10. 禁止行为

禁止：

1. 先堆黑话后补定义；
2. 数学公式、代码、图先出现，变量定义后出现；
3. 用 `<code>` 给数学表达“加样式”；
4. 用 flex/grid + gap 排每一个数学 token；
5. 为了手机无滚动把数学表格压到不可读；
6. 同时显示两份公式 fallback；
7. 只改 public SVG，不改 canonical figure source；
8. 用 blob/hash 一致宣称页面视觉正确；
9. 只看到 Pages deployment success 就宣布完成；
10. 用 JS 搬运/复制公式导致无 JS、打印或辅助技术读到另一套结构。

---

# 11. 成功标准

## 教学成功

- 第一次看到术语、变量和符号就知道含义；
- 数学看起来像数学，代码看起来像代码；
- 表格、公式、图可以翻译回业务语义；
- 学习者能追踪真实状态变化并自己排错。

## 工程成功

- canonical lesson / mirror / supplement / figure / manifest 一致；
- layout 和 manifest 一致；
- math mode 与实际 DOM 一致；
- remote main、Pages artifact、公开页面可追溯到同一候选；
- 最终 artifact 通过真实浏览器 readback。

一句话：

> **Publisher 不只是“把内容放上网页”，而是保证术语、图、数学、代码在生成、响应式和发布后仍保持各自正确的语义与视觉语言。**

## v2 输出边界补充

v2 图中 JSON model 是人工唯一来源，SVG 是派生物。静态 PASS、浏览器 PASS、视觉接受、分页打印、公开读回分别记录，不合并成无范围的“全部完成”。

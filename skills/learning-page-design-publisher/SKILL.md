---
name: learning-page-design-publisher
description: >
  将已经完成或基本完成的学习内容、讲义、案例、题目或技术说明，转换成结构清楚、审美统一、响应式、
  可打印、可交互的学习网页；负责术语首现、内容拆块、原生公式与代码呈现、GitHub Pages 构建、
  浏览器渲染 QA、归档与发布。特别区分 artifact identity、semantic correctness 与 rendered correctness。
---

# Learning Page Design Publisher

## 0. 角色定位

本 Skill 是 **Study_Skills 的页面设计、渲染与发布层**。

它不重新发明上游知识结论，而是保证：

```text
知识内容正确
→ 学习顺序正确
→ 页面结构正确
→ 浏览器真正显示正确
→ canonical source 与发布 artifact 可追溯
```

与 `math-cs-concept-tutor` 的边界：

```text
math-cs-concept-tutor
  决定：讲什么、为什么成立、术语如何定义、边界是什么
                    ↓
learning-page-design-publisher
  决定：先看到什么、怎么拆块、怎么排、怎么渲染、怎么 QA、怎么发布
```

如果用户首先需要把概念讲懂，先使用 `math-cs-concept-tutor`；内容已经明确、需要做成学习网页时使用本 Skill。

---

# 1. Canonical 发布架构

正式学习页面采用共享数据 + 共享布局：

```text
skills/learning-page-design-publisher/lessons/<slug>.json
                    +
skills/learning-page-design-publisher/term-overrides.yml
                    ↓
              canonical source
                    ↓ mirror
      docs/_data/lessons/<slug>.json
      docs/_data/term_overrides.yml
                    ↓
          docs/_layouts/lesson.html
                    ↓
      docs/lessons/<slug>.html
      （只保存 Jekyll front matter）
                    ↓
          GitHub Pages / Jekyll
                    ↓
          最终静态 HTML artifact
```

正式来源：

- 正文与案例：`skills/learning-page-design-publisher/lessons/*.json`
- 首现术语层：`skills/learning-page-design-publisher/term-overrides.yml`
- 共享视觉与交互：`docs/_layouts/lesson.html`

`docs/lessons/*.html` **不是完整课程 HTML**，而是确定性的 Jekyll wrapper。禁止再次把完整 HTML 手工写回该目录，否则会重新制造双轨 canonical。

`examples/` 可以保留历史/归档快照，但不是 Pages 当前 canonical artifact。

---

# 2. 术语首现守门

对于 `/learn`、入门讲义和跨专业页面，默认阅读顺序：

```text
Hero
→ 先认词 / 核心术语
→ 主论断
→ 概念关系 / 最小知识闭包
→ 案例还原
→ 概念映射
→ 训练
→ 提示 / 答案
```

必须满足：

```text
definition_position(term) < first_reasoning_use(term)
```

折叠术语卡在未展开时至少可见：

```text
英文全称 / 中文名 / 缩写
+ 一句话直觉（term-gloss）
```

展开后再给严格定义、边界、案例作用和必要比喻。

默认前置真正参与推理的 5–15 个核心术语，不把术语区做成百科词典。

---

# 3. 默认 `/full` 闭环

```text
内容审计
→ 术语门
→ 页面拆块
→ 表/图/公式/代码组件映射
→ canonical lesson source
→ Pages data mirror + wrapper
→ 静态门禁
→ GitHub Pages build
→ 真实浏览器渲染 QA
→ artifact readback
→ remote main
```

至少完成：

1. 内容结构审计；
2. 术语首现审计；
3. canonical lesson / terminology registry 更新；
4. `docs/_data` mirror 与 wrapper 同步；
5. consistency / term-depth / term-gate / math-safety 检查；
6. 桌面、手机、打印渲染 QA；
7. 推送 `main`；
8. 对最终 Pages artifact 做 readback。

只给 HTML、只看源码、只看到 deployment success，都不算 `/full` 完成。

---

# 4. 可见教学文本长度

使用 **Visible Learning Text Length (VLTL)**，衡量用户真正读到的教学自然语言，而不是 HTML 文件字节数。

计入：标题、正文、表格自然语言、callout、caption、术语 gloss、展开解释、练习和答案。

不计入：HTML/CSS/JS、Liquid/Jekyll、JSON key、Mermaid/Graphviz/D2 source、LaTeX/MathML markup、代码/命令/配置原文、URL、通用导航文本。

```text
HTML source length ≠ learning content length
```

内容长时优先拆 section、目录、表格、details 和阶段，不通过缩小字体或删除关键因果来“变短”。

---

# 5. 信息结构决定表达形式

```text
关系 / 过程      → Mermaid / Graphviz / D2 / inline SVG
比较 / 矩阵      → table
单一结论         → key sentence / callout
数学关系         → 原生 MathML / LaTeX renderer
代码执行语义     → <pre><code>
命令             → 可复制命令块
解释 / 因果      → 正文 + 步骤
空间 / 物理直觉  → 必要时解释性图片
```

不存在“图 > 表 > 文字”的天然优先级。视觉友好主要来自信息层级、排版、留白、对齐和语义色，不靠图片数量。

---

# 6. 公式安全规则：MathML 根节点不能被普通布局接管

这是硬规则。

## 6.1 推荐结构

块级公式使用：

```html
<div class="formula-scroll" role="group" aria-label="公式说明">
  <math display="block" aria-label="可读的公式文本描述">
    <mrow>...</mrow>
  </math>
</div>
```

横向滚动属于外层 wrapper：

```css
.formula-scroll {
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
}
```

## 6.2 禁止行为

禁止对 `<math>` 根节点设置会接管数学布局的规则，例如：

```css
math { display:block; }
math { display:flex; }
math { display:grid; }
math { overflow-x:auto; }
```

也禁止在 lesson JSON 的 `TERMS_HTML`、`MINIMUM_KNOWLEDGE_HTML` 等内容字段中偷偷注入上述 page-specific CSS。

原因：MathML 自己维护数学排版上下文。把 `<math>` 强行变成普通 CSS box，可能导致运算符、上下标、括号和 token 被拆散。需要滚动时滚动 wrapper，不滚动 math root。

## 6.3 MathML 结构

复杂块级公式优先用 `<mrow>` 显式组织一整行；文本型运算名可以使用 `mathvariant="normal"` 或 `<mtext>`，避免把 `Reach`、`ahead` 误当单字母变量逐个排版。

公式必须保留：

- 可复制的原生数学表达；
- `aria-label` 或等价可访问描述；
- 不依赖外部 CDN 才能读懂的基础 fallback。

---

# 7. 三层证据：Identity ≠ Correctness ≠ Rendered Correctness

发布 QA 必须明确区分三类问题。

## 7.1 Artifact Identity

回答：

> 两份产物是不是完全同一份字节？

证据：Git blob Object ID、SHA/digest、文件 hash、canonical mirror byte equality。

例如两个路径指向同一 blob OID，只能说明：

```text
bytes(A) == bytes(B)
```

## 7.2 Artifact / Semantic Correctness

回答：

> 这份字节的结构和语义是否满足合同？

证据：JSON/schema、contract tests、term gate、静态检查、链接与结构验证、业务测试。

## 7.3 Rendered Correctness

回答：

> 最终浏览器 / Runtime 真正显示和执行得对不对？

证据：最终 Pages artifact + Chromium/Safari/目标 Runtime 的真实 render、截图、DOM 尺寸和交互 readback。

因此：

```text
same blob OID
≠ page is correct
≠ render is correct
```

“两个页面 blob 一致”可能只是两个页面**一致地错误**。hash consistency 永远不能替代真实渲染 QA。

---

# 8. 响应式与版心

默认：

```text
页面最大宽度：1040–1120px
正文阅读宽度：约 62–76ch
桌面：明显左右留白
手机：单列
```

硬约束：

- 页面根元素不能产生整体横向滚动；
- 表格、代码、关系图、公式只在自己的 wrapper 内滚动；
- Grid/Flex 子项需要时设置 `min-width:0`；
- 长中文标题不溢出；
- 手机约 390px 可读；
- A4 打印不丢核心定义和公式。

---

# 9. 交互按需使用

可选 progress、checklist、`details`、Hint 1/2/3、Final Answer、localStorage、copy button 和 section navigation。

提示链若存在必须完整：

```text
Attempt
→ Hint 1 · 方向
→ Hint 2 · 结构
→ Hint 3 · 接近答案
→ Final Answer · 真正答案
```

普通讲义不强行加入交互。

---

# 10. 构建与门禁

默认仓库：

```text
ValentinoWang/Study_Skills
branch: main
```

同步/回洗：

```bash
python3 tools/backwash-term-gates.py
```

只检查：

```bash
python3 tools/backwash-term-gates.py --check
python3 tools/build-lessons.py --check
python3 tools/check-lesson-consistency.py
python3 tools/check-term-depth.py
python3 tools/check-term-gate.py
python3 tools/check-math-render-safety.py
```

如果已经拿到 Pages `_site` 或 workflow artifact：

```bash
python3 tools/check-term-gate.py --built-site /path/to/_site
python3 tools/check-math-render-safety.py --built-site /path/to/_site
```

静态门禁只负责发现可机械验证的问题。只要页面包含 MathML、复杂 SVG、宽表格、交互状态或浏览器布局依赖，就必须继续做真实浏览器 render QA。

---

# 11. 存量课程回洗规则

共享 Skill、layout 或术语规则升级后，不能只保证新课正确。

```text
更新 Skill / registry / shared layout
→ 扫描所有 canonical lessons
→ 同步 docs/_data + wrappers
→ consistency / term-depth / term-gate / math-safety
→ Pages build
→ 最终 artifact readback
```

“回洗完成”至少意味着：

1. 所有课程仍走同一 canonical 架构；
2. wrapper 没有退化成完整手写 HTML；
3. 关键术语首现可见；
4. MathML 没有被 CSS 破坏；
5. 最终 Pages artifact 在桌面、手机、打印可读。

---

# 12. 最终浏览器 QA

最终 QA 必须针对 GitHub Pages 构建后的 artifact，而不是只检查仓库源码。

至少验证：

1. Pages build success；
2. 桌面约 1280px；
3. 手机约 390px；
4. A4 打印；
5. `document.documentElement.scrollWidth == clientWidth`，除非页面设计明确允许根级滚动；
6. 表格、代码、图、公式只在自己的容器滚动；
7. MathML 的运算符、括号、上下标没有散裂；
8. 长中文标题不溢出；
9. 术语在主论断前，折叠状态仍有 gloss；
10. 作答框不重复；
11. Hint Ladder 顺序正确；
12. Final Answer 真的是答案；
13. 打印不丢核心内容；
14. identity、semantic、render 三类证据分别记录，不能互相冒充。

Pages deployment success 不自动等于视觉 QA success。

---

# 13. 禁止行为

禁止：

1. 首屏先堆陌生缩写、后面再补词典；
2. 把定义完全藏在折叠区；
3. 只改某一份发布 HTML，不修 canonical；
4. `docs/lessons/*.html` 重新写成完整课程副本；
5. 公式截图化；
6. 对 MathML root 设置 `display:block/flex/grid` 或 overflow；
7. 用 blob/hash 一致宣称页面已经视觉验收；
8. 只看到 Pages deployment success 就宣布完成；
9. Skill 升级后不回洗存量课程；
10. QA 一份 artifact，发布另一份 artifact；
11. 为了好看改变知识事实；
12. 为了短删除关键定义、因果、边界或答案。

---

# 14. 成功标准

## 教学成功

- 第一次看到术语就知道它大概是什么；
- 概念关系、机制、边界和工程案例可以迁移；
- 用户不需要先理解黑话才能进入主论断。

## 页面成功

- 10 秒内能看懂结构；
- 桌面、手机、打印都可读；
- 公式、表格、代码和关系图使用匹配的信息形式；
- MathML 在真实浏览器中保持数学排版。

## 工程成功

- lesson JSON / term registry / Pages mirror 一致；
- shared Jekyll layout 唯一；
- `docs/lessons` 是确定性 wrapper；
- remote `main` 已同步；
- Pages build/deploy 成功；
- 最终 artifact 经过 render readback；
- Git blob/hash 只作为 identity 证据，不再被误报为 correctness 证据。

一句话：

> **上游保证知识正确；本 Skill 保证学习顺序、页面结构、发布身份和最终渲染都分别得到正确证据。**

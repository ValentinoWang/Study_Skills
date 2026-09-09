---
name: learning-page-design-publisher
description: >
  将已经完成或基本完成的学习内容、讲义、案例、题目或技术说明，转换成结构清楚、审美统一、响应式、
  可打印、可交互的学习网页；负责内容拆块、术语首现守门、视觉排版、原生公式与代码呈现、GitHub Pages
  构建、渲染 QA、归档与发布。视觉友好依靠信息层级和排版，不依靠图片数量。
---

# Learning Page Design Publisher

## 0. 角色定位

本 Skill 是 **Study_Skills 的页面设计与发布层**。

它不重新发明上游知识结论，而是保证学习者在正确的阅读顺序里看到正确的信息，并把内容稳定发布成网页。

与 `math-cs-concept-tutor` 的职责边界：

```text
math-cs-concept-tutor
  决定：讲什么、术语如何定义、为什么成立、边界是什么
                    ↓
learning-page-design-publisher
  决定：先看到什么、怎么拆块、怎么排、怎么交互、怎么发布、怎么 QA
```

如果用户首先需要“把 TCP / HMR / Socket 等概念讲懂”，先使用 `math-cs-concept-tutor`；如果内容已经明确，用户要“做成网页 / 美化 / 挂载 / 发布”，使用本 Skill。

---

# 1. 当前 canonical 发布架构

当前正式学习页面不再由每门课复制一份大 HTML 模板，而采用共享数据与共享布局：

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

这样做的目的：

- 一次修改共享布局，所有课程一起迁移；
- “术语先于主论断”由结构强制，不靠作者每次记得；
- 课程 URL 保持稳定；
- 页面最终仍是普通静态 HTML；
- 页面内容、术语层、视觉层可以分别维护。

### 正式来源

- 课程案例/正文：`skills/learning-page-design-publisher/lessons/*.json`
- 首现术语层：`skills/learning-page-design-publisher/term-overrides.yml`
- 发布视觉/交互层：`docs/_layouts/lesson.html`

### 非正式来源

- `docs/lessons/*.html` 只是发布入口，不手写完整课程正文；
- `examples/` 可以作为历史/归档快照，不是 GitHub Pages 当前 canonical artifact；
- 不允许直接手改 Pages 构建后的线上 HTML。

---

# 2. 硬规则：术语必须先出现，再承担推理作用

## 2.1 Term First-Use Gate · 术语首现守门

对于 `/learn`、入门讲义、跨专业页面，默认顺序：

```text
Hero
→ 先认词 / 核心术语
→ 这段材料到底在说什么
→ 概念关系 / 最小知识闭包
→ 案例还原
→ 概念映射
→ 训练
→ 提示 / 答案
```

禁止：

```text
先用 Runtime / HMR / E2E / readback 得出综合结论
→ 几屏之后再解释这些词
```

如果一个主论断中出现 3 个以上学习者可能不认识的工程术语，必须先建立术语预备区。

## 2.2 首现卡片最低可见信息

术语卡可以折叠，但**折叠状态不能把定义一起藏掉**。

默认必须可见：

```text
英文全称 / 中文名 / 缩写
+ 一句话直觉
```

例如：

```html
<summary>
  Hot Module Replacement (HMR) · 热模块替换
  <span class="term-gloss">
    应用不整体重启，只替换发生变化的前端模块。
  </span>
</summary>
```

展开后再给：

- 严格一点；
- 当前案例；
- 边界；
- 必要时比喻。

## 2.3 什么不算“已经解释”

以下都不算通过首现门：

- 定义在后面的 section；
- 定义只在 tooltip / `aria-label` / alt；
- 定义藏在答案里；
- 只写缩写不写全称；
- 用另一个同样陌生的词解释；
- DOM 顺序在后，只靠 CSS 强行视觉挪前。

必须满足真实阅读顺序：

```text
definition_position(term) < first_reasoning_use(term)
```

## 2.4 术语数量

一门课默认只前置 **真正参与后文推理的 5–15 个核心词**。

不要把术语区做成百科词典。普通品牌名、已经解释过的常识词、后文只出现一次且不参与推理的词，不必强行建卡。

---

# 3. 输入与默认输出

## 输入

可以是：

- `math-cs-concept-tutor` 的结构化教学稿；
- 完整讲义；
- Markdown；
- 真实案例材料；
- 已有 HTML；
- lesson JSON；
- 旧学习页面；
- 用户指定的页面结构。

## `/full` 默认输出

至少完成：

1. 内容结构审计；
2. 术语首现审计；
3. 页面分区与组件映射；
4. canonical lesson source / term registry 更新；
5. Pages data mirror / wrapper 同步；
6. 桌面、手机、打印 QA；
7. terminology gate / consistency 检查；
8. 推送 remote `main`；
9. GitHub Pages build/deploy；
10. 对最终构建 artifact 做 readback。

只在聊天里给一段 HTML，不算 `/full` 完成。

---

# 4. 工作模式

## `/layout`

只做内容拆解、阅读顺序、术语顺序、组件选择与排版方案，不写代码、不发布。

## `/polish`

针对已有页面优化：

- 信息层级；
- 字体；
- 留白；
- 版心；
- 表格；
- callout；
- 术语首现；
- 手机端；
- 打印。

不擅自改写关键知识语义。

## `/mount`

已有最终内容，只负责：

```text
canonical source
→ Pages data / wrapper
→ main
→ Pages build
→ artifact readback
```

## `/full`

```text
内容审计
→ 术语门
→ 拆块
→ 视觉设计
→ canonical source
→ Pages build
→ QA
→ 发布
→ readback
```

---

# 5. 内容长度口径

页面层与 `math-cs-concept-tutor` 使用相同指标：

> **可见教学文本长度（Visible Learning Text Length, VLTL）**

它衡量用户最终真正会读到的教学自然语言，而不是 HTML 文件大小。

## 计入 VLTL

- 标题；
- 正文；
- 列表；
- 表格中的自然语言；
- callout；
- caption；
- 术语 gloss；
- 展开后的术语解释；
- 练习；
- 答案。

## 不计入 VLTL

- HTML 标签与 attribute；
- CSS；
- JavaScript；
- Liquid/Jekyll 模板语法；
- JSON key；
- Mermaid / Graphviz / D2 source；
- LaTeX / MathML markup；
- 代码、命令、配置原文；
- URL；
- 通用导航样板文本；
- 重复 accessibility 文本。

因此：

```text
HTML source length ≠ learning content length
```

页面设计不能靠删除关键知识伪造“轻量”。内容长时优先用 section、目录、表格、分阶段、`details`，必要时拆成多页。

---

# 6. 内容拆解：一屏一个主要认知任务

每个主要 section 尽量只回答一个问题：

```text
这些词是什么意思？
这件事到底在说什么？
概念怎样连接？
真实案例发生了什么？
怎么映射到工程？
我能不能自己判断？
```

默认主要 section 约 5–10 个。

超过 10 个时：

- 先聚类；
- 增加目录；
- 次要信息折叠；
- 必要时拆页；
- 不要制造 20 个同级标题。

### 内容性质 → 组件

| 内容 | 推荐组件 |
|---|---|
| 术语 | term primer + `<details>` |
| 核心结论 | lead / callout |
| 定义 | `<dl>` |
| 对比 | table / compare cards |
| 关系 / 流程 | diagram / step flow |
| 事实 | fact block |
| 推断 | inference block |
| 未知 | unknown block |
| 风险 | risk callout |
| 公式 | 原生 formula block |
| 代码 | `<pre><code>` |
| 命令 | 可复制 `<code>` |
| 补充材料 | `<details>` |
| 练习 | question block |
| 提示 | progressive reveal |
| 答案 | answer panel |

事实 ≠ 推断 ≠ 未知 ≠ 建议 ≠ 风险，不能因为想做得“统一”而揉成一种卡片。

---

# 7. 核心审美原则：视觉友好 ≠ 图片数量多

页面首先依靠这些东西建立视觉层级：

1. 信息顺序；
2. 字体层级；
3. 版心与阅读宽度；
4. 留白；
5. 对齐；
6. 表格；
7. callout；
8. 分栏；
9. 语义色；
10. 原生公式；
11. 代码块；
12. 必要时才使用关系图或解释性图片。

默认**没有图片配额**，也不存在“每个 section 必须有图”。

---

# 8. 最匹配信息结构的表达形式优先

不存在“图 > 表 > 文字”的天然顺序。

```text
关系 / 过程      → 图
比较 / 矩阵      → 表
单一结论         → 关键句 / callout
数学关系         → 原生公式
代码执行语义     → 代码
命令             → 可复制命令块
解释 / 因果      → 正文 + 步骤
空间 / 物理直觉  → 必要时解释性图片
```

Mermaid / Graphviz / D2 的选择由信息结构决定：

- Mermaid：中小型教学流程、时序、状态；
- Graphviz：大型依赖图、DAG、cluster；
- D2：软件架构、服务/容器/数据库边界。

---

# 9. 硬规则：公式、代码、命令不是图片

### 公式

单行公式、定义式、复杂度、概率、递推、性能模型默认使用 LaTeX / MathML / 原生数学排版。

只有需要二维几何、空间标注、多区域高亮或逐步空间解释时，才额外配图；原生可复制公式仍保留。

### 代码和命令

- 代码：`<pre><code>`；
- 命令：`<code>` / command block；
- 配置：文本代码块；
- 单一结论：正文 / callout。

禁止把这些截图化来制造“视觉感”。

---

# 10. 版心、密度与响应式

建议默认：

```text
页面最大宽度：1040–1120px
主要正文阅读宽度：约 62–76ch
桌面：明显左右留白
手机：单列
```

段落：

- 通常 1–4 句；
- 一个段落一个中心关系；
- 长比较转表格；
- 长补充信息折叠。

表格和代码块只允许自己的容器横向滚动，不能把整个页面撑宽。

中文 H1 不用极端字号制造“设计感”。

---

# 11. 交互按需使用

可选：

- progress；
- checklist；
- `<details>`；
- Hint 1 / 2 / 3；
- Final Answer；
- localStorage；
- copy button；
- section navigation。

普通讲义不要强行加 Hint Ladder。

如果有提示链：

```text
Attempt
→ Hint 1 · 方向
→ Hint 2 · 结构
→ Hint 3 · 接近答案
→ Final Answer · 真正答案
```

---

# 12. 当前仓库构建与回洗命令

默认仓库：

```text
ValentinoWang/Study_Skills
branch: main
```

正式同步：

```bash
python3 tools/backwash-term-gates.py
```

只检查不写：

```bash
python3 tools/backwash-term-gates.py --check
python3 tools/build-lessons.py --check
python3 tools/check-lesson-consistency.py
python3 tools/check-term-depth.py
python3 tools/check-term-gate.py
```

如果已经拿到 GitHub Pages `_site` 或 workflow artifact，可进一步：

```bash
python3 tools/check-term-gate.py --built-site /path/to/_site
```

这个检查必须验证：

- `id="terms"` 在 `id="orient"` 前；
- 所有核心术语在术语 section 可见；
- 每个折叠术语卡有 `.term-gloss`；
- 课程入口 URL 没有变化。

---

# 13. 存量课程回洗规则

Skill 结构规则升级后，**不能只保证新课正确**。

必须执行：

```text
更新 Skill / terminology registry / shared layout
→ 扫描所有 canonical lesson JSON
→ 给每门课建立/更新 term pack
→ build/sync Pages data + wrappers
→ consistency / term-depth / term-gate
→ GitHub Pages build
→ 下载最终 artifact
→ 逐页 readback
```

“回洗完成”至少意味着：

1. 所有现有课程进入同一阅读顺序；
2. 当前课程真正用到的关键术语有首现解释；
3. 页面收起术语卡时仍看得到一句话定义；
4. 主论断不再先于定义；
5. GitHub Pages 实际构建产物通过，而不只是源文件看起来正确。

---

# 14. Canonical Artifact 与 QA

最终 QA 应针对 GitHub Pages 构建后的 artifact，而不是只检查仓库源码。

至少验证：

1. GitHub Pages build success；
2. 桌面约 1280px；
3. 手机约 390px；
4. A4 打印；
5. 无页面整体横向滚动；
6. 表格 / 图 / 代码只在自身容器滚动；
7. 长中文标题不溢出；
8. 术语在主论断前；
9. 折叠状态可见 gloss；
10. 所有关键术语覆盖；
11. 练习作答框不重复；
12. Hint Ladder 顺序正确；
13. Final Answer 是真正答案；
14. 打印不丢核心定义；
15. build / consistency / term-depth / term-gate 全部通过。

Pages 的“deployment success”不自动等于内容 QA success；必须继续做 artifact readback。

---

# 15. 首页与发布

正式学习页面 URL：

```text
/lessons/<slug>.html
```

每门正式课应在 `docs/index.html` 有学习入口，除非用户明确要求隐藏。

首页只展示可学习产物；Skill、模板、QA 工具属于仓库内部基础设施，不放在“学习内容”一级卡片中。

---

# 16. 禁止行为

禁止：

1. 首屏连续使用陌生缩写，再在后面补词典；
2. 把一句话定义完全藏在折叠区；
3. 用陌生词解释陌生词；
4. 只改某一门生成 HTML，不修共享规则；
5. Skill 升级后不回洗已有课程；
6. 为了好看改变知识事实；
7. 为了短删除关键定义、因果、边界或答案；
8. 每一段都变成卡片；
9. 为了“视觉化”堆装饰图；
10. 把简单公式、代码、命令截图化；
11. QA 一份页面，发布另一份页面；
12. 只看到 Pages deployment success 就宣布验收完成；
13. 直接手写/复制四份不同页面模板，重新制造漂移。

---

# 17. 最终成功标准

## 教学顺序成功

- 用户第一次看到术语时就能知道它大概是什么；
- 术语解释先于综合判断；
- 不需要先理解一堆黑话才能读第一屏正文。

## 页面成功

- 10 秒内能看懂结构；
- 长文不压迫；
- 视觉层级清楚；
- 桌面、手机、打印都可读；
- 公式、表格、代码、关系图各用最适合自己的形式。

## 工程成功

- lesson JSON / term registry / Pages mirror 一致；
- shared Jekyll layout 唯一；
- URL 稳定；
- remote `main` 已同步；
- Pages build/deploy 成功；
- 最终 artifact 经过术语首现 readback。

一句话：

> **上游保证知识正确；本 Skill 保证学习者先拥有理解这句话所需的词，再看到这句话。**

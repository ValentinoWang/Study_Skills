---
name: learning-page-design-publisher
description: >
  将已经完成或基本完成的学习内容、讲义、案例、题目或技术说明，转换成结构清楚、审美统一、响应式、
  可打印、可交互的静态学习网页，并完成内容拆块、术语首现守门、原生公式与代码呈现、HTML 生成、
  渲染 QA、归档、首页注册与 GitHub Pages 发布。视觉友好依靠信息层级和排版，不依靠图片数量。
---

# Learning Page Design Publisher

## 0. 角色定位

本 Skill 是 Study_Skills 的**页面设计与发布层**。

它不负责重新发明知识结论，而负责把上游内容加工成：

- 读者一上来不会被陌生术语撞晕；
- 信息层级明确；
- 公式、代码和命令可复制；
- 桌面、手机、打印都可读；
- canonical artifact 唯一；
- 能归档并发布到 GitHub Pages。

如果用户首先需要“把 TCP / HMR / Socket 等概念讲懂”，先使用 `math-cs-concept-tutor`。

---

# 1. 硬规则：网页必须先建立术语入口

## 1.1 Term Gate 必须在主论断之前

对于 `/learn`、入门讲义和跨专业页面，默认信息顺序改为：

```text
Hero
→ 先认词 / 核心术语
→ 这段材料到底在说什么
→ 概念关系
→ 案例
→ 映射
→ 训练
→ 提示 / 答案
```

而不是：

```text
先用 Runtime / HMR / readback 讲一大段
→ 第二屏以后再解释这些词
```

如果首个主体 section 含有 3 个以上陌生工程术语，**术语区必须提前**。

## 1.2 折叠卡不能把定义也一起藏掉

术语卡可以使用 `<details>`，但折叠状态必须至少可见：

```text
术语名 / 全称
+ 一句话直觉
```

用户不点击时也应该知道这个词大概是什么；点击后再展开严格定义、边界和当前案例作用。

推荐：

```html
<details>
  <summary>
    Hot Module Replacement (HMR) · 热模块替换
    <span class="term-gloss">应用不整体重启，只替换发生变化的前端模块。</span>
  </summary>
  ...
</details>
```

如果上游已有 `<dl>`，页面层可以机械提取第一个 `<dd>` 作为 summary 的可见 gloss，但不能修改它的知识语义。

## 1.3 首现定义必须在视觉顺序上真的更早

以下不算“先解释”：

- 定义在 DOM 后面但 CSS 视觉上挪前；
- 定义只在 tooltip / alt / aria-label；
- 定义藏在默认不可见答案；
- 首屏先出现缩写，用户滚到后面才看到词卡。

网页真实阅读顺序必须满足：

```text
definition_position(term) < first_reasoning_use(term)
```

## 1.4 Hero 也不能堆黑话

标题为了精确可以保留核心术语，但 Subtitle / Lead 应尽量用人话说明主题。

如果 Hero 连续出现多个缩写，至少在 Subtitle 中展开其中最关键的一个，或者紧接 Hero 放术语预备区。

---

# 2. 输入与输出

输入可以是：完整讲义、`math-cs-concept-tutor` 输出、真实案例、Markdown、已有 HTML、课程 JSON 或旧页面。

默认输出至少包括：

1. 内容分区方案；
2. 术语首现审计；
3. 页面视觉与交互方案；
4. canonical HTML；
5. 桌面 / 手机 / 打印 QA；
6. examples 归档；
7. `docs/lessons/<slug>.html`；
8. `docs/index.html` 入口；
9. GitHub commit SHA；
10. GitHub Pages 最终 URL（若 Pages 可用）。

除非用户明确只要本地文件，否则只在聊天里给 HTML 不算完成。

---

# 3. 工作模式

- `/layout`：只拆结构、术语顺序和组件，不发布。
- `/polish`：已有 HTML 的审美、层级、移动端、打印与术语首现修复。
- `/mount`：已有最终 HTML，只做归档、首页、main、Pages。
- `/full`：默认，完成拆解 → 术语门 → 设计 → 生成 → QA → 发布 → 验证。

---

# 4. 内容长度口径

与 `math-cs-concept-tutor` 使用同一指标：

> **可见教学文本长度（Visible Learning Text Length, VLTL）**

计入：用户实际会读到的标题、正文、列表、表格自然语言、callout、caption、练习、答案、展开后的教学内容。

不计入：HTML/CSS/JS、JSON key、Mermaid/Graphviz/D2 source、LaTeX/MathML 标记、代码/命令/配置原文、URL、通用导航和重复 accessibility 文本。

```text
HTML source length ≠ learning content length
```

页面层不得为了“显得轻”擅自删掉上游关键定义、因果、边界、证据和答案。内容长时优先：目录、section、details、表格、分阶段、必要时多页。

---

# 5. 内容拆解

网页不是把 Markdown 原样套 CSS。

## 5.1 一屏一个主要认知任务

每个 section 尽量只回答一个问题：

```text
这些词是什么意思？
这件事到底在说什么？
它为什么成立？
它怎么工作？
和什么容易混淆？
放到案例里是什么？
我能不能自己判断？
```

## 5.2 顶层 section

默认 5–10 个主要 section。超过 10 个先聚类、加目录、折叠次要内容或拆多页。

## 5.3 组件按语义选

| 内容性质 | 推荐组件 |
|---|---|
| 核心结论 | lead / key takeaway |
| 术语 | term primer + `<details>` |
| 定义 | `<dl>` |
| 比较 | table / compare cards |
| 流程 / 关系 | diagram / step flow |
| 事实 | fact callout |
| 推断 | inference block |
| 未知 | unknown block |
| 风险 | risk callout |
| 代码 | `<pre><code>` |
| 命令 | command block / `<code>` |
| 公式 | 原生 formula block / MathML / LaTeX renderer |
| 补充 | `<details>` |
| 练习 | question block |
| 提示 | progressive reveal |
| 答案 | answer panel |

事实 ≠ 推断 ≠ 未知 ≠ 建议 ≠ 风险，不能为了好看揉在一起。

---

# 6. 核心审美原则：视觉友好 ≠ 图像数量多

页面首先依靠：字体层级、版心、留白、对齐、表格、callout、分栏、语义色、原生公式、代码块建立视觉层级。

默认没有图片配额，也没有“每个 section 必须有图”的要求。

禁止为了丰富页面加入没有信息价值的装饰图。

---

# 7. 公式、代码、命令不是图片

这是硬规则。

- 简单公式 → LaTeX / MathML / 原生公式；
- 代码 → `<pre><code>`；
- 命令 → 可复制 `<code>`；
- 配置 → 文本代码块；
- 单一结论 → 正文 / callout。

只有二维几何、空间标注、复杂多区域高亮确实需要视觉解释时才额外做图。

---

# 8. 静态网页与图形兼容

默认 Offline-first，不依赖 Mermaid / MathJax / KaTeX / 外部字体 / 前端框架 CDN。

关系图优先：

```text
Mermaid / Graphviz / D2 source
→ 预渲染 SVG
→ 或 inline SVG
```

复杂 SVG 要有 `aria-label` / caption，窄屏只让图容器滚动，打印按页宽缩放。

---

# 9. 版心、字体和密度

建议：

```text
页面最大宽度约 1040–1120px
正文阅读列约 62–76ch
桌面明显留白
手机单列
```

中文 H1 不极端放大。段落通常 1–4 句，一个段落一个中心关系。

表格宽时只让表格容器横向滚动；代码块同理，不允许整页横向滚动。

---

# 10. 交互组件按需使用

可选：progress、checklist、details、Hint Ladder、Final Answer、localStorage、copy button、section navigation。

普通讲义不要为了“互动”硬加 Hint 1/2/3。

如果有 Hint Ladder，必须：

```text
Attempt
→ Hint 1
→ Hint 2
→ Hint 3
→ Final Answer
```

最后必须是真正答案。

---

# 11. Canonical Artifact

QA 和发布必须针对同一份最终页面：

```text
内容数据 + canonical template
          ↓
     canonical HTML
          ↓
       render QA
          ↓ PASS
      ┌────┴────┐
      ↓         ↓
 examples/   docs/lessons/
```

禁止 QA 一份、发布再手写另一份。

---

# 12. 存量课程回洗与迁移

当 Skill 的教学结构发生变化，例如新增“术语首现守门”，不能只影响以后新课。

必须执行：

```text
修改 Skill / canonical template
→ 扫描 lessons/*.json
→ 对旧课程做确定性 migration
→ 重新 build 全部 examples + docs/lessons
→ 全量 checker
→ 最终 Pages smoke check
```

迁移脚本必须：

- 幂等：重复运行不重复插卡；
- 只修改明确命中的教学缺陷；
- 不改变原案例事实；
- 修改源 JSON，而不是只修生成 HTML；
- 能在 CI 中重复执行。

---

# 13. 仓库结构与构建

默认仓库：`ValentinoWang/Study_Skills`，branch `main`。

```text
skills/learning-page-design-publisher/
├── SKILL.md
├── assets/lesson-template.html
├── lessons/
├── examples/
└── templates/
```

机械构建：

```bash
python3 tools/backwash-term-gates.py
python3 tools/build-lessons.py
python3 tools/build-lessons.py --check
python3 tools/check-lesson-consistency.py
python3 tools/check-term-depth.py
python3 tools/check-term-gate.py
```

其中 `check-term-gate.py` 负责检查：术语区是否位于主论断前、核心术语是否覆盖、折叠 summary 是否能显示一句直觉。

---

# 14. 渲染 QA

至少验证：

1. 桌面约 1280px；
2. 手机约 390px；
3. A4 打印；
4. 无整页横向滚动；
5. 表格 / 图 / 代码只在自身容器滚动；
6. 长中文标题不溢出；
7. 深色代码块正常；
8. 术语区在阅读顺序上早于主论断；
9. 折叠术语卡未展开时仍可见一句直觉；
10. 缩写没有先使用后解释；
11. progress / checklist 同 key 同步；
12. Hint Ladder 顺序正确；
13. 打印不丢核心定义；
14. 所有 build / consistency / term gate checker 通过。

---

# 15. 首页与发布

正式页面发布到：

```text
docs/lessons/<slug>.html
```

每个正式学习页面在 `docs/index.html` 有入口；Skill、模板、QA 工具不占学习目录一级卡片。

发布状态只有在最终页面可访问并通过核心视觉/交互 smoke check 后才标记 `PUBLISHED / VERIFIED`。

---

# 16. 禁止行为

禁止：

1. 首屏连续使用陌生缩写，再把词典放到后面；
2. 折叠卡把术语的一句话定义也完全藏掉；
3. 用更多陌生词解释陌生词；
4. 把简单公式、代码、命令截图化；
5. 每段都变成卡片；
6. 依靠大量装饰图片制造“视觉感”；
7. 默认依赖外部 CDN；
8. 桌面正常就跳过手机；
9. deployment success 冒充视觉 QA；
10. QA 和发布不是同一 canonical artifact；
11. 只修生成 HTML 不修 canonical source；
12. Skill 规则升级后不回洗已有课程。

---

# 17. 与 Concept Tutor 的合同

```text
math-cs-concept-tutor
  负责：讲什么、术语如何定义、为什么成立、边界是什么
        ↓
learning-page-design-publisher
  负责：定义是否在第一次使用前可见、页面怎么拆、怎么排、怎么发布
```

一句话：**上游保证知识正确，下游保证读者在正确的时间看到正确的解释。**

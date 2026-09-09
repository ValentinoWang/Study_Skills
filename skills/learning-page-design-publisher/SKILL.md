---
name: learning-page-design-publisher
description: >
  将已经完成或基本完成的学习内容、讲义、案例、题目或技术说明，转换成结构清楚、审美统一、
  响应式、可打印、可交互的静态学习网页，并完成内容拆块、视觉排版、原生公式与代码呈现、HTML 生成、
  渲染 QA、归档、首页注册与 GitHub Pages 发布。视觉友好以信息层级和排版为主，不以图片数量为目标。
---

# Learning Page Design Publisher

## 0. 角色定位

这个 Skill 是 **Study_Skills 的页面设计与发布层**。

它的职责不是重新发明知识内容，而是把已有内容加工成真正可读、可交互、可挂载的网页。

核心链路：

```text
已有内容 / 上游讲解
→ 内容审计
→ 页面拆解
→ 信息层级
→ 组件映射
→ 视觉设计
→ canonical HTML
→ 响应式 / 打印 / 交互 QA
→ examples 归档
→ docs/lessons 发布
→ docs/index.html 注册
→ GitHub Pages 验证
```

如果用户首先需要“把 TCP / 线程 / Socket 等概念讲懂”，先使用：

```text
math-cs-concept-tutor
```

如果内容已经清楚，用户要“做成网页 / 美化 / 拆块 / 排版 / 发布”，使用本 Skill。

---

# 1. 输入与输出

## 输入可以是

- 一段完整讲义；
- `math-cs-concept-tutor` 的结构化输出；
- 真实案例材料；
- Markdown；
- 已有 HTML；
- 课程 JSON；
- 用户指定的网页结构；
- 需要重新排版的旧页面。

## 默认输出

至少产出：

1. 内容分区方案；
2. 页面视觉与交互方案；
3. canonical HTML 或由 canonical 模板生成的 HTML；
4. 桌面 / 手机 / 打印 QA；
5. 仓库归档；
6. `docs/lessons/<slug>.html`；
7. `docs/index.html` 入口；
8. GitHub commit SHA；
9. 最终 GitHub Pages URL（若 Pages 可用）。

除非用户明确只要本地文件，否则“只在聊天里给 HTML”不算完成。

---

# 2. 工作模式

## `/layout`

只做内容拆解、页面结构、组件选择和排版建议，不写代码、不发布。

## `/polish`

针对已有 HTML 做视觉审美、层级、间距、字体、卡片、颜色、移动端和打印优化。

## `/mount`

已有最终 HTML，只负责：

```text
归档
→ docs/lessons
→ 首页注册
→ main
→ Pages 验证
```

## `/full` — 默认

```text
拆解
→ 设计
→ 生成
→ QA
→ 归档
→ 发布
→ 验证
```

---

# 3. 内容长度口径：看用户读到什么，不看 HTML 有多少字符

本 Skill 与 `math-cs-concept-tutor` 使用同一口径：

> **可见教学文本长度（Visible Learning Text Length, VLTL）**

它衡量最终学习者实际会读到的教学自然语言，而不是源文件大小。

## 3.1 计入 VLTL

- 标题；
- 正文；
- 列表；
- 表格里的自然语言；
- callout / caption；
- 练习与答案；
- `<details>` 展开后会看到的教学内容；
- 本课特有的解释标签。

## 3.2 不计入 VLTL

- HTML 标签、属性；
- CSS；
- JavaScript；
- JSON key；
- Mermaid / Graphviz / D2 source；
- LaTeX / MathML markup 与公式源码；
- 代码、命令、配置原文；
- URL；
- 通用导航、Footer、按钮样板文案；
- 重复可见信息的 accessibility 文本。

因此：

```text
HTML source length ≠ learning content length
```

一个 50 KB 页面不等于“5 万字课程”。

## 3.3 页面设计不得靠删内容伪造“轻量”

如果上游内容较长：

- 先分 section；
- 增加目录 / anchor；
- 次要材料可用 `<details>`；
- 比较内容转表格；
- 长链路拆成多个阶段；
- 必要时拆成多页。

**不能为了让页面显得短，擅自删除上游的关键定义、因果、边界、证据和答案。**

如果需要明显压缩内容，回到上游内容层处理，而不是在 CSS/HTML 层偷偷删。

---

# 4. 内容拆解规则

网页不是把 Markdown 原样包一层 CSS。

必须先重新组织信息层级。

## 4.1 一屏一个主要认知任务

每个 section 尽量只回答一个问题，例如：

```text
这是什么？
为什么重要？
它怎么工作？
和什么容易混淆？
放到案例里是什么？
我现在能不能自己判断？
```

避免一个 section 同时承担定义、历史、机制、比较、题目、答案六件事。

## 4.2 顶层 section 数量

默认 5–10 个主要 section。

如果超过 10 个：

- 先聚类；
- 将次要内容折叠进 details / tabs / card group；
- 长课程可加目录；
- 必要时拆成多页；
- 不要让目录变成 20 项没有层次的清单。

## 4.3 内容块类型

把原文映射为最匹配语义的组件：

| 内容性质 | 推荐组件 |
|---|---|
| 核心结论 | lead / key takeaway |
| 定义 | definition block / `<dl>` |
| 对比 | table / compare cards |
| 流程 / 关系 | diagram / step flow |
| 单一事实 | fact callout / 正文关键句 |
| 推断 | inference block |
| 未知 | unknown block |
| 风险 | risk callout |
| 代码 | `<pre><code>` |
| 命令 | command block / `<code>` |
| 公式 | 原生 formula block / MathML / LaTeX renderer |
| 补充细节 | `<details>` |
| 练习 | question block |
| 提示 | progressive reveal |
| 最终答案 | answer panel |

不要为了视觉统一把所有内容都塞成同一种卡片。

## 4.4 保留语义边界

页面重排时必须区分：

```text
事实 ≠ 推断 ≠ 未知 ≠ 建议 ≠ 风险
```

不能为了“好看”把这些不同语义揉成一段。

---

# 5. 核心审美原则：视觉友好 ≠ 图像数量多

这是硬规则：

> **“视觉友好”不等于“多生成几张图片”。**

页面首先依靠这些东西建立层级：

1. 字体层级；
2. 版心与阅读宽度；
3. 留白；
4. 对齐；
5. 表格；
6. callout；
7. 分栏；
8. 语义色；
9. 原生公式；
10. 代码块；
11. 必要时才使用图和图片。

默认**没有图片配额**，也没有“每个 section 必须有视觉素材”的要求。

禁止为了显得丰富而加入没有信息价值的装饰图。

---

# 6. 表达形式必须匹配信息结构

不存在“图天然高于文字”的优先级。

```text
关系 / 过程      → 图
比较 / 矩阵      → 表
单一结论         → 关键句 / callout
数学关系         → 原生公式
状态 / 时序      → 状态图 / 时序图
精确执行语义     → 代码
命令 / 配置      → 原生文本块
空间 / 物理直觉  → 图片
解释 / 因果      → 正文
```

如果一句话能准确表达，就不要为它单独生成一张图片。

如果表格比关系图更容易比较，就用表格。

如果公式就是公式，就让它保持公式。

---

# 7. 硬规则：公式、代码、命令和单一结论禁止图片化

## 7.1 公式不是图片

以下内容默认使用：

- LaTeX 的原生渲染；
- MathML；
- 浏览器/运行环境支持的原生数学排版；
- 极简单情况可使用语义明确的正文排版。

适用：

- 单行公式；
- 定义式；
- 简单计算；
- 复杂度；
- 概率；
- 递推；
- 性能模型；
- 一般多行推导。

禁止：

- 截图公式；
- 生成图片重新画公式；
- 批量把公式做成 PNG 卡片；
- 仅为了“视觉统一”把公式转图片。

只有当公式需要**二维标注、几何解释、多区域高亮、箭头指向或公式与图形位置对应**时，才允许增加视觉化图层。

即使如此，页面仍必须保留可复制的原生公式。

## 7.2 代码和命令不是图片

代码、Shell 命令、配置、JSON、日志必须保留为可复制文本。

禁止：

- 代码截图；
- Terminal 截图代替命令；
- 用生成图片展示配置；
- 把单一命令放进装饰性图片卡片。

## 7.3 单一结论不是图片

例如：

```text
Socket 是编程接口，不是传输协议。
```

这种内容应使用关键句 / callout / 对比表，不应生成一张“海报图”。

---

# 8. 页面信息架构

推荐默认结构：

```text
Hero
│
├─ 页面说明 / 元信息
├─ 学习目标或阅读目标
│
├─ Section 1：定位
├─ Section 2：核心内容
├─ Section 3：机制 / 关系
├─ Section 4：案例 / 应用
├─ Section 5：比较 / 风险
├─ Section 6：练习 / 答案（若有）
│
└─ Footer / 来源 / 返回入口
```

不是每个页面都必须有题目或提示链。

如果上游内容只是技术讲义，就做技术讲义；不要为了“主动学习”硬加 Hint 1/2/3。

---

# 9. 视觉审美规则

## 9.1 设计目标

页面要达到：

- 第一眼知道主题；
- 10 秒内知道页面结构；
- 长文不压迫；
- 重点与次要信息层级明确；
- 桌面和手机都像同一个产品；
- 打印后仍可读；
- 不依赖炫技动画、插画数量或阴影数量维持可用性。

## 9.2 版心

建议：

```text
页面最大宽度：约 1040–1120px
正文阅读列：约 62–76ch
桌面左右留白明显
手机：单列
```

Hero 与正文尽量共用一致版心。

## 9.3 字体层级

至少形成：

```text
H1
> H2
> H3 / Card title
> Body
> Meta / Caption
```

中文 H1 不要为了“设计感”放到极端巨大。

正文 line-height 保持舒适阅读区间。

## 9.4 色彩

颜色必须有语义角色。

使用 CSS 变量，例如：

```css
:root {
  --bg: ...;
  --surface: ...;
  --ink: ...;
  --muted: ...;
  --line: ...;
  --accent: ...;
  --risk: ...;
  --success: ...;
}
```

避免：

- 每张卡随机颜色；
- 同一种语义使用多个无规则颜色；
- 低对比浅灰正文；
- 深色代码块里出现浅色 inline-code 背景块。

## 9.5 卡片

卡片只在内容确实是独立单元时使用。

不要把每一个普通段落都做成圆角阴影卡。

推荐：

- surface；
- border；
- modest radius；
- restrained shadow；
- whitespace 优先于装饰。

---

# 10. 排版与阅读密度

## 10.1 段落

- 一个段落一个中心关系；
- 一般 1–4 句；
- 复杂因果允许更长，但不要堆成没有层次的墙；
- 长定义用 `<dl>`；
- 长比较用表格；
- 次要补充信息可折叠。

## 10.2 列表

同一列表通常 3–8 项。

超过时考虑：

- 分组；
- 两列；
- 表格；
- details。

## 10.3 表格

宽表格必须：

- 放在独立 overflow 容器；
- 手机端横向滚动只发生在表格本身；
- 不能撑宽整个页面。

## 10.4 代码

深色代码块固定处理：

```css
pre code {
  padding: 0;
  background: transparent;
  color: inherit;
  border-radius: 0;
}
```

代码块过宽时自己滚动，不允许页面整体横向滚动。

## 10.5 长页面

当 VLTL 较长时，优先：

- sticky / static TOC（按场景）；
- 清楚的 section heading；
- anchor；
- 合理的上下留白；
- 将辅助内容折叠；
- 必要时分页。

不要靠把字体缩小来“塞下更多字”。

---

# 11. 图、公式与静态网页兼容

上游内容可能包含：

- Mermaid；
- Graphviz；
- D2；
- LaTeX；
- 生成图片。

本 Skill 负责把“语义表示”变成“网页可稳定显示的表示”，但**不能改变其语义类型**。

## 11.1 Offline-first

默认禁止依赖：

- Mermaid CDN；
- MathJax CDN；
- KaTeX CDN；
- 外部字体；
- 外部前端框架 CDN。

关系图优先：

```text
Mermaid / Graphviz / D2 source
→ 本地/构建时预渲染 SVG
→ 或转换为 inline SVG
```

公式优先：

```text
LaTeX semantic source
→ MathML / 本地可用原生数学 renderer
→ 保留 machine-readable source
```

**不得因为 offline-first 就把所有公式转成 PNG。**

如果某复杂公式确实需要特殊 fallback，仍应保留可访问、可复制的原始表达；图片只能是补充，不应成为唯一载体。

## 11.2 SVG 图

复杂关系可使用：

```html
<figure class="diagram">
  <div class="diagram-scroll">
    <svg viewBox="0 0 960 320" role="img" aria-label="完整文字描述">…</svg>
  </div>
  <figcaption>读图说明。</figcaption>
</figure>
```

要求：

- `aria-label` 足以替代图；
- 窄屏只让图本身横向滚动；
- 打印时按页宽缩放；
- 颜色来自设计 token；
- 图中不要塞长段正文。

## 11.3 图片生成

只在真正需要空间、物理或具象直觉时使用。

不允许把以下东西交给图片生成模型：

- 公式；
- 代码；
- 命令；
- 表格；
- 大段文字；
- 精确系统拓扑；
- 需要逐字准确的技术标签。

---

# 12. 交互组件按需使用

交互不是强制项。

可选：

- progress；
- checklist；
- `<details>`；
- Hint 1 / 2 / 3；
- Final Answer；
- localStorage；
- copy button；
- section navigation。

只有内容真的需要主动练习时才加入 Hint Ladder。

如果使用：

```text
Attempt
→ Hint 1：方向
→ Hint 2：结构
→ Hint 3：接近答案
→ Final Answer：真正答案
```

不能到 Hint 3 就结束。

---

# 13. Canonical Artifact

QA 和发布必须针对同一份最终页面。

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

禁止：

```text
QA 一份 HTML
→ 发布时又重新手写另一份
```

任何发布版改动都必须重新 QA。

---

# 14. 仓库结构

默认仓库：

```text
ValentinoWang/Study_Skills
branch: main
```

本 Skill 路径：

```text
skills/learning-page-design-publisher/
├── SKILL.md
├── assets/
│   └── lesson-template.html
├── lessons/
├── examples/
└── templates/
    └── latex-learning-report.html
```

发布路径：

```text
docs/lessons/<slug>.html
```

首页：

```text
docs/index.html
```

---

# 15. 构建流程

现有机械构建入口：

```bash
python3 tools/build-lessons.py
python3 tools/build-lessons.py --check
python3 tools/check-lesson-consistency.py
```

对于包含术语卡的主动学习页面，再运行：

```bash
python3 tools/check-term-depth.py
```

`check-term-depth.py` 是特定页面类型的内容门禁，不要求所有普通技术讲义都必须出现术语卡。

---

# 16. 模板一致性

设计系统的 CSS、JS 和主要页面骨架只能有一个 canonical 来源：

```text
skills/learning-page-design-publisher/assets/lesson-template.html
```

课程之间主要允许**内容不同**。

如果新增通用组件：

```text
先提升进 canonical template
→ 再重新生成全部受影响页面
```

不要只在某一课偷偷复制一套新 CSS，导致不同页面像两个产品。

模板版本应由实际内容 hash 派生，而不是人工写一个容易忘记更新的版本号。

---

# 17. 渲染 QA

不能只检查源码。

至少验证：

1. 桌面约 1280px；
2. 手机约 390px；
3. A4 打印；
4. 页面无整体横向滚动；
5. 表格 / 图 / 代码只在自己的容器内滚动；
6. H1 / 长中文标题不溢出；
7. 代码块背景正常；
8. 折叠组件可展开；
9. 如果有 progress / checklist，同 key 状态同步；
10. 如果有 Hint Ladder，顺序正确；
11. Final Answer 真的是答案；
12. CSS Grid / Flex 子项有必要的 `min-width: 0`；
13. 打印不丢核心内容；
14. 简单公式仍为原生可复制公式，而不是图片；
15. 代码 / 命令仍为可复制文本，而不是截图；
16. 没有为了“视觉丰富”加入无信息价值图片；
17. `build-lessons.py --check` 通过；
18. `check-lesson-consistency.py` 通过。

如果页面类型包含术语卡，再额外要求 `check-term-depth.py` 通过。

---

# 18. 发布闭环

默认发布流程：

```text
确定 slug
→ 写入 lessons/<slug>.json 或 canonical source
→ build
→ QA
→ examples/<slug>.html
→ docs/lessons/<slug>.html
→ 注册 docs/index.html
→ commit 到 main
→ 获取 commit SHA
→ 检查 Pages deployment
→ smoke check 最终 URL
```

最终状态建议：

```text
LOCAL_ONLY
GITHUB_SYNCED
PUBLISHED / QA_BLOCKED
PUBLISHED / VERIFIED
```

只有最终网页可访问且核心视觉/交互验证通过，才标记：

```text
PUBLISHED / VERIFIED
```

---

# 19. 首页注册

每个**正式学习页面**都应该在 `docs/index.html` 有入口，除非用户明确要求隐藏。

卡片至少包括：

- 标题；
- 一句话说明；
- 类型 / 主题标签；
- 日期（适用时）；
- 页面链接。

**Skill、模板、构建脚本、QA 工具属于仓库内部生产基础设施，不作为学习内容卡片注册到首页。**

不要生成正式学习页面的“孤儿页”：页面发布了但学习目录找不到。

---

# 20. 禁止行为

禁止：

1. 把已有 Markdown 原样套 CSS 就宣称完成设计；
2. 为了好看改变事实语义；
3. 每段都变成卡片；
4. 页面同时出现多套视觉语言；
5. 随机使用大量颜色和阴影；
6. 默认依赖外部 CDN；
7. 桌面看起来正常就跳过手机；
8. GitHub Pages deployment success 就等于视觉 QA success；
9. QA 文件和发布文件不是同一 canonical artifact；
10. 用户只需要排版时擅自改写大量内容；
11. 普通讲义强行加入提示链；
12. 把 Skill / 工具注册成首页学习卡片；
13. 只给 sandbox 文件却不完成用户要求的仓库挂载；
14. 将简单公式截图化 / 图片化；
15. 将代码、命令、配置截图化；
16. 用生成图片代替单一结论；
17. 为了“视觉友好”设置图片数量 KPI；
18. 用 HTML 源码字符数冒充教学字数。

---

# 21. 最终成功标准

## 内容结构成功

- 页面每个 section 有清晰任务；
- 事实、推断、未知、风险没有混淆；
- 长内容被合理拆块但没有碎片化；
- VLTL 口径与上游一致，没有因 HTML/CSS/JS 膨胀而误判篇幅。

## 审美成功

- 视觉层级清楚；
- 留白、字体、颜色、卡片一致；
- 桌面、手机、打印都可读；
- 图、表、代码不破坏页面宽度；
- 简单公式、代码、命令仍保持原生、可复制；
- 即使没有生成图片，页面也应该视觉友好。

## 工程成功

- canonical artifact 唯一；
- examples 与 docs/lessons 一致；
- 构建检查通过；
- 正式学习页面首页入口存在；
- main 已提交；
- Pages 可访问；
- 最终页面经过 smoke check。

---

# 22. 与 `math-cs-concept-tutor` 的协作方式

推荐完整链路：

```text
用户：给我讲清楚某个计算机概念
        ↓
math-cs-concept-tutor
        ↓
得到结构化、足够深入、按 VLTL 控制的教学内容
        ↓
用户：把这个做成好看的学习网页
        ↓
learning-page-design-publisher
        ↓
拆块 + 排版层级 + 原生公式/代码 + 必要图形 + HTML + QA + GitHub Pages
```

一句话区分：

> **`math-cs-concept-tutor` 决定“讲什么、怎么讲清楚”；`learning-page-design-publisher` 决定“如何把这些内容排成一个好看、稳定、可复制、可发布的网页”。**
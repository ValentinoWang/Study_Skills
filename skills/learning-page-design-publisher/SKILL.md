---
name: learning-page-design-publisher
description: >
  将已完成或基本完成的学习内容、讲义、案例、题目或技术说明转换成结构清楚、响应式、可打印、可交互的学习网页；
  负责术语/变量首现呈现、内容拆块、GitHub Pages 构建、浏览器 QA、归档和发布。特别区分 artifact identity、
  semantic correctness、rendered correctness，并要求生成器、检查器和最终页面共享同一份课程机器合同。
---

# Learning Page Design Publisher

## 0. 角色定位

本 Skill 是 Study_Skills 的**页面设计、渲染与发布层**。

```text
math-cs-concept-tutor
  决定：讲什么、前置是什么、术语/变量怎么定义、机制为什么成立
                    ↓
learning-page-design-publisher
  决定：定义先在哪里出现、章节怎么拆、如何生成、如何 QA、如何发布和读回
```

Publisher 不得为了模板方便、文件缩小或提交省事，把完整讲义换成缩略稿。

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

长讲义或特殊布局必须显式登记在：

```text
skills/learning-page-design-publisher/lesson-manifest.json
```

manifest 可以声明：

- `layout`：使用哪个 Jekyll layout；
- `term_source`：术语来自 registry 还是 lesson 本身；
- `supplement_source_dir`：长章节 canonical 源目录；
- `supplement_pages_dir`：Pages include 镜像目录；
- `global_prerequisites`：全课阅读变量/符号预备；
- `section_prerequisites`：每章在推理前必须出现的术语、变量和 ID。

**生成器、consistency、term gate、term depth 都必须读取同一 manifest。**禁止在脚本里各自硬编码另一套课程结构。

`docs/lessons/*.html` 只保存 Jekyll front matter。长章节正文也不能只存在 `docs/_includes`；必须从 manifest 声明的 canonical supplement source 镜像过去。

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
练习与答案
建议学习时长及活动构成（若有时长）
```

若这些内容缺失，Publisher 不能用排版掩盖教学缺口；应先补内容合同。

---

# 3. 术语与变量首现守门

入门课必须满足：

```text
definition_position(x) < first_reasoning_use(x)
```

这里 `x` 不只包括术语，还包括：

- 缩写；
- 工程概念；
- 变量；
- 函数名和参数；
- `xxx_id` 字段；
- 状态取值；
- SQL 占位符；
- 公式符号；
- 单位和性能指标。

长讲义默认阅读顺序：

```text
Hero
→ 全局核心术语
→ 全景 / 知识地图
→ 必要的“怎么读变量 / 伪代码”
→ 每章自己的先认词 / 先认变量
→ 机制 / trace / 反例
→ 小题
→ 综合题 / 提示 / 答案
```

全局词典不能替代章节闭包。一个变量只在第三章出现，就可以在第三章定义，但必须早于第三章第一次推理使用。

折叠术语卡未展开时至少显示：英文全称 / 中文名 / 缩写 + 一句话直觉。

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

不得把 manifest 中声明为 `lesson-expanded` 的入口重新覆盖成默认 `lesson`。

`build-lessons.py --check` 和 `check-lesson-consistency.py` 必须能发现：

- wrapper layout 被改回默认布局；
- supplement source 与 Pages include 漂移；
- supplement 缺文件或出现 orphan；
- manifest 指向不存在的 layout。

---

# 5. 可见教学文本长度与时长

使用 Visible Learning Text Length (VLTL) 衡量用户真正看到的教学自然语言。

不以 HTML/CSS/JS 字节数、文件大小或标题数量估算学习时长。

若页面标“20 分钟”“2 小时”，必须把它当作**建议学习安排**，并有阅读 / trace / 练习 / 核对答案等活动构成；没有真实试读数据时不得声称为实测时长。

---

# 6. 信息结构决定表达形式

```text
关系 / 过程      → Mermaid / Graphviz / D2 / inline SVG
比较 / 矩阵      → table
单一结论         → callout
数学关系         → 原生 MathML / LaTeX renderer
代码执行语义     → <pre><code>
解释 / 因果      → 正文 + 步骤
```

视觉化不是装饰 KPI。

---

# 7. 公式与代码呈现

MathML 根节点不能被普通布局接管。需要横向滚动时滚动外层 wrapper，不给 `<math>` 设置 flex/grid/overflow。

代码块出现前必须确认：其中承担推理作用的变量、参数、字段、占位符已经解释。代码块不是定义区。

---

# 8. 三层证据

## 8.1 Artifact Identity

回答：两份产物是不是同一份字节？

证据：blob OID、SHA、digest、mirror byte equality。

## 8.2 Semantic Correctness

回答：结构和教学合同是否正确？

证据：schema、consistency、term gate、prerequisite gate、depth gate、业务/内容审阅。

## 8.3 Rendered Correctness

回答：最终浏览器真正显示和执行是否正确？

证据：GitHub Pages artifact + 浏览器 render、DOM、交互、打印 readback。

```text
same bytes
≠ semantic correct
≠ rendered correct
```

---

# 9. 默认 `/full` 闭环

```text
内容审计
→ 上游学习合同检查
→ 术语 / 变量首现门
→ 页面拆块
→ canonical lesson + manifest + supplements
→ build-lessons 同步
→ consistency / term-depth / term-gate / math-safety
→ GitHub Pages build
→ 桌面 / 手机 / 打印浏览器 QA
→ artifact readback
→ remote main
```

只给 HTML、只看源码、只看到 deployment success，都不算 `/full` 完成。

---

# 10. 构建与门禁

默认执行：

```bash
python3 tools/backwash-term-gates.py --check
python3 tools/build-lessons.py --check
python3 tools/check-lesson-consistency.py
python3 tools/check-term-depth.py
python3 tools/check-term-gate.py
python3 tools/check-math-render-safety.py
```

拿到 `_site` / Pages artifact 后继续：

```bash
python3 tools/check-term-gate.py --built-site /path/to/_site
python3 tools/check-math-render-safety.py --built-site /path/to/_site
```

静态检查只能证明可机械验证的条件。它不能单独证明“读者一定看懂”。

---

# 11. 发布状态必须分层

最终汇报必须区分：

| 状态 | 证据 |
|---|---|
| 源码已提交 | remote main 包含目标 commit |
| 构建已完成 | 对应 commit 的 Pages build 成功 |
| 部署已完成 | 对应 artifact deploy 成功 |
| 页面内容已核实 | 公开页面 / 构建 artifact 包含预期章节和版本 |
| 页面交互已验证 | 浏览器中的折叠、作答、移动端、打印等检查 |

不能把“源码在 main”写成“课程已上线”，也不能把“deploy success”写成“视觉 / 教学验收完成”。

---

# 12. 响应式与浏览器 QA

至少验证：

1. Pages build success；
2. 桌面约 1280px；
3. 手机约 390px；
4. A4 打印；
5. 页面根元素无意外横向滚动；
6. 表格、代码、图、公式只在自己的容器滚动；
7. 长中文标题不溢出；
8. 术语 / 变量定义早于推理；
9. Hint Ladder 顺序正确；
10. Final Answer 真的是答案；
11. 页面实际包含 manifest 声明的所有章节；
12. identity、semantic、render 三类证据分开记录。

---

# 13. 存量课程回洗

Skill、manifest、layout 或门禁升级后：

```text
扫描 canonical lessons
→ build-lessons --check
→ consistency
→ term / prerequisite depth
→ term / prerequisite gate
→ math safety
→ Pages build
→ 最终 artifact readback
```

必须保留两个核心回归条件：

1. **未定义的变量 / ID 出现在推理或代码里，不能被误判为通过。**
2. **重新运行 build-lessons 不能让长讲义从特殊布局退回默认布局，也不能让 supplement 章节消失。**

---

# 14. 禁止行为

禁止：

1. 先堆黑话后补词典；
2. 公式 / 伪代码先出现，变量定义后出现；
3. 只解释“这是变量”，不绑定当前业务对象；
4. 只改 Pages include，不改 canonical supplement；
5. 生成器忽略 lesson manifest；
6. 用 blob/hash 一致宣称教学正确；
7. 只看到 Pages deployment success 就宣布完成；
8. 为了短删除定义、trace、因果、边界或答案；
9. 课程标时长却没有对应学习活动；
10. QA 一份 artifact，发布另一份 artifact。

---

# 15. 成功标准

## 教学成功

- 第一次看到术语、变量、ID 就知道它在当前系统里指什么；
- 代码块和公式可以逐个翻译回业务含义；
- 每章都能独立形成最小学习闭包；
- 学习者可以追踪一次真实状态变化并自己排错。

## 工程成功

- canonical lesson / supplement / manifest / Pages mirror 一致；
- wrapper layout 与 manifest 一致；
- remote main、Pages artifact、公开页面可追溯到同一候选；
- 最终 artifact 通过真实浏览器 readback。

一句话：

> **上游定义“学什么和先懂什么”；Publisher 把这些依赖变成可见、可检查、不会被重新构建丢掉的学习页面。**

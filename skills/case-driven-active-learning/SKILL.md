---
name: case-driven-active-learning
description: >
  将包含大量陌生术语、专业概念、工程背景或行业知识的真实材料，
  转换成“最小知识学习 → 案例还原 → 主动做题 → 分级提示 → 成熟解法 →
  反思迁移”的干中学课程。使用双模板：交互式练习工作表负责做题，
  LaTeX 风格讲义负责结题沉淀与打印。为 Study_Skills 生成的案例 HTML
  默认必须同步到 ValentinoWang/Study_Skills 的 main 分支，同时发布到
  GitHub Pages 的 docs/lessons、注册首页导航并验证 Pages 部署。
---

# Case-Driven Active Learning

## 0. 核心任务与完成条件

把用户提供的真实材料转化为一节主动学习课程，而不是只做术语翻译或直接给答案：

```text
真实材料
→ 识别真正问题与未知知识
→ 建立最小知识闭包
→ 还原对象、状态与约束
→ 把案例改造成训练题
→ 用户尝试作答
→ 分级提示与针对性反馈
→ 成熟解法、验证标准与专家心智模型
→ 迁移练习
→ 生成 HTML
→ 归档 examples/
→ 发布 docs/lessons/
→ 注册 docs/index.html
→ 提交 GitHub main
→ 验证文件、commit 与 Pages deployment
→ 返回可访问的 GitHub Pages URL
```

### 0.1 GitHub 同步与网页发布是强制交付闭环

对于本 Skill 生成并归档到 `Study_Skills` 的 HTML，下面这些状态都**不算完成**：

- 只在聊天中给出 HTML；
- 只生成到 `/mnt/data`、sandbox 或当前会话；
- 只给一个下载链接；
- 只建议用户“之后提交 GitHub”；
- 已经写入 GitHub，但没有确认目标分支与 commit；
- 只写入 `skills/case-driven-active-learning/examples/`，但没有发布到 `docs/lessons/`；
- 已发布到 `docs/lessons/`，但没有把课程注册到 `docs/index.html`；
- 仓库文件存在，但没有确认 GitHub Pages 是否针对最新 commit 成功部署。

除非用户明确要求仅本地生成，否则完成条件必须同时包括：

1. HTML 真实生成；
2. 归档到 `skills/case-driven-active-learning/examples/<slug>.html`；
3. 发布到 `docs/lessons/<slug>.html`；
4. 在 `docs/index.html` 增加可导航到该课程的入口；
5. 写入 `ValentinoWang/Study_Skills` 的 `main`；
6. 获得本次写入的 commit SHA；
7. 重新读取归档文件、发布文件和首页，确认 `main` 上均存在且导航路径正确；
8. 检查 GitHub Pages 最新 `pages build and deployment` 针对该 commit 成功；
9. 最终回复给出仓库路径、commit SHA、GitHub 文件链接和 GitHub Pages 页面 URL。

若 GitHub 写入失败，状态必须明确为：

```text
LOCAL_ONLY / GITHUB_SYNC_BLOCKED
```

若仓库写入成功但 Pages 发布失败，状态必须明确为：

```text
GITHUB_SYNCED / PAGES_DEPLOY_BLOCKED
```

不要把本地生成、仓库归档或未部署成功的网页描述成最终发布完成。

默认归档目录：

```text
skills/case-driven-active-learning/examples/
```

默认网页发布目录：

```text
docs/lessons/
```

默认站点入口：

```text
https://valentinowang.github.io/Study_Skills/index.html
```

---

# 1. 双模板架构：两套模板都必须使用

本 Skill 明确保留两套模板，它们职责不同，不得互相替代。

## 1.1 第一阶段练习模板

```text
assets/lesson-template.html
```

用途：`/learn` 的主动做题阶段。

目标：

- 让用户先理解最小知识；
- 直接在网页中作答；
- 逐级查看 Hint 1–3；
- 使用 `localStorage` 暂存答案与学习进度；
- 一键复制作答回到对话；
- **源码中不得出现成熟答案**。

视觉定位：清爽、轻量、适合交互，不做 SaaS 仪表盘式堆卡。

## 1.2 结题讲义模板

```text
templates/latex-learning-report.html
```

用途：

- `/learn` 完成作答和反馈后的最终结题稿；
- `/solve` 的完整讲解；
- `/exam` 用户请求答案后的答案稿；
- 长期归档、分享和 A4/PDF 打印。

视觉定位：现代 LaTeX 讲义，依靠版心、留白、细线、字体层级和语义环境建立结构。

**不得让该模板成为孤儿文件。** 每次进入结题阶段必须优先从它生成最终 HTML。

---

# 2. 三种运行模式

## `/learn`：默认

第一轮：

```text
ORIENT → LEARN → RECONSTRUCT → ATTEMPT
```

生成交互式练习 HTML，但源码中不能包含成熟答案。用户作答后再进入：

```text
FEEDBACK → SOLVE → REFLECT → TRANSFER → PUBLISH
```

最终使用 `templates/latex-learning-report.html` 生成结题讲义。

## `/solve`

一轮完成术语、案例、推理框架、成熟方案、迁移训练，并直接使用 LaTeX 风格讲义模板输出。

## `/exam`

只提供必要背景、题目、约束、评分标准和答题区。默认无提示、无答案。答案稿另行生成。

---

# 3. 教学原则

1. **案例优先**：真实案例本身就是教材。
2. **Just-in-Time Learning**：只学解决当前问题需要的知识。
3. **主动回忆优先**：具备最小知识后尽快让用户作答。
4. **先保护思考机会**：`/learn` 不在题目后立刻给答案。
5. **逐步撤掉脚手架**：同类问题越往后提示越少。
6. **事实、推断、未知分开**：不能把合理猜测写成事实。
7. **验证优先**：任何成熟方案都必须告诉用户如何确认它真的成功。

---

# 4. 最小知识闭包

## 4.1 术语分层

### A. 核心术语

不懂就无法完成当前案例。通常 5–12 个，使用五层解释。

### B. 支撑术语

有助于分析但不是主线。通常 3–8 个，简短解释。

### C. 当前可忽略

当前结论不依赖。明确说明为什么现在不用学。

## 4.2 五层解释法

每个核心术语必须依次给：

1. 一句话直觉；
2. 严格定义；
3. 比喻或直观模型；
4. 比喻失效处；
5. 它在当前案例中影响哪个判断。

遵循：

```text
自然语言 → 结构关系 → 领域语言 → 严格定义
```

禁止用一串新的陌生术语解释一个陌生术语。

## 4.3 概念地图

解释完术语后建立：

- 包含关系；
- 依赖关系；
- 因果关系；
- 对象 / 状态 / 操作 / 指标分类；
- 易混淆概念；
- 先后约束。

最终 HTML 优先使用内联 SVG、HTML/CSS 图或简单文本树。不要依赖 Mermaid 运行时。

## 4.4 最小记忆清单

进入题目之前，只保留 3–7 条真正需要记住的原则。

---

# 5. 案例还原

不要逐句翻译。将材料重构为：

1. 背景；
2. 关键对象；
3. 当前状态；
4. 已知事实；
5. 可以推断；
6. 尚不知道；
7. 关键风险；
8. 真正问题。

必须建立“概念 → 现实实例 → 影响判断”的映射表。

---

# 6. 把场景改造成训练题

训练题至少包含：

- 用户扮演的角色；
- 目标状态；
- 已知条件；
- 限制条件；
- 不可接受的失败；
- 可观察的成功标准。

通常拆成五类问题：

1. 理解题；
2. 诊断题；
3. 风险题；
4. 方案题；
5. 验证题。

思考脚手架：

```text
识别对象
→ 标注状态
→ 找差异和约束
→ 找不可逆风险
→ 确定第一保护目标
→ 设计降低不确定性的操作顺序
→ 定义验证证据
```

---

# 7. Hint Ladder 与反馈

## Hint 1：方向

只指出应该关注哪个对象、变量或风险。

## Hint 2：结构

给出解决问题的阶段结构，不填关键答案。

## Hint 3：接近答案

给接近执行层的提示，仍让用户完成最后判断。

用户回答后反馈必须包括：

- 你的判断；
- 已经掌握；
- 还缺什么；
- 如果照此执行会有什么风险；
- 更成熟的组织方式；
- 成熟方案与验证标准。

如评分，必须按明确维度计算，不得凭感觉生成百分比。

---

# 8. 成熟方案最低要求

必须包含：

1. 问题本质；
2. 目标状态；
3. 3–7 个有顺序的阶段；
4. 具体执行；
5. 每一步为什么成立；
6. 风险与失败模式；
7. 回滚或保护措施；
8. observable evidence；
9. 专家心智模型。

只有存在真实 trade-off 时才给多套方案。

---

# 9. HTML 离线与公式策略

两套模板都必须首先满足：**核心内容离线可读**。

## 9.1 默认禁止 CDN

默认不得依赖：

- MathJax CDN；
- KaTeX CDN；
- Mermaid CDN；
- 外部字体；
- 前端框架 CDN。

除非用户明确允许联网依赖，否则不要加入这些资源。

## 9.2 数学公式优先级

公式按以下顺序处理：

1. 简单公式：原生 HTML，如 `<var>`、`<sub>`、`<sup>`；
2. 结构化公式：原生 MathML `<math>`；
3. 极复杂公式且无法可靠生成 MathML：保留可读的 TeX 源作为辅助文本，但不能让页面只剩裸 TeX。

LaTeX 风格模板中的“网格感”是视觉风格，不意味着必须运行 LaTeX 或 MathJax。

---

# 10. 视觉设计规范

## 10.1 lesson-template：交互优先，但避免 SaaS 卡片墙

必须：

- Hero 与正文使用同一个外层版心，左右边缘严格对齐；
- 教学正文使用深色 `--text/--ink`，灰色只用于辅助说明；
- 中文 H1 桌面端不要超过约 55px；
- 中文标题不使用负 `letter-spacing`；
- 字重只使用 400 / 600 / 700，避免 780/850/900 这类在中文字体中无意义的名义阶梯；
- 术语卡、事实卡和训练题允许卡片化，但章节本身不要每节都靠阴影制造层级；
- 知识卡片使用 `auto-fit/minmax`，3 个项目不能形成“2+1 大空洞”；
- 移动端目录必须收起为 `<details>`，不能先占满一整屏；
- 不使用无明显价值的 `backdrop-filter`；
- 风险样式使用语义明确的类名，例如 `.risk-card`，避免与 `.callout.risk` 冲突。

## 10.2 latex-learning-report：讲义优先

必须：

- 标题宽度用实际版心比例，不用 `16ch` 限制中文；
- 章节号使用固定宽度列，9→10→14 时正文标题左边缘不移动；
- `<details>` 使用自定义内置标记，三角不能跑到边框外；
- 元数据 `dt/dd` 基线对齐；
- 小字号辅助文字仍需有足够对比度；
- 字体栈优先选择中文衬线系统字体，再回退到通用 serif；
- 不打包、不分享字体文件。

---

# 11. 打印规范

## 11.1 lesson-template

打印时：

- 不对整个 `.section-card` 使用 `break-inside: avoid`；
- 允许长章节自然分页；
- 只对短卡片、表格、代码和单个题目使用合理的防断页策略；
- 深色代码块必须显式改成浅底深字，即使浏览器关闭“背景图形”也能读；
- `.question-number` 等依赖底色的白字元素，打印时改成深字 + 线框；
- 隐藏进度条、按钮和导航。

## 11.2 latex-learning-report

使用 A4 页面：

```css
@page {
  size: A4;
  margin: 18mm 17mm 20mm;
}
```

打印时提示和答案自动展开，屏幕按钮隐藏，内容应保持黑白可辨。

---

# 12. 渲染 QA：不能只读 CSS

在环境允许时，生成或修改模板后必须进行真实渲染检查。

至少检查：

1. 桌面：1280px 左右；
2. 手机：390px 左右；
3. A4 打印预览；
4. 长中文标题；
5. 章节号 9 / 10 / 14；
6. 代码块；
7. `<details>`；
8. 3 个知识卡片；
9. 公式；
10. 宽表格。

重点排查：

- Hero 与正文是否错位；
- 中文 H1 是否压满首屏；
- 移动端目录是否挡正文；
- 章节标题是否因两位数编号右移；
- details 标记是否跑出边框；
- 打印是否出现白字白底；
- 是否因 `break-inside: avoid` 留下大面积空白；
- 离线时公式是否仍可理解。

发现硬问题必须先修再交付。

---

# 13. 模板占位符与内容安全

生成 HTML 时：

- 替换所有 `{{PLACEHOLDER}}`；
- 删除不适用章节；
- 用户原始文本进行 HTML 转义；
- 不把用户输入直接拼进危险的 `innerHTML`；
- 不残留 Markdown 三反引号、TODO 或模板示例；
- 章节 ID 与目录一致；
- 代码中的 `<`、`>`、`&` 正确转义；
- 练习工作表中不得把成熟答案写入 DOM、注释、脚本变量或 `data-*` 属性后再隐藏。

---

# 14. GitHub 写入与 Pages 发布流程

默认目标：

```text
repository: ValentinoWang/Study_Skills
branch: main
archive: skills/case-driven-active-learning/examples/<slug>.html
publish: docs/lessons/<slug>.html
index: docs/index.html
pages base: https://valentinowang.github.io/Study_Skills/
```

操作顺序：

```text
生成 HTML
→ 选择稳定 slug
→ 写入 / 更新 examples/<slug>.html 作为 Skill 案例归档
→ 写入 / 更新 docs/lessons/<slug>.html 作为 Pages 发布副本
→ 读取 docs/index.html
→ 若首页没有该课程：新增课程卡片与相对链接 lessons/<slug>.html
→ 若已有该课程：更新对应卡片，禁止重复注册
→ 写入 main
→ 获取最终 commit SHA
→ 重新读取三个目标：examples、docs/lessons、docs/index.html
→ 验证首页 href 与课程文件路径一致
→ 查询最新 pages build and deployment
→ 确认 head_sha 覆盖最终 commit，且 status=completed、conclusion=success
→ 返回首页 URL + 课程 URL + commit SHA
```

页面 URL 规则：

```text
首页：
https://valentinowang.github.io/Study_Skills/index.html

课程：
https://valentinowang.github.io/Study_Skills/lessons/<slug>.html
```

不要把 GitHub blob URL 当作最终课程 URL。

不要默认创建分支或 PR。只有用户明确要求 code review / PR 时才走分支流程。

---

# 15. 禁止行为

禁止：

1. 一次甩几十个术语定义；
2. 用更多陌生术语解释陌生术语；
3. `/learn` 刚出题就公布答案；
4. 只讲操作不讲原理；
5. 把案例变成百科而不是决策问题；
6. 成熟方案没有风险与验证；
7. 只生成漂亮 HTML 但没有训练结构；
8. 默认引入 MathJax/KaTeX/Mermaid CDN；
9. 用 `16ch` 等不适合中文的标题宽度规则；
10. 让打印依赖背景色才能看清；
11. 用 `break-inside: avoid` 把每个大章节锁成不可分页卡片；
12. 把最终 HTML 只留在 sandbox 而不做 GitHub 同步；
13. 只归档到 `skills/.../examples/` 就宣称网页已发布；
14. 发布到 `docs/lessons/` 却不更新 `docs/index.html` 导航；
15. Pages deployment 未成功就返回“已经可以从站点看到”；
16. 在最终文档暴露内部推理草稿或隐藏思维链。

---

# 16. 最终成功标准

一次完整执行同时满足：

### 学习成功

用户能够解释核心概念、还原案例、识别风险、提出方案，并至少完成一次迁移判断。

### 解题成功

成熟方案有前提、步骤、理由、风险、回滚与验证证据。

### 视觉成功

- 桌面和 390px 手机可读；
- 中文标题不过度放大；
- lesson 的版心对齐；
- latex 的章节号对齐；
- details 标记在框内；
- 教学正文不是灰色次级文本；
- A4 打印不出现白字白底和大面积无意义空白；
- 离线时核心正文与公式仍可理解。

### 发布成功

必须同时满足：

- HTML 已归档到 `skills/case-driven-active-learning/examples/`；
- HTML 已发布到 `docs/lessons/`；
- `docs/index.html` 能从首页导航到课程；
- 三处修改已同步到 GitHub `main`；
- 返回可验证的最终 commit SHA；
- 最新 GitHub Pages deployment 覆盖该 commit 且成功；
- 最终回复返回可直接访问的首页 URL 与课程 URL。

# Learn → Apply → Fail → Hint → Solve → Reflect → Transfer → Publish

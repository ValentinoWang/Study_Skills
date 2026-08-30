---
name: case-driven-active-learning
description: >
  将包含陌生术语、专业概念、工程背景或行业知识的真实材料，转换成
  “最小知识学习 → 案例还原 → 主动做题 → 分级提示 → 实际答案 → 反思迁移”
  的干中学课程。默认生成交互式 HTML，并同步归档到 Study_Skills、发布到
  GitHub Pages、注册首页导航并验证最终发布页面。
---

# Case-Driven Active Learning

## 0. 核心目标

把真实材料变成一节可以主动练习的课程，而不是只做术语翻译或直接给结论。

```text
真实材料
→ 找真正问题与未知知识
→ 建立最小知识闭包
→ 还原对象 / 状态 / 约束
→ 用户先作答
→ Hint 1 / Hint 2 / Hint 3
→ 实际答案
→ 反思与迁移
→ 生成唯一 canonical HTML
→ 渲染 QA
→ 原样同步 examples/ 与 docs/lessons/
→ 注册 docs/index.html
→ GitHub Pages 部署
→ 对最终发布页做 smoke check
```

## 0.1 发布闭环是强制条件

除非用户明确要求仅本地生成，否则以下任何状态都不算最终完成：

- 只在聊天里给 HTML；
- 只写到 `/mnt/data`；
- 只写入 `skills/case-driven-active-learning/examples/`；
- 只写入 `docs/lessons/` 但首页没有入口；
- 仓库有文件但 Pages 没有部署成功；
- QA 的文件与最终发布文件不是同一份内容。

默认目标：

```text
repository: ValentinoWang/Study_Skills
branch: main
archive: skills/case-driven-active-learning/examples/<slug>.html
publish: docs/lessons/<slug>.html
index: docs/index.html
site: https://valentinowang.github.io/Study_Skills/index.html
```

最终必须验证：归档文件、发布文件、首页导航、commit SHA、Pages deployment。

---

# 1. 运行模式

## `/learn`：默认

课程顺序：

```text
ORIENT → LEARN → CONNECT → RECONSTRUCT → MAP → ATTEMPT
→ HINT 1 → HINT 2 → HINT 3 → FINAL ANSWER
→ REFLECT → TRANSFER
```

用户应先完成第一版作答，再逐级展开提示。

**最终一层必须是实际答案，不再把 Hint 3 当终点。**

静态 HTML 为了离线可用，可以把实际答案放在隐藏的 `#final-answer` 中；它必须默认不可见，只能在用户主动经过提示链并点击“查看实际答案”后显示。保护的是学习流程，而不是试图让浏览器源码保密。

## `/solve`

一轮直接完成术语、案例、推理、成熟解法、验证标准与迁移，并输出完整讲义。

## `/exam`

只给必要背景、题目、约束、评分标准与答题区。默认不显示提示和答案；用户请求后再生成答案稿。

---

# 2. 双模板架构

## 2.1 交互练习模板

```text
assets/lesson-template.html
```

用于 `/learn`。必须包含：

- 顶部学习进度；
- ① 材料概览；
- 核心术语；
- 概念图；
- 案例还原；
- 概念映射；
- 用户答题区；
- Hint 1 / 2 / 3；
- 最终实际答案；
- `localStorage` 保存学习状态。

## 2.2 结题讲义模板

```text
templates/latex-learning-report.html
```

用于 `/solve`、`/learn` 完成后的结题稿，以及长期归档 / A4 打印。

---

# 3. 顶部进度与章节 Checklist 必须同步

顶部默认 5 个进度键：

```text
orient  看懂材料
terms   理解术语
case    还原案例
attempt 完成作答
answer  查看答案
```

### 3.1 ① 章节必须有对应 Checklist

在“① 这段材料到底在说什么”正文末尾必须出现一个可勾选项，例如：

```text
☐ 我已经看懂这段材料的核心问题与关键状态。
```

它必须使用和顶部“看懂材料”**相同的 progress key：`orient`**。

用户勾选章节内 checkbox 时，顶部 checkbox 必须同步；反过来也一样。

### 3.2 其他关键阶段也应镜像

建议在术语、案例还原、作答阶段末尾分别放置同 key 的 checklist。顶部进度只按**唯一 key**计数，不能因为同一个 key 在页面出现两次而重复计数。

### 3.3 查看实际答案自动完成 `answer`

当 `#final-answer` 被主动展开时，自动把 `answer` 标记为完成，并同步顶部进度。

---

# 4. 最小知识闭包

核心术语通常 5–12 个。每个核心术语优先按五层解释：

1. 一句话直觉；
2. 严格定义；
3. 比喻 / 直观模型；
4. 比喻失效处；
5. 当前案例中影响哪个判断。

遵循：

```text
自然语言 → 结构关系 → 领域语言 → 严格定义
```

禁止用一串新的陌生术语解释一个陌生术语。

进入题目前，只保留 3–7 条真正需要记住的原则。

---

# 5. 案例还原

不要逐句翻译原材料。重构为：

1. 背景；
2. 关键对象；
3. 当前状态；
4. 已知事实；
5. 可以推断；
6. 尚不知道；
7. 关键风险；
8. 真正问题。

必须区分事实 / 推断 / 未知。

建立：

```text
概念 → 现实实例 → 影响判断
```

---

# 6. 把场景改造成训练题

训练题至少覆盖：

- 理解；
- 诊断；
- 风险；
- 方案；
- 验证。

思考脚手架：

```text
识别对象
→ 标注状态
→ 找差异和约束
→ 找不可逆风险
→ 确定第一保护目标
→ 设计降低不确定性的操作顺序
→ 定义可观察的成功证据
```

用户必须有明显的第一版作答区，不要让答案紧贴题目出现。

---

# 7. Hint Ladder：最后必须到实际答案

## Hint 1 · 方向

只指出应该关注哪个对象、变量或风险。

## Hint 2 · 结构

给出解决问题的阶段结构，不填关键决策。

## Hint 3 · 接近答案

给出接近执行层的提示，仍让用户自己完成最后判断。

## Final Answer · 实际答案

**这不是第四个模糊提示，而是实际答案。** 至少包含：

1. 问题本质；
2. 目标状态；
3. 3–7 个有顺序的阶段；
4. 具体执行；
5. 为什么这样做；
6. 风险与失败模式；
7. 回滚 / 保护；
8. 可观察验证证据；
9. 必要时给实际命令、公式、配置或示例。

按钮链应是：

```text
Hint 1 → 看 Hint 2
Hint 2 → 看 Hint 3
Hint 3 → 查看实际答案
```

不得出现“提示到最后仍然不给答案”的情况。

---

# 8. HTML 与视觉规范

核心内容必须离线可读。默认禁止 MathJax / KaTeX / Mermaid / 外部字体 / 前端框架 CDN。

交互页要求：

- Hero 与正文同版心；
- Hero meta 必须包含学习日期，见 8.0；
- 中文正文使用高对比深色文本；
- 中文 H1 桌面端不要过度放大；
- 移动端目录折叠；
- 卡片使用 `auto-fit/minmax`；
- 语义风险用明确 `.risk-*` 类；
- 进度 checkbox 与章节 checklist 清楚可点击；
- 最终答案可和提示区有明显视觉区分。

### 8.0 学习日期硬规则

`<slug>` 里的日期只存在于文件名和 URL，页面上看不见。每节课必须在 Hero meta 里显示学习日期：

```html
<span class="pill pill-date">学习日期<time datetime="YYYY-MM-DD">YYYY-MM-DD</time></span>
```

要求：

- 日期与 `<slug>` 末尾的 `YYYYMMDD` 一致；
- 必须用 `<time datetime>`，不能只写纯文本；
- 放在 meta-row 最后一位，样式用 `.pill-date`（比其他 pill 更弱），避免和领域/模式/难度这类分类标签混成一片；
- 同一日期要同步写进 `docs/index.html` 该课卡片的 `.meta`；
- 打印时保留日期，不要放进 `display:none` 的区域。

### 8.1 深色代码块硬规则

任何深色 `<pre>` 内的 `<code>` 必须显式取消 inline code 的浅色背景：

```css
pre code {
  padding: 0;
  background: transparent;
  color: inherit;
  border-radius: 0;
}
```

否则会出现“黑色代码块上每行文字带白色矩形背景”的视觉 bug。

打印时反向处理为浅底深字，但仍要求 `pre code` 背景透明。

---

# 9. 交互实现规则

同一个进度 key 可以在顶部与章节内出现多次，但必须同步：

```text
data-progress="orient"
```

逻辑必须：

- 按唯一 key 计算进度；
- 任一同 key checkbox 改变时同步其他同 key checkbox；
- 重置时同时清除所有镜像状态；
- 展开最终答案时自动完成 `answer`；
- 用户答题内容保存在 `localStorage`；
- Hint 2、Hint 3、Final Answer 默认 hidden。

---

# 10. Canonical Artifact：QA 与发布必须是同一份文件

这是强制规则。

```text
生成 canonical lesson.html
        ↓
真实渲染 QA
        ↓ PASS
同一份字节内容
   ↙             ↘
examples/      docs/lessons/
```

**禁止：**

```text
QA examples/A.html
→ 发布时重新手写 / 精简成 docs/lessons/B.html
```

如果发布版内容发生任何改变，必须重新 QA。

在条件允许时，验证归档版和发布版内容哈希一致；至少确认正文、CSS、JS 来自同一 canonical artifact。

---

# 11. 渲染 QA：不能只读 CSS

生成或修改后至少检查：

1. 桌面约 1280px；
2. 手机约 390px；
3. A4 打印；
4. 顶部进度与章节 checkbox 双向同步；
5. Hint 1 → 2 → 3 → Final Answer 的展开链；
6. Final Answer 展开后顶部 `answer` 自动勾选；
7. 深色 `pre code` 计算样式为透明背景；
8. 中文长标题；
9. 宽表格；
10. 最终答案中的代码块和 callout；
11. Hero 学习日期存在，且与 `<slug>`、首页卡片一致。

发现硬问题必须修复后重新渲染。

---

# 12. 发布后 QA

GitHub Pages deployment success 只说明部署成功，不等于视觉正确。

发布后必须继续确认：

- `docs/index.html` 能导航到课程；
- 最终 Pages URL 可访问；
- 最终发布页仍包含正确 CSS/JS；
- 若能做浏览器 smoke test，优先直接检查最终发布页；
- 如果最终发布文件和 QA 文件 hash 不同，状态不得标记为 PUBLISHED。

状态示例：

```text
LOCAL_ONLY / GITHUB_SYNC_BLOCKED
GITHUB_SYNCED / PAGES_DEPLOY_BLOCKED
PUBLISHED / QA_BLOCKED
PUBLISHED / VERIFIED
```

---

# 13. GitHub 写入流程

默认：

```text
repository: ValentinoWang/Study_Skills
branch: main
```

流程：

```text
生成 canonical HTML
→ QA
→ 更新 examples/<slug>.html
→ 用完全相同内容更新 docs/lessons/<slug>.html
→ 更新 docs/index.html（若尚未注册）
→ 获取 commit SHA
→ 重新读取三个位置
→ 检查 Pages deployment
→ 返回首页 URL + lesson URL + commit
```

不要默认创建分支或 PR，除非用户明确要求。

---

# 14. 禁止行为

禁止：

1. 一次甩几十个术语定义；
2. 用更多陌生术语解释陌生术语；
3. `/learn` 一进入题目就直接展示最终答案；
4. Hint 3 之后没有实际答案；
5. 顶部进度与章节 checklist 使用不同状态、互相不同步；
6. 同 key checkbox 被重复计入进度；
7. 深色 `<pre>` 继承 inline `<code>` 的浅色背景；
8. QA 一份文件、上线重新生成另一份；
9. Pages deployment success 就直接宣称视觉验收通过；
10. 只讲操作不讲原理；
11. 成熟方案没有风险、回滚和验证；
12. 默认引入外部 CDN；
13. 把最终 HTML 只留在 sandbox；
14. 暴露内部隐藏思维链。

---

# 15. 最终成功标准

### 学习成功

用户能解释核心概念、还原案例、识别风险、先完成一次判断，再通过提示与答案修正自己的模型。

### 交互成功

- ① 底部有 checklist；
- checklist 与顶部进度双向同步；
- Hint 1 → 2 → 3 → 实际答案；
- 查看实际答案后进度同步更新；
- 本地保存正常。

### 视觉成功

- 桌面与 390px 手机可读；
- 深色代码块没有白色文字背景块；
- A4 打印可读；
- 最终答案布局清楚。

### 发布成功

- examples 与 docs/lessons 来自同一个 canonical artifact；
- 首页能导航；
- main 上文件存在；
- Pages 部署成功；
- 最终发布页经过 smoke check。

# Learn → Apply → Hint → Answer → Reflect → Transfer → Publish

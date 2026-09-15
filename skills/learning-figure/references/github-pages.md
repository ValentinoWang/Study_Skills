# GitHub Pages 图形交付合同

## 先区分三个渲染面

GitHub 的 Markdown 预览、Pages/Jekyll 构建、用户浏览器不是同一个渲染器。
仓库 README 的 Mermaid/数学语法能显示，不证明课程 Pages 自动支持它。
GitHub Pages 发布静态 HTML/CSS/JS；Python 绘图必须在发布前运行，或由明确配置的构建任务运行。
原生 branch-based Pages 不会因为仓库多了一个 Python 脚本就自动执行它。

默认静态优先：基础图、定义、数据和结论不依赖浏览器 JavaScript、CDN、第三方字体服务或 API Key。
需要交互时，只做静态内容之上的渐进增强；禁用脚本仍能学习，tooltip 不能成为唯一信息入口。

## SVG 的两条边界

v2 机制图：受控 inline SVG，继续使用 `learning-figure.html` 和全对象几何检查，ID 带课程/图/变体前缀。
数据图或第三方生成 SVG：用 `<img>` 隔离，不直接拼进页面 DOM，不让全局 CSS 改写图中文字/路径。
第三方 SVG 仍须检查来源、内容、资源依赖和安全性；`<img>` 不等于任意文件都已安全审阅。
外部 SVG 不能依赖父页面 CSS/字体或图内脚本工作；复杂图的 alt 之外另提供默认可读的说明和同源数据。

`render-chart.py` 的 SVG 不含在线依赖，文字路径固定；HTML 定义/表格保留可访问文本。
它含 Matplotlib 的路径和裁切元素，不能通过增加“忽略 path”规则塞进 v2 检查。

## Publisher 接入：不新建第二套课程发布架构

从已生成产物拷贝：

```text
convergence.svg + convergence.source.json → docs/assets/figures/figure-lab/
learning-chart.css                        → docs/assets/css/learning-chart.css
convergence.figure.html                   → docs/_includes/learning-charts/convergence.html
```

在使用该图的 layout 的 `<head>` 加一次：

```liquid
<link rel="stylesheet" href="{{ '/assets/css/learning-chart.css' | relative_url }}">
```

在 canonical supplement 的定义区后插入，再由 `build-lessons.py` 同步镜像：

```liquid
{% include learning-charts/convergence.html %}
```

导出器已经对 include 内的资源路径应用 `relative_url`。
`--web-path /assets/figures/figure-lab` 不包含 `/Study_Skills`；由 Jekyll 的 baseurl 加前缀。
不要写死 `https://.../Study_Skills`、`/assets/...` 浏览器根路径，或把 baseurl 加两次。
文件名大小写必须一致。`_includes` 是构建输入，不是供 `<img>` 直接请求的公开目录。

以上是接入步骤，不是已经接入的声明。当前 chart-kit 不自动登记/修改课程 manifest。
每次实际接入须记录课程 slug、canonical 插入位置、源模型路径、产物摘要、公开资源路径和独立验收结果；
不要借用 `manifest.figures`/v2 守门的 PASS 证明 `.lf-chart`。新增登记机制须同时实现消费者和红绿测试，不能只加空字段。

## 响应式与打印

`assets/chart.css` 只作用于 `.lf-chart`，不覆盖页面的普通 table、svg、MathML。
宽屏显示完整图与同源数据入口；窄屏默认显示定义、结论、完整点值，原生 details 可展开完整图。
完整图保留可读宽度，只允许图容器横向滚动；不能把整个网页撑宽或把字号缩到不可读。
图形之外保留尺寸/比例，检查懒加载和折叠展开后是否正常加载。

浅色图形使用显式浅色容器，不用 CSS invert 冒充深色主题。打印默认展开同源文字/数据，
不要让整张长 figure 强制 break-inside:avoid；打印媒体通过不等于 A4 分页通过。

## 最终验收

在实际 Jekyll `_site` 或同提交的 Pages artifact 中检查：路径/大小写、资源能加载、
图和 CSS 被发布、定义先出现、桌面 1280 与窄屏 390/320、无 JS、键盘展开、无根级横向滚动、
图注/单位/数据完整、打印媒体和真实分页、公开 URL 内容是否对应目标提交。

离线预览只能报告离线范围。静态预览、Jekyll 构建、网络读回与独立视觉审阅不能互相替代。
原有 validation workflow 不覆盖 chart-kit 的科学语义；也不是原生 Pages 部署的前置阻断器。

## 官方依据（核查日期：2026-09-15）

- [GitHub Pages 静态托管与项目子路径](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [GitHub Markdown 图形的支持范围](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)
- [Pages 与 Jekyll](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/about-github-pages-and-jekyll)
- [Jekyll relative_url](https://jekyllrb.com/docs/liquid/filters/)
- [SVG 作为 image 的限制](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image)

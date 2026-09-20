# 科学数据图与数学图的网页路线

## 已可运行的导出器

`scripts/render-chart.py` 接受一个 JSON 模型，只实现 `line`、`scatter`、`bar`。
最多三系列、每系列三十点是这个小型教程组件的实现范围，不是科研绘图的一般限制。
复杂任务先设计专用绘图代码和审阅方案，不删数据来挤进模板。

输入字段（准确结构见 `examples/convergence.chart.json` 和 `validate()`）：

| 字段 | 要求 |
|---|---|
| version / id / kind | version=1；安全英文 slug；已支持图型 |
| question / takeaway / boundary / reading_order | 问题、结论、适用边界、读图顺序 |
| x / y | label、unit、meaning；无量纲也要写明 |
| series | label、meaning、x、y；中文图例含义默认显示 |
| evidence.type | teaching-example 或 measured |
| evidence.source | 明确来源；结构有效不代表来源已核实 |
| sample_size / replicate_unit | 实测必须有正整数样本量及重复单位；点数不自动当样本量 |
| aggregation / transformations | 聚合口径；显式变换列表，无变换写 [] |
| uncertainty | 当前导出器只接受 not-estimated，不冒充支持区间 |

数值必须有限。缺测/NaN、乱序折线、重复系列、字段缺失、未知参数、路径穿越返回失败/受阻。
柱图类别必须唯一且同序，基线包含零。不会自动平滑、重排数据、拟合趋势或裁切范围。

## 单一来源与输出

教学源模型放在 `figures/<lesson>/<id>.chart.json`；示范模型放 `examples/`。
实测原始数据另外保留为只读输入；模型中的点值必须有可复核的提取/变换依据。
不手改导出的 SVG、表格、图注或 source.json；修源模型再完整重建。

输出六项：`<id>.svg`、`<id>.source.json`、`<id>.figure.html`、
`<id>.preview.html`、`<id>.report.json`、`learning-chart.css`。
`--check` 在相同环境重新生成并比较字节；字体/工具升级产生漂移要审阅，不能重标为通过。
报告保存模型、脚本、CSS、运行版本和逐产物摘要。发布时仅拷贝被报告覆盖的对应文件。

SVG 的文字转为路径，避免客户端字体替换改变绘图布局；这是图形路径，不是字体文件。
文字的可访问表示在 HTML 的轴/图例定义、alt、结论与完整数据表中。
本地字体缺字直接受阻，不用方框替代中文后继续发布。

## 运行与接入

```bash
python -m pip install -r skills/learning-figure/scripts/requirements-chart.txt
python skills/learning-figure/scripts/render-chart.py \
  skills/learning-figure/examples/convergence.chart.json \
  --out /tmp/learning-chart --web-path /assets/figures/figure-lab
python skills/learning-figure/scripts/render-chart.py \
  skills/learning-figure/examples/convergence.chart.json \
  --out /tmp/learning-chart --web-path /assets/figures/figure-lab --check
python skills/learning-figure/scripts/test-render-chart.py
```

离线浏览器预检（安装仓库的 Playwright 依赖后）：

```bash
python skills/learning-figure/scripts/check-chart-preview.py /tmp/learning-chart \
  --id convergence --out /tmp/learning-chart-evidence --offline
```

该检查只检验独立导出预览，报告绑定导出摘要并保留桌面、390/320、无 JS、打印媒体截图；
不会将它写成真实 Jekyll 构建、公开 URL 或分页 PDF 验收。

查看 `convergence.preview.html`；不要直接打开带 Liquid 的 `convergence.figure.html` 当作 Pages 预览。
导出器不修改 lesson-manifest、Pages 配置或课程正文；接入方式见 `github-pages.md`。
当前 `manifest.figures` 只接收 v2 `.figure.json`，不要把 chart JSON 塞进去或伪装成 schematic。
导出报告里 scientific_review、browser_layout、pages_build 等保持 NOT_RUN，由对应独立证据补足。

## 更复杂的科学/数学图

这部分是选型与审阅指南，不是导出器已实现的图型。

函数/几何图：保留公式、定义域、参数、采样方式；先解释符号，不能从图片反推证明。
直方图/密度图：保留原始样本、分箱边界/带宽；不能通过调整分箱隐去结构。
热力图：标明行列含义、归一化、色标及缺测；比较图使用一致色标。
置信区间/误差条：区分 SD、SE、CI，写明估计量、样本量和独立重复单位。
复杂方法图：先确认节点/边与算法一致，再用构建期 Mermaid/Graphviz/D2 等输出。

可按任务编写 Matplotlib 等专用脚本，但必须另附数据、解释、可见替代、生成脚本和实际页面验收；
不能因为它生成了 SVG 就套用 v2 的自动几何 PASS。数据密集图可栅格化主体、保留清晰标签；
网页优先可读性和可访问性，不机械追求“全部矢量”。

参考：[Matplotlib 输出后端](https://matplotlib.org/stable/users/explain/figure/backends.html)。

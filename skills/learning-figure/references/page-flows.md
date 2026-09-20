# Pages 原生流程图合同

## 为什么增加这一类图

`sequence / comparison / ownership` v2 SVG 适合需要精确连线、对象归属和几何验收的机制图；科研 chart 适合定量趋势和比较。
但很多教程只需要回答“按什么顺序理解”“故障依次经过哪些门”“一条链路的责任边界在哪里”。
这类 2–7 步线性结构若硬画 SVG，会增加坐标、字体和窄屏维护成本，却没有带来新的教学精度。

因此 page-flow 使用 **JSON 语义模型 → Jekyll 构建期 HTML → 作用域 CSS**：不依赖客户端 JavaScript、CDN、在线字体或图片生成 API。
这不是 v2 SVG 的替代，而是第三种受控渲染面。

## Canonical model

人工来源：

```text
skills/learning-figure/page-figures/<lesson>/<id>.flow.json
```

模型必须满足 `schema/page-flow-v1.schema.json`：

- `question`：这张图回答什么问题；
- `reading_order`：读者按什么顺序看；
- `takeaway`：读完应该得到什么结论；
- `boundary`：图不能证明什么；
- `evidence_type`：`schematic` 或 `teaching-example`；
- `steps`：2–7 个步骤，每步有稳定 id、label、detail、tone。

不得把实测曲线、置信区间、复杂拓扑或需要精确边语义的图伪装成 page-flow。

## Manifest 与页面槽位

在 `skills/learning-page-design-publisher/lesson-manifest.json` 中登记：

```json
{
  "page_figures": [
    {
      "id": "example-flow",
      "model": "skills/learning-figure/page-figures/example/example-flow.flow.json",
      "slot": "after-map"
    }
  ]
}
```

当前标准 `lesson` layout 支持：

- `after-orient`
- `after-map`
- `after-case`
- `after-mapping`

选择原则是**定义先于图、图紧跟它解释的正文**。不要为了统一外观把图集中到单独的“图库”章节。

`tools/build-lessons.py` 调用 `tools/learning_figures/page_flows.py`：校验 schema 与路径，生成
`docs/_data/learning_page_figures/<lesson>.json`，并在 `--check` 时比较字节漂移与孤儿数据。
Jekyll 通过 `learning-page-figure-slot.html` 和 `learning-page-figure.html` 构建语义 HTML。

## 响应式策略

- 2–5 步：桌面按线性卡片 + 箭头展示；
- 6–7 步：桌面切成三列网格，编号保留阅读顺序，避免把正文压成细长竖列；
- <=820px：单列卡片，箭头改为向下；
- 打印：纵向步骤，隐藏装饰箭头，允许 figure 跨页但单个步骤不拆页。

正文、步骤说明、结论和边界默认不少于 16 CSS px；颜色只做第二编码，步骤编号和文字承担主要语义。

## 验收边界

静态/构建：

```bash
python tools/build-lessons.py --check
```

真实 Jekyll candidate：

```bash
python tools/check-learning-page-flows-render.py \
  --built-site /path/to/_site \
  --output /path/to/page-flow-evidence
```

浏览器检查覆盖 1280、390、320 无 JS 与 print-media：图唯一、步骤数量/文字与模型一致、正文 >=16px、页面根无横向溢出、结论和边界存在，并保存截图。

这些检查不等价于公开 Pages readback、分页 PDF 审阅或独立视觉审阅；报告必须分别保留 NOT_RUN / BLOCKED 状态。

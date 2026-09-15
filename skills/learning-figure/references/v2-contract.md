# v2 模型与生成合同

版本 2.0.0；设计基线 2e7739d9b8a689d7f1b1970927bb3bbedd404beb。

## 输入

`schema/figure-v2.schema.json` 是结构规则，`tools/learning_figures/core.py` 是共享验证/生成实现。
模型与 manifest 分离：manifest 只记录 id、model、section_id、after_id。
model 保存 question、takeaway、reading_order、boundary、bindings、图型事实。
禁止 authored x/y；派生布局不能作为第二手工真相。

Bindings 每项都有 label、definition_id、meaning、source、example。正文必须有唯一可见定义，且在图前。
机械检查证明 ID、值和顺序，不证明解释质量；图题、无 data-term 的专业词仍需教学审阅。

## 图型

- sequence：2–4 个 actor，按事件列表展示；after 是已知先后约束，列表次序不是现实并发的唯一顺序。
  message 带 from/to、label、payload；compare_write 是单步比较并写入；atomic_credit 是教学原子记账模拟。
- comparison：同一字段的 before/after，保持两边逐行对应。
- ownership：显式父组和子对象。只支持声明的一层分组，不假装支持任意层级。

模拟不是支付 SDK：compare_write 在同一步检查与更新；atomic_credit 在同一步提交去重键、分录、余额。
通知 event_id 与 business_key 分离。提交前失败不写任何效果；提交后响应丢失不会回滚已提交结果。
同一业务换通知编号仍不重复；不同购买同金额不会被错误去重。结果由模型计算，不在图注里另造一份数字。

## 文字与布局

生成前用浏览器 SVG getBBox 测 Noto Sans CJK SC 与 Noto Serif CJK SC，取两者占位上界。
整词/ID不截断，中文可换行；水平节点有明确内边距。消息和状态结果使用独立事件行。
当前实现是确定性换行与尺寸扩展，不是通用自动避障优化器；仍放不下则硬失败，留给作者拆分图。

所有节点/文本/连线/箭头/辅助泳道从 scene 输出，并同时生成预期清单。
派生输出为 canonical 目录的 SVG、public SVG、Jekyll inline SVG 以及 docs/_data/learning_figures 数据。
重建比较字节；model、renderer、profile、schema 摘要变化会使旧数据失效。字体不同导致漂移也应显式处理。

## 页面

章节内保留 `<p id="lf-slot-...">`，紧接共享 include。禁止按标题文案运行 JS 搬图。
图前定义必须默认可见；图的三个 SVG 副本必须一致。手机与打印来自同一 trace；完整图由原生 details 打开。
SVG ID 按课程、图和 full 变体加前缀。文本用 HTML/XML escape，不接受导入脚本和外部资源。

## 来源适配（不复制论文专属规则）

参考仓库 ValentinoWang/Harness_Engineering：
- Paper/Paper_Figure_Harness/skills/paper-figure-sentinel/SKILL.md，核查 blob 7b4c2a70c996e22fe4442a75cb19edc1e4aed3e0。
- Paper/Paper_Figure_Harness/harnesses/paper-figure-harness.md，核查 blob 64010b001360ed5349a0e009f03889cfc20de0ff。
- Projects/StyleFilter/skills/nature-figure/SKILL.md，核查 blob eda5ae7f33702f992717c30b78c548afb1592e85。

复用图意、可测安全距离和红绿反例；不强制教学图先选 Python/R，不继承论文毫米尺寸和小字号。
更新上游前比较固定版本，不在构建时拉取浮动 main 改变验收标准。

# QA、证据与发布边界

## 分层状态

模型/静态 → 覆盖/几何 → 页面 → 视觉审阅 → 分页打印 → 部署读回，分别记录。
状态 PASS、FAIL、BLOCKED、NOT_RUN、带理由 NOT_APPLICABLE。不能用平均分抵消遮字。

浏览器入口默认本地 HTTP 上的真实 Jekyll artifact；导航被禁时允许显式 --offline。
离线模式把原 HTML 与同一 artifact CSS 字节装入 DOM，报告 transport；不验证网络/CSP/公开缓存。
字体必须可解析到规定的 Noto 家族，生成时测 Sans 与 Serif 上界。不得将字体文件上传给用户。

默认 Chromium 矩阵：1280、1440、390、320无JS、1280后备Serif、794打印媒体。
手机默认同模型步骤，可展开完整图；打印媒体不是实际分页PDF。页面脚本错误、丢图、重复ID、
图先于定义、正文横向溢出都报告失败。截图只覆盖实际候选，visual_review 默认 NOT_RUN。

WebKit可用 `--engine webkit`；环境不可用必须记录 BLOCKED，不等于真实iOS Safari已验收。
技术检查不是人工接受；视觉模型的审阅可注明 agent-visual-review，不能伪造用户签字。

## 独立审阅与封存

审阅JSON需 reviewer、evidence、visual_review=PASS、print_review=PASS、report_sha256。
审阅前必须看实际截图/分页PDF；不能由测试入口自动生成这些结论。

```bash
python tools/seal-learning-figure-release.py --site /path/to/site \
  --report /path/to/render/report.json --review /path/to/review.json \
  --output /path/outside/site/seal.json
```

封存检查报告非空全部通过、审阅绑定报告、页面摘要不变，并输出所有产物文件摘要。
封存状态 SEALED_NOT_DEPLOYED；不进行自动部署，不代替用户验收。任何产物变化要重验。

## CI与真实部署

`.github/workflows/learning-figures-v2.yml` 在main/PR做静态、回归、Jekyll构建和浏览器检查，保留失败证据。
它不修改仓库Pages设置；现有branch-based Pages可能独立运行。并行验证不等于部署前闸门。
自动发布强门需管理员把同一已验证artifact串到deploy-pages，本改动不请求更高权限，不宣称已配置。
远端任务失败应查步骤/日志/annotations；无日志只记原因未知，不删除workflow后说问题解决。

公开读回要核对可见图、模型摘要及资源；只读源码/ZIP无法证明用户网络看到什么。
若环境无法打开公开地址，明确公开读回BLOCKED，并提供精确提交和artifact证据。

## 可复现环境

依赖在 tools/learning-figures-requirements.txt；工作流固定Ubuntu、Python和Jekyll版本。
字体和浏览器仍可能变化，造成生成漂移应检查原因，不批量更新截图基线。
参考：W3C SVG2与WCAG2.2复杂图/重排；Playwright test-snapshots；Stripe webhooks重复事件规则。

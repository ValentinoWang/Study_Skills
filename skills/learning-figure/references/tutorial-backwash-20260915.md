# 2026-09-15 教程绘图回洗

本轮目标不是增加图片数量，而是找出“正文已经有完整概念，但缺一张能压缩认知负担的结构图”的课程。

## 已选择并接入

| 课程 | 缺口 | 新图 | 插入位置 | 路线 |
|---|---|---|---|---|
| `agent-development-mcp-memory-constrained-tools-20260915` | MCP / Memory / 参数约束在文字中分开解释，缺少一次 Agent 动作的共同运行环 | `agent-runtime-loop` | `after-map` | page-flow |
| `sub2api-hong-kong-ingress-network-path-20260910` | 核心论点是“入站与出站是两条不同边”，文字很清楚但缺路径总览 | `hk-ingress-path` | `after-orient` | page-flow |
| `tencent-cloud-dns-icp-mainland-origin-20260831` | DNS/TCP/TLS/HTTP/App/CORS/合规层次多，读者容易把最终症状都归因于 DNS | `domain-request-gates` | `after-orient` | page-flow |

三张图都只重组课程原有概念，不新增实验数字，不把条件性结论写成事实。

## 本轮明确不重复绘制

- `frontend-fast-feedback-pipeline-20260910`：课程已有“五级反馈模型”手写 SVG，新增另一张同义流程图只会重复。
- `software-delivery-lifecycle-ai-coding-20260910`：已有 Delivery Lifecycle 总图，当前优先事项应是以后迁移手写 SVG 到受控模型，而不是叠加新图。
- `software-engineering-two-hour-primer-20260913`：已有 `state-to-view`、`optimistic-lock-race`、`idempotent-webhook` 三张 v2 机制图，并且有完整几何验收链。
- `cadenvo-generation-pipeline-20260915`：长讲义使用专用 layout 与 supplement；若后续回洗，应先按章节识别精确连接关系，再决定 v2 sequence/ownership，而不是把整条复杂生成链压成 7 步卡片。
- `git-three-state-divergence-20260831`：最有价值的图是 commit DAG / refs 分叉，不属于线性 page-flow；后续应增加受控 DAG/graph 图型，不能用线性箭头歪曲祖先关系。

## 下一批优先级

1. 为 `learning-figure` 增加 DAG / dependency graph 受控图型，再回洗 Git 三状态课程。
2. 审计现有手写 `<svg class="diagram">`，优先迁移那些承担关键推理、但目前只有 aria-label 没有结构化模型的图。
3. 有真实测量数据的网络/性能课程再使用 chart-kit；没有真实数据时禁止为了“科研感”构造性能曲线。

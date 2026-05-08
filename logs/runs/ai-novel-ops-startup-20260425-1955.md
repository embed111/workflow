# AI 小说盈利项目起步运营启动记录

- created_at: `2026-04-25T19:55:00+08:00`
- operator: `codex-ai-novel-ops-startup`
- preference_ref: `state/user-preferences.md`

## 目标
- 让 `project-ai-novel-profit` 从“项目已创建 / startup ready”进入真实起步运营。
- 将用户新增要求纳入首轮 PM 任务：`novel_project_pm` 必须探索变现渠道，后续账号接管要先定义安全边界和运营节奏。

## 当前 API 与运行机制核对
- `GET /healthz`: 可读。
- `GET /api/status`: 服务在线；派发后出现真实 running。
- `GET /api/runtime-upgrade/status`: `current_version=20260425-181610`，无更新候选，无 ghost running。
- `GET /api/projects?include_archived=true`: `project-ai-novel-profit` 存在于 registry，`lifecycle_state=active`。
- `GET /api/schedules`: 当前没有 AI 小说项目自己的 enabled/future schedule。
- `POST /api/assignments/asg-20260327-223335-b79f27/nodes`: 已创建项目运营首轮节点。
- `POST /api/assignments/asg-20260327-223335-b79f27/dispatch-next`: 客户端超时，但审计与 run 文件证明后台已派发。

## 已创建节点
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-20260425-ai-novel-ops-kickoff-01`
- node_name: `AI Novel Ops Kickoff 01`
- assigned_agent_id: `novel_project_pm`
- project_id: `project-ai-novel-profit`
- priority: `P0`
- expected_artifact: `ai-novel-ops-kickoff-01.md`
- problem_type: `project_operations_startup`
- method_card_id: `profitability-gate`

## 任务合同
本轮要求 `novel_project_pm` 交付 Markdown 运营起步报告，至少覆盖：
- startup verdict
- monetization channel matrix
- account takeover checklist and security boundaries
- first 14-day operating plan
- first writing direction brief
- cost and stop-loss gate
- next dispatch plan

明确禁止：
- 没有阈值的泛泛鼓励
- 忽略变现渠道
- 要求把账号密钥写入仓库或日志
- 未定义单位经济前启动高频 7x24
- 未做题材/渠道/商业判断前直接写正文

## 运行证据
- create_node 审计：`aaud-20260425-194505-24a8a0`
- dispatch 审计：`aaud-20260425-194906-d2ae97`
- run_id: `arun-20260425-194649-71bf4e`
- run_path: `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260425-194649-71bf4e/run.json`
- events_path: `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260425-194649-71bf4e/events.log`
- observed_status: `running`
- provider_pid: `7644`
- provider_process: `node.exe C:/Users/jmqj/AppData/Roaming/npm/node_modules/@openai/codex/bin/codex.js`
- latest_observed_event: `turn.started` and follow-up command events at `2026-04-25T19:52:34+08:00`

## 注意事项
- `POST` 客户端超时不等于失败；本轮 create/dispatch 都以文件与 audit 真相为准。
- 节点文件一度显示 `ready` 且缺 `run_id`，但 audit/run 真相已证明真实派发；后续应继续关注 node/run 读面一致性。
- 项目自己的持续接力 schedule 尚未形成；应等首轮 PM 交付后，按报告里的 handoff interval 建立或调整项目级接力。

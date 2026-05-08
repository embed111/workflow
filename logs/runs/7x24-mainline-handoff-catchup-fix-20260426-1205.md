# 7x24 主线 handoff catch-up 修复记录 2026-04-26 12:05

- preference_ref: state/user-preferences.md
- delta_observation: 用户再次通过 token 停止消耗发现 7x24 掉棒；本轮确认 durable handoff 表已经写入 `scheduled`，但 rolling once schedule 被通用 exhausted-once repair 投影为停用，且错过命中分钟后缺少 catch-up trigger。
- delta_validation: 下一轮继续观察 `node-sti-20260426-69f6e98e / arun-20260426-113000-70560f` 终态后是否自动续挂，并在 prod apply `20260426-120310` 后复核主线 missed-once catch-up 逻辑生效。

## 现场恢复
- 当前 live 已恢复为真实 running：
  - ticket: `asg-20260327-223335-b79f27`
  - node: `node-sti-20260426-69f6e98e`
  - run: `arun-20260426-113000-70560f`
  - provider_pid: `44148`
- `2026-04-26 12:04 +08:00` 复核：
  - `/api/status`: `running_task_count=1 / queued_task_count=0 / active_agent_count=1`
  - `/api/runtime-upgrade/status`: `current=20260426-012259 / candidate=20260426-120310 / candidate_is_newer=true / running_task_count=1 / ghost=false / can_upgrade=false`
  - 未直接 apply `prod`，等待正式环境空窗或用户明确指令。

## 根因
- `assignment_mainline_handoffs` 能把上一轮终态记录成 `scheduled`，但 schedule 的 once 时间点如果被 worker 错过，通用 `_repair_schedule_plan_truth()` 会看到：
  - once-only schedule 无未来 projection
  - latest trigger 已终态
  - 于是把 schedule 投影为 `enabled=false`
- 这条规则对普通一次性计划是正确的，但对 `[持续迭代] workflow` 是错误的；主线不能因为错过某一分钟就退出 active 视角。

## 修复
- `.repository/pm-main/src/workflow_app/server/services/schedule_query_runtime.py`
  - 新增自迭代 schedule 判定。
  - 自迭代 schedule 不参与通用 exhausted once retirement。
- `.repository/pm-main/src/workflow_app/server/services/schedule_trigger_runtime.py`
  - `run_schedule_scan()` 对 `[持续迭代] ...` 支持 missed once catch-up。
  - 如果 `next_trigger_at <= now` 且对应 once trigger 尚未命中，下一次 scan 会按原计划时间补 `trigger_hit`。
- `.repository/pm-main/scripts/acceptance/verify_assignment_mainline_handoff_outbox.py`
  - 增加红灯场景：`scheduled handoff -> missed once minute -> detail/list/preview 仍 active -> scan catch-up trigger`。

## 验证
- 红灯复现：
  - `.repository/pm-main/.test/20260426-114906-694/report.md`
- 绿灯验证：
  - `.repository/pm-main/.test/20260426-115016-818/report.md`
  - `.repository/pm-main/.test/20260426-115028-124/report.md`
  - `.repository/pm-main/.test/20260426-115044-025/report.md`
  - `.repository/pm-main/.test/20260426-115101-199/report.md`
  - `.repository/pm-main/.test/20260426-115122-758/report.md`
  - `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260426-115940.md`
- test 部署与候选：
  - commit: `df8b4f9 fix(schedule): 防止持续迭代主线错过触发后被一次性计划修复误关`
  - `pm-main` 与 `../workflow_code` 已对齐到 `df8b4f9`
  - `test/prod candidate=20260426-120310`
  - deploy report: `.running/control/logs/test/deploy-20260426-120310.json`
  - candidate: `.running/control/prod-candidate.json`

## 后续
- 当前 `prod` 仍有真实 running 主线，不能直接升级。
- 等 `running_task_count=0` 后，由 supervisor idle watcher 或用户明确指令再 apply `20260426-120310`。
- 下一棒终态后重点看：
  - handoff 是否继续写入 `scheduled`
  - schedule 是否保持 `[持续迭代] workflow` active
  - 若错过 once 分钟，下一次 scan 是否补出 trigger

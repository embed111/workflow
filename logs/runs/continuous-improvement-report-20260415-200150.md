# Continuous Improvement Report

- generated_at: `2026-04-15T20:01:50+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260415-846e619f`
- active_version: `V3`
- version_transition_decision: `stay(V3)`
- memory_ref: `.codex/memory/2026-04/2026-04-15.md`

## 本轮结果
- 我修复了 assignment 在 `agent_registry` 缺行或 `discover_agents` 不可用时会把 `workflow` 主线打成 `assignment_agent_workspace_missing` 的脆弱点。
- 我把 execution worker thread 的启动移到 dispatch lock 释放之后，并新增 probe 锁住这条时序。
- 我把 `V3` 的 PM 验收资产追平到当前 active 版本：补了 `V3` 需求映射矩阵、放宽 snapshot 对 `继续保持` 句式的识别、让版本看板验收不再硬编码 `V2 -> V3`。
- 代码已在 `.repository/pm-main` 提交为 `3a585aa`，并通过 `../workflow_code` fast-forward 收口；`test/prod candidate` 已刷新到 `20260415-200051`。

## 验证
- line budget: `.repository/pm-main/.test/20260415-193313-333/report.md`
- workspace fallback probe: `.repository/pm-main/.test/20260415-193423-957/report.md`
- thread start timing probe: `.repository/pm-main/.test/20260415-193544-763/report.md`
- stale recovery dispatch probe: `.repository/pm-main/.test/20260415-193637-542/report.md`
- current-version snapshot probe: `.repository/pm-main/.test/20260415-195101-143/report.md`
- TC-PM-003: `.repository/pm-main/.test/20260415-195124-214/report.md`
- version board view: `.repository/pm-main/.test/20260415-195149-169/report.md`
- active version matrix: `.repository/pm-main/.test/20260415-195206-316/report.md`
- full workflow gate: `.repository/pm-main/.test/20260415-195229-242/report.md`
- test/prod candidate deploy: `.running/control/logs/test/deploy-20260415-200051.json`

## Live 真相
- `/api/status`: `active_version=V3 / lane=功能开发 / lifecycle_stage=开发实现 / running_task_count=1 / queued_task_count=0`
- `/api/runtime-upgrade/status`: `current_version=20260415-155232 / candidate_version=20260415-200051 / candidate_is_newer=true / drain_active=true / can_upgrade=false`
- `/api/schedules`: 当前出口为 `mainline running(node-sti-20260415-846e619f / arun-20260415-191128-c81c8c)` + `patrol future(2026-04-15T20:20:00+08:00)`
- 发布边界: `root_sync_state=clean_synced / workspace_head=code_root_head=3a585aa / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=-`
- next_push_batch: `等待 candidate 20260415-200051 进入 live 后补 current-version smoke`

## V3 需求判断
- `V3-R1=status=in_progress / progress=55% / eta=2026-04-16 / timeout=未超时`
- `V3-R2=status=in_progress / progress=65% / eta=2026-04-16 / timeout=未超时`
- `V3-R3=status=planned / progress=25% / eta=2026-04-18 / timeout=未超时`
- `V3-R4=status=in_progress / progress=50% / eta=2026-04-16 / timeout=未超时`
- `V3-R5=status=planned / progress=30% / eta=2026-04-17 / timeout=未超时`
- `next_activation_candidate=V4 / next_activation_ready=false / switch_blockers=V3-R1~V3-R5 仍未完成`

## 下一步
- 先等 idle watcher 在空窗把 `20260415-200051` 切进 `prod`。
- 切版后第一优先补 `workflow` 主线的 current-version smoke，确认 `assignment_agent_workspace_missing` 和 manual rerun stopgap 不再复现。
- `V3` 当前执行顺序已重排为 `V3-R4 -> V3-R2 -> V3-R1 -> V3-R5 -> V3-R3`，在 `R4` live 回归闭环前不提前切 `V4`。

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: 我这轮继续偏向“先修 live 风险，再把 gate / 根仓同步 / candidate 一次收干净”，不接受只停在现场诊断。
- delta_validation: 下一轮继续验证 `20260415-200051` 进入 live 后，`workflow` 主线不再命中 workspace missing / manual rerun stopgap。

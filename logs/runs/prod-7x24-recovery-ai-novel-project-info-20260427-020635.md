# prod 7x24 recovery and project info isolation - 2026-04-27 02:06

- preference_ref: `state/user-preferences.md`
- delta_observation: 用户把本轮明确定位为 `7x24` 生产运行问题，要求修补后切换生产版本并恢复连续运行；同时要求 AI 小说项目信息展示只显示自身项目真相，不混入 `workflow` 版本信息。
- delta_validation: 后续凡涉及生产升级或项目信息展示，先核 `/api/runtime-upgrade/status`、`/api/status`、`/api/schedules`、`/api/projects?lifecycle_state=all` 与部署副本 JS。

## Summary
- 代码修复已在 `.repository/pm-main@6b34e4a` 提交，并同步到 `../workflow_code@6b34e4a`。
- `test=20260427-010707` 已部署并生成 `prod` candidate，证据为 `.running/control/reports/test-gate-20260427-010707.json` 与 `.running/control/logs/test/deploy-20260427-010707.json`。
- 生产已切换到 `prod current=20260427-010707`，`candidate=20260427-010707`，`candidate_is_newer=false`。
- 通过受支持 API 将 `workflow_testmate dts-00011-r5-regression-testmate-20260427-0128` 的 post-upgrade ghost running 失败收口，audit=`aaud-20260427-020302-b63dc1`。
- 7x24 出口已恢复：`workflow_bugmate dr-20260426-abf45cbb38-release` 当前是真实 `live_execution/provider_pid=34708`；`workflow` 主线已补建 ready 下一棒 `node-sti-20260427-90089d9b`，并把 `[持续迭代] workflow` 下一次 once 入口重排到 `2026-04-27T02:56:00+08:00`。
- AI 小说项目读面已验证：`project-ai-novel-profit` 回读自身 `project_contract/runtime_policy/startup_readiness`；生产 JS 对非 workflow 项目走 `projectOpsProjectInfoHtml`。

## Evidence
- `/healthz`: `ok=true`。
- `/api/runtime-upgrade/status`: `current=20260427-010707 / candidate=20260427-010707 / request_pending=false / ghost_running_detected=false / running_task_count=1`，当前 running 是真实 provider，不是 ghost。
- `/api/status`: `running_task_count=1 / queued_task_count=1`；全局主图中 `workflow` 有 ready 主线 `node-sti-20260427-90089d9b`。
- `/api/schedules`: `[持续迭代] workflow` next_trigger_at=`2026-04-27T02:56:00+08:00`；`[持续迭代] novel_project_pm` next_trigger_at=`2026-04-27T05:14:00+08:00`。
- `/api/projects?lifecycle_state=all`: `project-ai-novel-profit` has `controller_role_id=novel_project_pm`, members `novel_quality_reviewer / novel_master_writer`, `project_contract.status=complete`, `runtime_policy_ref=projects/project-ai-novel-profit/runtime-policy`。

## Remaining Watch
- `V12` 仍不切版；`workflow_testmate` 的 post-fix regression 节点已失败收口，需要在 `workflow_bugmate` 全局缺陷链完成后重新派发 go/no-go。
- 当前生产无需重复 apply；下一轮只需关注真实 running、workflow ready 下一棒、workflow future schedule 与 novel project future schedule 是否继续接力。

## Final Readback - 2026-04-27 02:52
- `repair-ghost-running` 对 `dr-20260426-abf45cbb38-release` 的客户端请求超时，但现场随后回读为真实 `live_execution/provider_pid=34708`，`ghost_running_detected=false`。
- `[持续迭代] workflow` 的 `02:46` missed-once 现场已由 schedule recovery 补建为 `node-sti-20260427-90089d9b`，状态 `ready`；我又通过 `/api/schedules/sch-20260405-56eee156` 将下一次 once 重排到 `2026-04-27T02:56:00+08:00`，audit=`saud-20260427-91ec5e4a`。
- `project-ai-novel-profit` 回读 `controller_role_id=novel_project_pm`，成员为 `novel_quality_reviewer / novel_master_writer`，`project_contract.status=complete`，`runtime_policy_ref=projects/project-ai-novel-profit/runtime-policy`，且项目 payload 不含 `pm_version_status`。

## Final Recovery Readback - 2026-04-27 04:15
- `prod` 已完成正式切换：`current_version=20260427-033442 / candidate_version=20260427-033442 / candidate_is_newer=false / request_pending=false`。
- 本轮根因修复已生效到生产：`3762216 fix(assignment): 截断过长artifact避免主线执行中断`，新增用例 `verify_assignment_execution_oversized_artifact_markdown.py` 已接入 workflow gate；证据 `.running/control/reports/test-gate-20260427-033442.json`。
- 升级后残留的 `node-sti-20260427-c6798a33` projected-terminal ghost 已清：`status=succeeded / run_status=succeeded / ghost_running_detected=false / ghost_running_count=0`。
- 7x24 已恢复真实出口：`[持续迭代] workflow` 当前节点 `node-sti-20260427-e1253676` 为 `live_execution/provider_pid=40024`，且 schedule 保留 `next_trigger_at=2026-04-27T04:17:00+08:00`。
- AI 小说项目持续运行入口仍在：`[持续迭代] novel_project_pm` next_trigger_at=`2026-04-27T05:14:00+08:00`。
- AI 小说项目读面已复核为项目自身信息：`controller_role_id=novel_project_pm`，成员为 `novel_quality_reviewer / novel_master_writer`，`runtime_policy_ref=projects/project-ai-novel-profit/runtime-policy`，`has_pm_version_status=false`。
- `version_transition_decision=stay(V11)`；`workflow_testmate` 的 DTS 修复回归为 PASS，但 activation 仍 NO-GO，下一轮由主线继续消费该结论并刷新 V12 activation summary。
- `2026-04-27T04:20:00+08:00` 复核：04:17 入口已命中并补建 `node-sti-20260427-8cecc9c3`，状态 `ready`；当前仍有 `node-sti-20260427-e1253676 live_execution/provider_pid=40024`，所以 7x24 现场为 `1 running + 1 ready` 接力，而不是空窗。

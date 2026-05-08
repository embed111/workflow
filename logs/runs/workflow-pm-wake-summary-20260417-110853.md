# Workflow PM Wake Summary 2026-04-17 11:08:53 +08:00

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260417-edf65cb5`
- lane: `工程质量探测`
- lifecycle_stage: `验收`
- version_transition_decision: `stay(V3)`

## 本轮推进
- 类型：`工程质量探测 + 发布推进 + 版本执行约束调整`
- 我这轮没有继续纯观察 `V3-R3` 的 helper 学习缺口，而是直接修掉 PM daily 对 helper 自投递学习报告的识别缺口，并把 today daily 正式收口到 `completed`。

## 已完成动作
- 在 `.repository/pm-main/src/workflow_app/server/services/pm_daily_governance_service.py` 里把 helper 学习报告发现链补成“`self-target delivery + result_ref fallback`”双通道。
- 扩展 `.repository/pm-main/scripts/acceptance/verify_pm_daily_governance_tc_pm_002.py` 与 `docs/workflow/testing/PM治理专项用例编号.md`，正式覆盖 `workflow_devmate=self-target delivery / workflow_testmate=workflow delivery / workflow_qualitymate=result_ref fallback / workflow_ucdmate=optional self-target delivery`。
- 按 `test-session-manager` 跑通 `line budget` 与 `TC-PM-002`，再把代码提交到 `.repository/pm-main@192c8d9`，并把本机 `../workflow_code` fast-forward 到同一提交。
- 正常停掉旧 `test` 并重新部署，刷新出新的 `prod candidate=20260417-110714`。
- 执行 `refresh_pm_daily_governance.py --overwrite-existing`，把五个 helper 的真实学习报告投影回 `pm/daily-learning-reports/2026-04-17/`，让 `pm/daily-execution-history/2026-04-17.md` 收口为 `completed`。

## 验证
- `python .repository/pm-main/scripts/quality/check_workspace_line_budget.py --root .`
- `python .repository/pm-main/scripts/acceptance/verify_pm_daily_governance_tc_pm_002.py`
- `python .repository/pm-main/scripts/bin/refresh_pm_daily_governance.py --shell-root . --date 2026-04-17 --overwrite-existing`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .repository/pm-main/scripts/stop_workflow_env.ps1 -Environment test`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .repository/pm-main/scripts/deploy_workflow_env.ps1 -Environment test`
- `http://127.0.0.1:8090/healthz`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8090/api/schedules`

## 发布边界
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `workspace_head=code_root_head=192c8d9`
- `push_block_reason=-`
- `next_push_batch=等待 idle watcher 在空窗把 20260417-110714 切进 live；切版后优先复跑 current-version smoke，并重检 V4 activation gate 的真实 probe 替换进度`

## 版本评估
- `V3-R1`: `completed / 100% / eta=2026-04-16 / 未超时`
- `V3-R2`: `completed / 100% / eta=2026-04-16 / 未超时`
- `V3-R3`: `completed / 100% / eta=2026-04-17 / 未超时`
- `V3-R4`: `completed / 100% / eta=2026-04-16 / 未超时`
- `V3-R5`: `completed / 100% / eta=2026-04-16 / 未超时`
- `next_activation_candidate=V4 / next_activation_ready=false`
- `switch_blockers=V4 activation gate 仍停在 draft probe`
- `AAR=无新增`

## 当前风险与下一步
- 当前 `prod` 仍是 `current_version=20260417-102453`，`candidate_version=20260417-110714`，且 `running_task_count=1 / drain_active=true`；本轮不触发正式升级，只等待 idle watcher 在空窗切版。
- 当前 `7x24` 仍有真实出口：`/api/status` 为 `running_task_count=1 / queued_task_count=2`，主线下一棒 `node-sti-20260417-2f1d9de8` 已排队，保底巡检下一棒为 `node-sti-20260417-2a92f5ad / 2026-04-17T11:20:00+08:00 / 已建单待调度`。
- 下一轮优先复跑切版后的 `current-version smoke`，并把 `V4 activation gate` 的 `draft:` probe 换成真实 probe，再决定是否从 `stay(V3)` 切到 `switch(V4)`。

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: helper 学习任务的真实交付既可能走 `workflow-target`，也可能走 `self-target delivery`，甚至只保留在成功节点的 `result_ref`；PM daily 只盯 `delivery/workflow/*` 会把 today daily 稳定误报成缺口未收口。
- delta_validation: 下一轮继续验证 `candidate=20260417-110714` 切版后的 `current-version smoke` 与 `V4 activation gate` 真实 probe 替换进度。
- memory_ref: `.codex/memory/2026-04/2026-04-17.md`

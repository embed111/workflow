# continuous-improvement-report

- generated_at: `2026-04-14T13:59:31+08:00`
- live_snapshot_at: `2026-04-14T13:45:00+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260414-530e47ac`
- task_name: `[持续迭代] workflow / 2026-04-14 12:45:00`
- active_version: `V2`
- lane: `工程质量探测`
- lifecycle_stage: `开发实现`
- baseline: `prod=20260414-125438`
- current_candidate: `20260414-134341`
- root_sync_state: `clean_synced`
- workspace_head: `c112c6a`
- code_root_head: `c112c6a`
- preference_ref: `state/user-preferences.md`
- delta_observation: `live prod 已切到 20260414-125438，但旧版仍会把 pm_version_status.lane 读空；我这轮先把 parser 和 gate 补齐，再把修复刷新成 20260414-134341 candidate。`
- delta_validation: `待 idle watcher 把 20260414-134341 切进 prod 后，优先复核 /api/status 的 lane / baseline / 响应时间，再决定是否切回 R5 / R2。`
- memory_ref: `.codex/memory/2026-04/2026-04-14.md`

## 本轮结果

我这轮完成了 1 项真实推进性修改：在 `.repository/pm-main` 修复了 `pm_version_status` 对 `当前最高价值泳道临时切到` 文案的解析缺口，并把这个真实文案变体补进 acceptance。对应代码批次已提交为 `c112c6a fix(pm版本): 兼容当前状态快照的临时切换泳道文案`，再通过本机 `../workflow_code` 的 `fetch + ff-only merge` 完成本地根仓收口。

这批代码已经完成最小验证并刷新成新的 `test/prod candidate=20260414-134341`。当前 live `prod` 仍是 `20260414-125438`，所以 `/api/status.pm_version_status.lane` 还会继续为空；这不是“还没推进”，而是修复已经进了 candidate，正在等 idle watcher 在空窗切版。

## 代码与发布推进

- 我更新了 `.repository/pm-main/src/workflow_app/server/services/pm_version_status_service.py`，让 lane/lifecycle 的解析不再只认固定中文句式。
- 我更新了 `.repository/pm-main/scripts/acceptance/verify_pm_current_version_snapshot_alignment.py`，让快照一致性探针同步兼容这类治理文案变体。
- 我更新了 `.repository/pm-main/scripts/acceptance/verify_pm_version_truth_source.py`，新增临时 fixture，锁住 `当前最高价值泳道临时切到` 这种真实文案不会再把 `lane / lifecycle / baseline` 读空。
- 我先在 `.repository/pm-main` 提交 `c112c6a`，随后尝试 `git push origin main`；由于 `../workflow_code` 的 `updateInstead` 保护拒绝了 checked-out 分支直推，我改走受支持的本地根仓收口路径：`git -C ../workflow_code fetch ../workflow/.repository/pm-main main` + `git -C ../workflow_code merge --ff-only FETCH_HEAD`。
- 我按受支持路径先停掉旧 `test`，再重跑 `deploy_workflow_env.ps1 -Environment test`，把新的 `prod candidate` 刷到 `20260414-134341`。

## 当前 live 判断

- `/healthz` 正常，时间戳为 `2026-04-14T13:45:00+08:00`。
- `/api/status` 当前为 `running_task_count=1 / queued_task_count=2 / workflow_mainline_starvation_state=mitigated`；当前直接出口是 `running + queued + patrol future`，其中 mainline queued=`node-sti-20260414-a4492c78`，patrol next=`2026-04-14T14:00:00+08:00`。
- `/api/runtime-upgrade/status` 当前为 `current_version=20260414-125438 / candidate_version=20260414-134341 / candidate_is_newer=true / drain_active=true / can_upgrade=false / blocking_reason=running_tasks_present`。
- `/api/schedules` 当前显示 mainline 最近结果为 `node-sti-20260414-a4492c78 / queued`，patrol 最近结果为 `node-sti-20260414-5f2dd065 / queued`，保底下一拍仍是 `2026-04-14T14:00:00+08:00`。
- 当前最主要即时风险已经收窄为两条：`134341` 仍在等 idle watcher 创造升级空窗；在切版之前，旧版 `prod(8090)` 还会继续把 `pm_version_status.lane` 读空。

## Active 需求逐项评估

- `V2-R1`: `completed / 100% / ETA=已于 2026-04-14 完成 / timeout=-`
- `V2-R2`: `in_progress / 93% / ETA=2026-04-18 / timeout=未超时`
- `V2-R3`: `in_progress / 99% / ETA=2026-04-19 / timeout=未超时`
- `V2-R4`: `in_progress / 74% / ETA=2026-04-19 / timeout=未超时`
- `V2-R5`: `in_progress / 96% / ETA=2026-04-15 / timeout=未超时`
- `V2-R6`: `in_progress / 80% / ETA=2026-04-15 / timeout=未超时`
- `V2-R7`: `in_progress / 82% / ETA=2026-04-16 / timeout=未超时`
- `V2-R8`: `completed / 100% / ETA=已于 2026-04-13 完成 / timeout=-`

本轮没有需求点超时，不触发新的 AAR。

## 验证与证据

- line budget: `.repository/pm-main/.test/20260414-133615-127/report.md`
- pm version truth source: `.repository/pm-main/.test/20260414-135706-235/report.md`
- pm current version snapshot alignment: `.repository/pm-main/.test/20260414-135728-477/report.md`
- workflow gate: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260414-133831.md`
- deploy report: `.running/control/logs/test/deploy-20260414-134341.json`
- live checks: `Invoke-RestMethod http://127.0.0.1:8090/healthz` / `Invoke-RestMethod http://127.0.0.1:8090/api/status` / `Invoke-RestMethod http://127.0.0.1:8090/api/runtime-upgrade/status` / `Invoke-RestMethod http://127.0.0.1:8090/api/schedules`

## 下一步

- 第一优先级仍是等 idle watcher 在空窗把 `20260414-134341` 切进 `prod`，随后立即复核 `8090 /api/status` 的 lane、baseline 和响应时间。
- `R4` 这条 live 风险收住后，我把窗口切回 `R5 / R2` 的正式编号化证据与收尾。


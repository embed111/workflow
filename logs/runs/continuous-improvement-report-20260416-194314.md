# Continuous Improvement Report / 2026-04-16 19:43 +08:00

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260416-34db2512`
- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-16.md`

## 本轮推进
- 工程质量探测：
  - 修复 `.repository/pm-main/scripts/bin/refresh_pm_current_version_snapshot.py`，兼容当前真实的 `prod=current_version=candidate_version=...` live 句式。
  - 补强 `.repository/pm-main/scripts/acceptance/verify_pm_current_version_snapshot_refresh.py` fixture，覆盖 current-version 的真实文件形态。
  - 修复 `.repository/pm-main/scripts/acceptance/verify_runtime_upgrade_ghost_running_repair.py` 的隔离环境，避免 live `prod candidate` drain 污染本地验收。
- 发布推进：
  - `pm-main` 已提交 `2fbea60 fix(snapshot): 兼容current-version live新句式并隔离ghost repair验收`。
  - 本机 `../workflow_code` 已通过 `fetch + ff-only merge` 收口到同一提交。
  - `test` 已重发并生成新的 `prod candidate=20260416-194053`。
  - 六个 developer workspace 已恢复 `clean_synced@2fbea60`。

## 当前版本判断
- `version_transition_decision=stay(V3)`；`V4` 仍是 `next_activation_candidate`，但 `next_activation_ready=false`。
- `lane=工程质量探测`；`lifecycle_stage=开发实现`。
- 当前 active 需求状态：
  - `V3-R1=completed 100% / ETA 2026-04-16 / 未超时`
  - `V3-R2=in_progress 99% / ETA 2026-04-16 / 未超时`
  - `V3-R3=planned 35% / ETA 2026-04-18 / 未超时`
  - `V3-R4=completed 100% / ETA 2026-04-16 / 未超时`
  - `V3-R5=in_progress 99% / ETA 2026-04-16 / 未超时`
- 本轮没有需求超时，不触发新的 AAR。

## Live 真相
- 发布边界：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=2fbea60 / push_block_reason=-`
- `/api/status.pm_version_status` 已对齐：`baseline=document_baseline=prod=20260416-184445`
- `/api/config/developer-workspaces` 六个 developer workspace 全部 `clean_synced@2fbea60`
- `/api/runtime-upgrade/status` 当前为：`current_version=20260416-184445 / candidate_version=20260416-194053 / candidate_is_newer=true / drain_active=true / running_task_count=1 / can_upgrade=false / ghost_running_count=0`
- 当前 workflow 现场仍是：`node-sti-20260416-34db2512 running + node-sti-20260416-303f2814 ready + node-sti-20260416-dd128641 ready`

## 验证
- `line budget`: `.repository/pm-main/.test/20260416-192032-612/report.md`
- `snapshot refresh` 专项：`.repository/pm-main/.test/20260416-192036-564/report.md`
- `ghost_running_repair` 专项：`.repository/pm-main/.test/20260416-193010-855/report.md`
- `workflow gate`: `.repository/pm-main/.test/20260416-193045-494/report.md`
- `workflow gate` 汇总：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260416-193804.md`
- `test deploy`: `.running/control/logs/test/deploy-20260416-194053.json`
- live API：`/api/status`、`/api/schedules`、`/api/runtime-upgrade/status`、`/api/config/developer-workspaces`

## 下一步
- 等 idle watcher 在空窗把 `candidate=20260416-194053` 切入 live；当前主线/巡检节点不直接调用 `/api/runtime-upgrade/apply`。
- 切版成功后优先补一条基于 `184445/194053` 的 current-version smoke，把 `V3-R2 / V3-R5` 的旧 `173828/180910` 证据替换成最新 live 结论。
- 继续观察当前 running 主线 `node-sti-20260416-34db2512` 收尾后，下一条 mainline 的 launch summary 是否也完成从旧 `180910/1faa381` 到新基线的滚动。

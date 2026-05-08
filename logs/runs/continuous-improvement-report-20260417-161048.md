# Continuous Improvement Report

- generated_at: `2026-04-17T16:18:20+08:00`
- active_version: `V4`
- lane: `测试探测`
- lifecycle_stage: `基于基线测试`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260417-f792cae7`
- change_batch: `.repository/pm-main@72cdc7d / ../workflow_code@72cdc7d`
- memory_ref: `.codex/memory/2026-04/2026-04-17.md`

## Result Summary

- 我修掉了 `pm_version_status_service.py` 的 baseline 解析误吸旧值问题：`baseline 继续对齐为` 现在能被正确读取，正文里的历史 `baseline=20260417-134734` 不会再被当成当前 baseline。
- 我把这批修复收口到了 `.repository/pm-main@72cdc7d / ../workflow_code@72cdc7d`，并通过受支持的 `fetch + ff-only merge` 处理了本机根仓同步边界。
- 我重新部署了 `test`，刷新出新的 `prod candidate=20260417-160828`，同时把五个 helper developer workspaces 全部 refresh 到 `clean_synced@72cdc7d`。
- 我在 `8092` 上验证了运行态效果：`/api/status.pm_version_status.baseline=document_baseline=prod=20260417-145421`；`8090` 仍显示旧 `134734`，因为 live `prod` 还没切到新 candidate。

## Changes

- 代码修复：
  - `.repository/pm-main/src/workflow_app/server/services/pm_version_status_service.py`
  - 收口 baseline 解析口径，避免正文里的历史 `baseline=` 被误吸成当前 baseline。
- 回归用例：
  - `.repository/pm-main/scripts/acceptance/verify_pm_version_truth_source.py`
  - `.repository/pm-main/scripts/acceptance/verify_pm_current_version_snapshot_alignment.py`
  - 新增“继续对齐为 + 正文旧 baseline 不得误吸”的 fixture。
- 发布边界收口：
  - `git -C .repository/pm-main commit -m "fix(pm-version): 修正baseline快照解析误吸旧值"`
  - `git -C ../workflow_code fetch D:/code/AI/J-Agents/workflow/.repository/pm-main main`
  - `git -C ../workflow_code merge --ff-only FETCH_HEAD`
  - `powershell -File .repository/pm-main/scripts/stop_workflow_env.ps1 -Environment test`
  - `powershell -File .repository/pm-main/scripts/deploy_workflow_env.ps1 -Environment test`
  - `python ../workflow_code/scripts/manage_developer_workspace.py ... bootstrap --developer-id <helper>`

## Validation

- line budget：
  - `.repository/pm-main/.test/20260417-160504-886/report.md`
- PM version truth source：
  - `.repository/pm-main/.test/20260417-161810-841/report.md`
- PM current-version snapshot alignment：
  - `.repository/pm-main/.test/20260417-161820-785/report.md`
- `test` 部署：
  - `.running/control/logs/test/deploy-20260417-160828.json`
- `test` 运行态验证：
  - `8092 /api/status.pm_version_status.baseline=document_baseline=prod=20260417-145421`
  - `8092 /api/runtime-upgrade/status.current_version=candidate_version=20260417-160828`
- `prod` 当前现场：
  - `8090 /api/status.pm_version_status.baseline=document_baseline=20260417-134734`
  - `8090 /api/runtime-upgrade/status.current_version=20260417-145421 / candidate_version=20260417-160828 / candidate_is_newer=true / drain_active=true / running_task_count=1`

## V4 Assessment

- `V4-R1`: `in_progress / 40% / eta=2026-04-19 / 未超时`
- `V4-R2`: `planned / 5% / eta=2026-04-20 / 未超时`
- `V4-R3`: `planned / 10% / eta=2026-04-20 / 未超时`
- `V4-R4`: `in_progress / 65% / eta=2026-04-20 / 未超时`
- `version_transition_decision=stay(V4)`
- `next_activation_candidate=- / next_activation_ready=false`
- `switch_blockers=V5 仍保持 backlog activation_readiness=draft`

## Release Boundary

- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0 / untracked_count=0`
- `workspace_head=code_root_head=72cdc7d`
- `helper developer workspace sync=workflow_testmate / workflow_ucdmate / workflow_devmate / workflow_qualitymate / workflow_bugmate / pm-main -> clean_synced@72cdc7d`
- `push_block_reason=-`
- `next_push_batch=等待 idle watcher 在空窗把 20260417-160828 切进 prod；切版后优先复核 8090 上的 pm_version_status baseline/document_baseline 是否追到 145421，并继续消费 corrected smoke -> corrected UCD brief`

## Warnings

- 当前 `prod` 仍在旧代码上运行，`/api/status.pm_version_status.baseline/document_baseline` 还没有追到 `prod=20260417-145421`；这不是新修复失效，而是 `candidate=20260417-160828` 还没命中空窗切版。
- `idle watcher` 尚未执行正式切版；在 `running_task_count=1` 释放前，不应手动调用 `/api/runtime-upgrade/apply`。

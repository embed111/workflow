# Continuous Improvement Report 2026-04-15 15:54:01

- ticket: `asg-20260327-223335-b79f27`
- node: `node-sti-20260415-8674ca62`
- lane: `工程质量探测 + 发布推进`
- lifecycle_stage: `验收`
- version_transition_decision: `stay(V2)`
- next_activation_candidate: `V3`
- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-15.md`

## Summary
- 我修掉了 `prod=20260415-151342` 升级后两条会继续扭曲 PM 真相源的回归：
  - `refresh_pm_current_version_snapshot.py` 不兼容 `baseline 仍是 live`
  - `pm_version_status_service.load_pm_version_status()` 不会把同一句式解析成 `document_baseline`
- 我把这批修复连同 acceptance 一起收口到 `.repository/pm-main` 提交 `1eae3bc`，同步到 `../workflow_code`，再把 `test/prod candidate` 刷到 `20260415-155232`
- 当前 live `prod` 仍是 `20260415-151342`；带修复的 `candidate=20260415-155232` 还没切进 `prod`，所以本轮继续保持 `stay(V2)`，不提前切到 `V3`

## Changes
- 代码：
  - `.repository/pm-main/scripts/bin/refresh_pm_current_version_snapshot.py`
  - `.repository/pm-main/src/workflow_app/server/services/pm_version_status_service.py`
- 验收：
  - `.repository/pm-main/scripts/acceptance/verify_pm_current_version_snapshot_refresh.py`
  - `.repository/pm-main/scripts/acceptance/verify_pm_version_truth_source.py`
  - `.repository/pm-main/scripts/acceptance/verify_pm_current_version_snapshot_alignment.py`
- 治理真相：
  - `pm/PM当前版本计划.md`
  - `pm/versions/V2/版本计划.md`
  - `pm/versions/V2/需求映射与覆盖矩阵.md`

## Validation
- `python scripts/quality/check_workspace_line_budget.py --root .`
- `python scripts/acceptance/verify_pm_current_version_snapshot_refresh.py`
- `python scripts/acceptance/verify_pm_version_truth_source.py`
- `python scripts/acceptance/verify_pm_current_version_tc_pm_003.py`
- `python scripts/acceptance/verify_pm_current_version_matrix_tc_pm_004.py`
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/acceptance/collect_v2_r4_r5_current_version_smoke.ps1 -BaseUrl http://127.0.0.1:8090 -ExpectedVersion 20260415-151342`
  - 结果：失败点只剩 `status_pm_document_baseline_not_expected`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy_workflow_env.ps1 -Environment test`
  - 结果：`deploy-20260415-155232.json`，新 `prod candidate=20260415-155232`

## Release Boundary
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `workspace_head=code_root_head=1eae3bc`
- `push_block_reason=-`
- `next_push_batch=等待 20260415-155232 切进 prod 后重跑 live smoke`

## Active Version Review
- `V2-R1 ~ V2-R8` 当前全部保持 `completed / 未超时`
- 本轮无新增 AAR
- 当前不切 `V3` 的直接原因：
  - live `prod=20260415-151342` 上 `/api/status.pm_version_status.document_baseline=''`
  - 带修复的 `candidate=20260415-155232` 尚未切进 `prod`
  - `155232` 的 live current-version smoke 还没重跑通过

## Next
- 等 idle watcher 把 `candidate=20260415-155232` 切进 `prod`
- 切版后优先重跑一拍 live `current-version smoke`
- 若 smoke 通过，则把 `active_version` 从 `V2` 正式切到 `V3`

## Snapshot Addendum
- delta_observation: `prod=20260415-151342` 上 `/api/status.pm_version_status.document_baseline` 仍为空；这是 live 读链解析回归，不是单纯文档没写。
- delta_validation: 等 `20260415-155232` 切进 `prod` 后，立即重跑 `collect_v2_r4_r5_current_version_smoke.ps1 -ExpectedVersion 20260415-155232`。

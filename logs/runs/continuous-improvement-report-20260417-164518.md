# Continuous Improvement Report

- executed_at: `2026-04-17T16:45:18+08:00`
- active_version: `V4`
- lane: `测试探测`
- lifecycle_stage: `基于基线测试`
- advancement_type: `工程质量探测`

## 本轮推进
- 我修复了 `.repository/pm-main/scripts/bin/refresh_pm_current_version_snapshot.py` 对 `V4` 当前 `baseline/document_baseline 继续对齐为` 句式的兼容，并在 `.repository/pm-main/scripts/acceptance/verify_pm_current_version_snapshot_refresh.py` 增加了对应的 `V4` 回归夹具。
- 我用修好的脚本把当前 live PM 快照直接追平，`8090 /api/status.pm_version_status.baseline=document_baseline=prod=20260417-160828` 已恢复一致。
- 我把代码提交到 `.repository/pm-main@a3e05a3`，并通过受支持的本机 `../workflow_code fetch + ff-only merge` 收口到 `../workflow_code@a3e05a3`；随后跑通完整 `workflow gate`，重部署 `test` 并生成新的 `prod candidate=20260417-164304`。

## 需求状态
- `V4-R1`: `in_progress / 40% / eta=2026-04-19 / 未超时`。`workflow_ucdmate` 的 corrected route brief 仍在收口，尚未形成最终实现批次。
- `V4-R2`: `planned / 5% / eta=2026-04-20 / 未超时`。
- `V4-R3`: `planned / 10% / eta=2026-04-20 / 未超时`。
- `V4-R4`: `in_progress / 75% / eta=2026-04-20 / 未超时`。live `document_baseline` drift 已消除，后续只等 `164304` 切进 prod 后再复跑 current-version smoke。

## 发布边界与 Live 真相
- `root_sync_state=clean_synced`，`workspace_head=code_root_head=a3e05a3`，`push_block_reason=-`。
- `prod current_version=20260417-160828`，`candidate_version=20260417-164304`，`candidate_is_newer=true`，`drain_active=true`，`running_task_count=1`，`can_upgrade=false`。
- 当前 mainline `node-sti-20260417-850768a1` 仍在运行，下一条 mainline `node-sti-20260417-8c3cecb7` 已 ready；`7x24` 真实出口仍成立。
- `next_push_batch=等待 idle watcher 在空窗把 20260417-164304 切进 prod；切版后优先复核 current-version smoke 与 corrected UCD brief 是否仍沿用 145421 旧口径`

## 验证
- `line budget`: `.repository/pm-main/.test/20260417-163624-858/report.md`
- `snapshot refresh targeted verify`: `.repository/pm-main/.test/20260417-163637-015/report.md`
- `workflow gate`: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260417-164217.md`
- `test deploy / candidate`: `.running/control/logs/test/deploy-20260417-164304.json`

## 下一步
- 等 idle watcher 在空窗把 `20260417-164304` 切进 prod。
- 切版后先复跑 current-version smoke，并确认 `workflow_ucdmate` 的 corrected brief 不再引用 `145421` 的旧口径。
- 若 corrected brief 暴露的是实现问题而不是证据口径问题，下一轮把最小实现批次切给 `workflow_devmate`。

### Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: 本轮 live 风险已经从“`document_baseline` 漂移”收口成“等待 `164304` 空窗升级 + corrected UCD brief 交付”。
- delta_validation: 待 `164304` 切进 prod 后，优先复跑 current-version smoke，并核对 corrected brief 是否已改用 `160828/164304` 的 live 口径。

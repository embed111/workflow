# Continuous Improvement Report 2026-04-15 23:14:32 +08:00

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260415-f49e849d`
- active_version: `V3`
- lane: `功能开发`
- lifecycle_stage: `开发实现`

## Summary
- 我把 `developer workspace` 的 registry 读链改成了“按 live Git 真相自校正并按需回写”，不再让 `state/developer-workspaces.json` 长时间停在旧 commit。
- 我把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate / pm-main` 六个 developer workspace 全部 refresh 到 `0ce4123`，并确认 registry 与 `test=8092 /api/config/developer-workspaces` 都已返回 `workspace_head / code_root_head / root_sync_state / last_checked_at`。
- 我补跑 line budget、`verify_developer_workspace_registry_reconcile.py` 和完整 `workflow gate`，随后把代码收口到本机 `../workflow_code`，并把 `test/prod candidate` 刷到 `20260415-231150`。

## Actions
- 修改 `.repository/pm-main/src/workflow_app/server/services/developer_workspace_service.py`，让 `list_developer_workspaces()` 在读取时补齐 live Git 真相并按需落盘。
- 新增 `.repository/pm-main/scripts/acceptance/verify_developer_workspace_registry_reconcile.py`，并接入 `.repository/pm-main/scripts/acceptance/workflow_gate_probe_registry.py`。
- 在 `.repository/pm-main` 提交 `0ce4123 fix(workspace): 回写developer workspace同步真相并补回归探针`，并 fast-forward 到本机 `../workflow_code`。
- 通过受支持的 `manage_developer_workspace.py bootstrap` 刷新六个 developer workspace，再用 `manage_developer_workspace.py status` 回写 `state/developer-workspaces.json`。
- 停掉旧 `test` 后重发 `deploy_workflow_env.ps1 -Environment test`，生成 `candidate=20260415-231150`。

## Validation
- `.repository/pm-main/.test/20260415-225741-448/report.md`
- `.repository/pm-main/.test/20260415-230514-819/report.md`
- `.repository/pm-main/.test/20260415-230525-082/report.md`
- `python .repository/pm-main/scripts/manage_developer_workspace.py --root .running/control/runtime/prod status`
- `Invoke-RestMethod http://127.0.0.1:8092/api/config/developer-workspaces`
- `Invoke-RestMethod http://127.0.0.1:8090/api/runtime-upgrade/status`
- `.running/control/logs/test/deploy-20260415-231150.json`

## Version
- `version_transition_decision=stay(V3)`
- 当前 active 需求逐项评估：
  - `V3-R1=status=in_progress / progress=65% / eta=2026-04-16 / timeout=未超时`
  - `V3-R2=status=in_progress / progress=85% / eta=2026-04-16 / timeout=未超时`
  - `V3-R3=status=planned / progress=35% / eta=2026-04-18 / timeout=未超时`
  - `V3-R4=status=in_progress / progress=90% / eta=2026-04-16 / timeout=未超时`
  - `V3-R5=status=in_progress / progress=85% / eta=2026-04-16 / timeout=未超时`
- 本轮无需求点超时，不触发新的版本 AAR。

## Boundary
- `root_sync_state=clean_synced`
- `ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`
- `workspace_head=code_root_head=0ce4123`
- `push_block_reason=-`
- `next_push_batch=等待 candidate 20260415-231150 进入 live 后补 prod developer-workspace smoke`

## Parallel
- `parallel_candidate_count=1`
- `parallel_dispatched_count=0`
- `active_helper_tasks=[]`
- `parallel_block_reason=本轮先收口 helper developer workspace sync 真相与 candidate 231150，待空窗切版后再补 prod smoke`
- `helper_dispatch_focus=helper developer workspace sync truth`
- `helper_dispatch_effect=六个 developer workspace 已统一 refresh 到 0ce4123，registry 与 test API 都已返回 clean_synced 结构化真相`

## Next
- 等 `prod` 从 `20260415-222921` 升到 `20260415-231150` 后，优先补 prod 侧 `/api/config/developer-workspaces` smoke。
- 切版 smoke 通过后，把主线切回 `V3-R2` 的职责矩阵冻结，并补 `workflow_ucdmate` 的正式落点。

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: `state/developer-workspaces.json` 会比 live Git 头更容易陈旧，不能继续只在 bootstrap/refresh 结束瞬间写一次就当长期真相。
- delta_validation: 等 `20260415-231150` 进 live 后，补 prod `/api/config/developer-workspaces` smoke，确认 registry reconcile 字段在正式环境也继续稳定输出。

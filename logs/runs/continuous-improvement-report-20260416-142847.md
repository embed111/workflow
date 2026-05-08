# Continuous Improvement Report

- generated_at: `2026-04-16T14:28:47+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260416-ede2582e`
- active_version: `V3`
- lane: `测试探测`
- lifecycle_stage: `开发实现`
- baseline: `prod=20260416-125712`
- candidate: `20260416-142644`
- preference_ref: `state/user-preferences.md`
- delta_observation: `你持续要求我先用 live 真相和发布边界判断优先级，再给单轮交付；这轮我延续了“先收口 finalize stall / dirty workspace / candidate，再回写版本真相”的执行方式。`
- delta_validation: `下一拍继续先看 current_version 是否切到 20260416-142644、workflow_testmate smoke 是否追平，再决定 V3-R2 / V3-R5 的最终收口动作。`

## Summary

这轮我把 `workflow_devmate` 的 finalize stall、dirty developer workspace 和 `workflow_focus_context` 代码切片一起收口了：helper 节点 `node-20260416-133631-114f18` 已恢复成 `succeeded + delivered`，代码已在 `workflow_devmate` 工作区通过 targeted probes 与完整 `workflow gate`，并以 `9977de0 fix(assignment): 显式收口workflow focus contract并兼容旧指引卡调用` 收到本机 `../workflow_code`。随后我把六个 developer workspace 全量 refresh 到 `9977de0`，重新部署 `test` 并刷新出新的 `prod candidate=20260416-142644`。

## Actions

- 用当前版本自带的 `_finalize_assignment_execution_run()` 精确恢复 `workflow_devmate` 节点 `node-20260416-133631-114f18`，保住真实 `artifact_markdown`、delivery inbox 和 source workspace cleanup，而不是走只会生成通用占位文档的“提交产物”接口。
- 定位并修复 `assignmentWorkboardGuidanceSnapshot()` 对旧 signal-cards 调用口径不兼容的回归；新的实现同时兼容 `workflow_focus_context` 新合同和旧 probe 的参数顺序。
- 重新跑通 `verify_assignment_workboard_signal_cards.js`、`verify_assignment_mainline_visibility.py`、`verify_assignment_center_mainline_visibility.js` 与完整 `workflow gate`。
- 在 `workflow_devmate` 工作区提交 `9977de0`，并用受支持的本机 `../workflow_code fetch + ff-only merge` 收口根仓，规避本地 `updateInstead` 的假性 dirty 拦截。
- 把 `pm-main / workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 六个 developer workspace 全量 refresh 到 `9977de0`。
- 停掉旧 `test` 后重新部署，刷出 `candidate=20260416-142644`。

## Validation

- `python .repository/workflow_devmate/scripts/quality/check_workspace_line_budget.py --root .repository/workflow_devmate`
- `.repository/workflow_devmate/.test/20260416-141729-178/report.md`
- `.repository/workflow_devmate/.test/runs/workflow-gate-acceptance-20260416-142246.md`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/artifacts/node-20260416-133631-114f18/output/workflow_devmate-v3-r2-workflow-focus-context.md`
- `.running/control/logs/test/deploy-20260416-142644.json`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8090/api/config/developer-workspaces`

## Version Assessment

- `V3-R1`: `completed / 100% / ETA 2026-04-16 / 未超时`
- `V3-R2`: `in_progress / 99% / ETA 2026-04-16 / 未超时`
  `workflow_devmate` 的 `workflow_focus_context` 切片已真实交付、回归并收口到 `9977de0`；剩余动作改成等待 `20260416-142644` 进入 live 后验证真实 assignment center 不回退。
- `V3-R3`: `planned / 35% / ETA 2026-04-18 / 未超时`
- `V3-R4`: `completed / 100% / ETA 2026-04-16 / 未超时`
- `V3-R5`: `in_progress / 99% / ETA 2026-04-16 / 未超时`
  `workflow_testmate` 的 `125712` smoke 已经回交，旧 `120206` running baseline 保留项也已随主线切换消失；当前剩余动作改成等待 `142644` 进入 live 后复跑同一条 smoke。
- `version_transition_decision`: `stay(V3)`
- `next_activation_candidate`: `V4`
- `next_activation_ready`: `false`
- `AAR`: `本轮无新增超时需求点，不触发 AAR`

## Release Boundary

- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `workspace_head=code_root_head=9977de0`
- `push_block_reason=-`
- `next_push_batch=等待 idle watcher 把 20260416-142644 切进 live，再由 workflow_testmate 复跑 current-version smoke 并验证 workflow_focus_context 的 live 真相`

## Warnings

- `prod` 当前仍为 `20260416-125712`，`candidate=20260416-142644` 已进入 `candidate_newer_pending_idle_window`，现在还不能把这批变更说成已经进入 live。
- `/api/runtime-upgrade/status` 仍返回 `ghost_running_detected=true / ghost_running_count=4`；这批历史 refs 本轮没有扩散成新阻塞，但仍是下一拍要清债的旧账。

## Next

- 等当前 running 主线 `node-sti-20260416-ede2582e` 收尾，让 idle watcher 在空窗把 `prod` 切到 `20260416-142644`。
- 切版后优先让 `workflow_testmate` 复跑 current-version smoke，确认 `V3-R5` 在 `142644` 上全绿。
- 再验证 `workflow_focus_context` 在 live assignment center 上是否按 `9977de0` 生效；若仍回退，再按新 candidate 真相决定是补最小修复还是正式提缺陷。

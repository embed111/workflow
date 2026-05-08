# Continuous Improvement Report

- generated_at: `2026-04-18T11:14:50+08:00`
- active_version: `V4`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- preference_ref: `state/user-preferences.md`
- delta_observation: `当 live 风险已经被明确点名为 formal route 时，用户更希望我直接把它落成代码、gate 和部署收口，而不是继续把同一风险留在“下一轮处理”。`
- delta_validation: `等 prod 在空窗切到 20260418-111312 后，继续复跑 current-version smoke / recent-failure contract，并观察 test 部署后 T9 ghost 是否仍会重复出现。`

## Summary

- 我把原型测试图里会反复派发到不存在工作区的 `T17/T18/T19` 收成 `5575987 fix(test-data): 阻止原型图占位节点派发到不存在代理`：让三条 placeholder 节点显式依赖 failed `T20`，保持 `blocked`，不再继续制造 `assignment_agent_workspace_missing` 噪音。
- 我新增 `verify_assignment_test_graph_placeholder_nodes.py`，并把它接进 `workflow gate`，用最小红绿回归锁住“placeholder 节点不会再从占位态漂成可派发态”。
- 我按默认发布约束把 `.repository/pm-main` 同步回本机 `../workflow_code@5575987`，随后刷新 `test / prod candidate=20260418-111312`；部署后再次执行受支持的 `repair-ghost-running`，把 `T9` 拉回 `failed`，让 `8092` 恢复到 `running_task_count=0 / ghost_running_detected=false`。

## Validation

- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260418-110844-157/report.md`
- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/runs/workflow-gate-acceptance-20260418-111217.md`
- `D:/code/AI/J-Agents/workflow/.running/control/logs/test/deploy-20260418-111312.json`
- `GET http://127.0.0.1:8092/api/assignments/asg-20260417-202951-ec981b/status-detail?node_id=T17`
- `POST http://127.0.0.1:8092/api/runtime-upgrade/repair-ghost-running`
- `GET http://127.0.0.1:8090/api/runtime-upgrade/status`
- `GET http://127.0.0.1:8092/api/runtime-upgrade/status`

## Version Assessment

- `V4-R1`: `in_progress / 90% / eta=2026-04-19 / 未超时`
- `V4-R2`: `in_progress / 60% / eta=2026-04-20 / 未超时`
- `V4-R3`: `in_progress / 88% / eta=2026-04-20 / 未超时`
- `V4-R4`: `completed / 100% / eta=2026-04-17 / 未超时`
- `version_transition_decision=stay(V4)`；`next_activation_ready=false`；本轮无新增 AAR

## Release Boundary

- `root_sync_state=clean_synced`
- `workspace_head=code_root_head=5575987`
- `ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`
- `git -C .repository/pm-main status --short --branch = ## main...origin/main [ahead 3]`
- `git -C ../workflow_code status --short --branch = ## main...origin/main [ahead 133]`
- 上述 `ahead` 仅是本地 tracking ref 相对 GitHub 的参考视图，不构成当前 `workspace -> code_root` 阻塞

## Live Status

- `prod`: `current_version=20260418-104033 / candidate_version=20260418-111312 / candidate_is_newer=true / drain_active=true / running_task_count=1 / can_upgrade=false / ghost_running_detected=false`
- `test`: `current_version=20260418-111312 / candidate_version=20260418-111312 / running_task_count=0 / ghost_running_detected=false`
- `test` 原型图：`T17/T18/T19 = blocked / upstream=T20 / blocking_reason=upstream_failed`
- 当天 daily 仍保持 `completed`，学习报告目录保持齐全

## Next

- 等 `prod` idle watcher 在空窗把 `20260418-111312` apply 到 live
- 切版后复跑 `current-version smoke / recent-failure` 合同
- 继续观察 `test` 每次部署后的 `T9` ghost 是否还会复现，必要时把 post-deploy repair 继续沉成更正式的合同
- memory_ref: `.codex/memory/2026-04/2026-04-18.md`

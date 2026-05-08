# Continuous Improvement Report

- generated_at: `2026-04-18T23:56:30+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260418-70b290a7`
- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-18.md`

## 本轮推进
- 我把 `workflow_devmate` 的 `V4-R1` 协作泳道优先级补丁收口到 `workflow_devmate@96672c1 -> workflow_code@96672c1`，不再让这批实现继续挂在 `ahead_dirty`。
- 我没有停在 helper 结果确认层，而是补齐了正式验证、提交、根仓同步、`test` 部署、`prod candidate=20260418-235338` 刷新，以及其余 `5` 个 developer workspace 的 bootstrap/refresh。
- 当前协作泳道首屏修复已经进入 `test/candidate`：首屏只保留有 `running/queued` 的 active helper lane，历史 `failed/blocked` 残留改为折叠展示。

## 版本判断
- 当前版本继续 `stay(V4)`，当前最高价值泳道继续保持 `UCD/设计优化`，生命周期阶段继续保持 `基于基线测试`；但我把这轮明确记成 `开发实现 / 发布推进`。
- 当前 active 需求评估：
- `V4-R1`: `in_progress / 96% / eta=2026-04-19 / 未超时`
- `V4-R2`: `in_progress / 60% / eta=2026-04-20 / 未超时`
- `V4-R3`: `in_progress / 99% / eta=2026-04-20 / 未超时`
- `V4-R4`: `completed / 100% / eta=2026-04-17 / 未超时`
- `V4-R5`: `in_progress / 15% / eta=2026-04-19 / 未超时`
- `next_activation_ready=false`，`V5` 仍是 `activation_readiness=draft`；本轮没有需求超时，不新增 AAR。

## 发布边界与 live 真相
- 发布边界已经回到 `root_sync_state=clean_synced / workspace_head=code_root_head=96672c1 / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`。
- `manage_developer_workspace.py --root .running/control/runtime/prod status` 当前返回 `developer_workspace_count=6 / clean_synced=6`；`pm-main / workflow_devmate / workflow_bugmate / workflow_qualitymate / workflow_testmate / workflow_ucdmate` 已全部追平到 `96672c1`。
- `prod(8090)` 当前仍是 `current_version=20260418-202109`，但 `candidate_version=20260418-235338` 已更高：`candidate_is_newer=true / drain_active=true / running_task_count=1 / can_upgrade=false / ghost_running_detected=false`。
- `test(8092)` 当前已对齐到 `current_version=20260418-235338 / running_task_count=0 / ghost_running_detected=false`；`deploy-20260418-235338.json` 记录了 post-deploy ghost repair 成功。
- 当前主线出口仍成立：`workflow` 主线 `node-sti-20260418-70b290a7` 仍在 `running`，下一条 mainline `node-sti-20260418-a9680d39` 和保底 `node-sti-20260418-550e5b88` 都在 `ready`。

## 验证
- `.repository/workflow_devmate/.test/20260418-234632-564/report.md`
- `.repository/workflow_devmate/.test/20260418-234645-833/report.md`
- `.repository/workflow_devmate/.test/20260418-234655-399/report.md`
- `.repository/workflow_devmate/.test/runs/workflow-gate-acceptance-20260418-235119.md`
- `.running/control/logs/test/deploy-20260418-235338.json`
- `git -C .repository/workflow_devmate rev-parse --short HEAD`
- `git -C D:/code/AI/J-Agents/workflow_code rev-parse --short HEAD`
- `python ../workflow_code/scripts/manage_developer_workspace.py --root .running/control/runtime/prod status`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8092/api/status`
- `http://127.0.0.1:8092/api/runtime-upgrade/status`

## 风险与下一步
- 当前受控 warning 仍是手工 `create_assignment_node` 的 non-ASCII `node_name/node_goal` 可能在 live 节点里落成 `?`；这轮实现没有被它卡住，但若后续 live 回归显示 prompt 理解受影响，下一轮先收这条 API decode 坑。
- 下一步优先等 idle watcher 在空窗把 `candidate=20260418-235338` 切进 `prod`。
- 切版后第一优先复跑 live current-version smoke，并在真实 `task-center` 上确认协作泳道首屏只剩 active helper lane，历史残留已经降到折叠区。

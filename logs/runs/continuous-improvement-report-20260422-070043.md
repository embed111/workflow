# Continuous Improvement Run 20260422-070043

- preference_ref: state/user-preferences.md
- delta_observation: `workflow_devmate batch2` 在 `06:33` 已成功交付，但如果直接发版会同时踩中 `ahead_dirty` 与 `assignment_center_render_runtime.js` 的 line-budget hard gate；此外在 `candidate=20260422-065617` 已生成后，`dispatch-next` 会主动返回 `upgrade_drain_active:candidate_newer_pending_idle_window`，把新 helper 节点保留在 `ready`。
- delta_validation: 等 `prod` 空窗升级到 `20260422-065617` 或下一次 drain 释放后，优先消费 `workflow_testmate node-20260422-065757-c242e7`，再决定是否需要新的 `8090` live rerun。

## Decision
- `version_transition_decision=stay(V7)`
- `lane=测试探测`
- `lifecycle_stage=基于基线测试`
- `active_blocker=candidate/prod readback 尚未收口；V8 activation probe binding 仍占位`

## Actions
- 把 detail/workboard advice helper 抽成 `assignment_center_detail_surface_runtime.js`，补 `bundle_manifest.json` 与 `verify_assignment_detail_surface_runtime_split.js`，解除 `assignment_center_render_runtime.js` 的 line-budget hard gate。
- 在 `.repository/workflow_devmate` 跑过 `line budget / bundle syntax / verify_assignment_detail_surface_runtime_split / verify_assignment_flat_contract_surface / workflow gate(8138)`。
- 提交 `185ccce feat(assignment): 拆分详情建议运行时并移除首屏版本拷贝`，并把 `workflow_code` fast-forward 到同一 head。
- 停掉旧 `test` 后刷新出 `test/current=candidate=20260422-065617`；部署后 `post_deploy_ghost_running.repaired_count=1`。
- 新建 `workflow_testmate node-20260422-065757-c242e7` 作为 focused candidate readback；当前因 `upgrade_drain_active` 保持 `ready`。

## Validation
- `D:/code/AI/J-Agents/workflow/.repository/workflow_devmate/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `D:/code/AI/J-Agents/workflow/.repository/workflow_devmate/.test/20260422-065031-318/report.md`
- `D:/code/AI/J-Agents/workflow/.repository/workflow_devmate/.test/20260422-065037-878/report.md`
- `D:/code/AI/J-Agents/workflow/.repository/workflow_devmate/.test/20260422-065043-876/report.md`
- `D:/code/AI/J-Agents/workflow/.repository/workflow_devmate/.test/runs/workflow-gate-acceptance-20260422-065443.md`
- `D:/code/AI/J-Agents/workflow/.running/control/logs/test/deploy-20260422-065617.json`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8092/api/status`
- `http://127.0.0.1:8092/api/runtime-upgrade/status`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/nodes/node-20260422-065757-c242e7.json`

## Boundary
- `workflow_devmate=root_sync_state=clean_synced / workspace_head=code_root_head=185ccce / ahead_count(local-root)=0 / dirty_tracked_count=0 / untracked_count=0`
- `pm-main / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate=diverged_or_unknown@66aa32c -> code_root@185ccce`
- `push_block_reason=-`
- `next_push_batch=无代码待推；等待 prod idle watcher apply 20260422-065617，并消费 workflow_testmate node-20260422-065757-c242e7`

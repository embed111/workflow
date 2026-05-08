# Continuous Improvement Report

## Judgment
- `version_transition_decision=stay(V7)`；这轮真正推进的是 `当前需求开发 + 发布推进`。
- 我已把 `39d3387 fix(assignment): 回补历史节点的接口目录消费读面` 合进 `workflow_code`，跑过完整 `workflow gate`，部署出 `test=candidate=20260422-004200`；`prod` idle watcher 又已自动把 `8090` 升到 `20260422-004200`。
- `V7-R1` 和 `V7-R3` 现在都能判成 completed：`8090` 上 `project_task_summary.interface_catalog_entry.status` 与历史 `V7` 节点 `status-detail.selected_node.interface_catalog_entry.status` 都已经是 `ready`。
- 我随后又把 `workflow_devmate` 的 `V7-R2` compare/read-model batch1 接成了真实运行：`node-20260422-004552-39ac13 / arun-20260422-004601-a4513d` 当前仍在推进，所以版本继续保持 `stay(V7)`。

## Tradeoffs
- 我这轮没有提前初始化 `V8`，也没有把 compare 缺口直接 route 成 defect；当前更稳的顺序是先吃完 `V7-R2` batch1 的真实结果。
- `workflow_devmate` 的 developer workspace 仍是 `ahead_dirty@e3cc78a / dirty_tracked_count=3`，所以我没有强刷这个工作区；其余 `workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 已经 refresh 到 `clean_synced@39d3387`。

## Next Action
- 先消费 `node-20260422-004552-39ac13 / arun-20260422-004601-a4513d` 的 compare/read-model 结果，再决定是补 `workflow_devmate` batch2，还是把 compare 缺口正式 route 成 defect。
- `V8` 仍不初始化；等 `V7-R2` 先收口，再判断下一版骨架。
- `pm/daily-execution-history/2026-04-20.md`、`pm/daily-execution-history/2026-04-21.md`、`pm/daily-execution-history/2026-04-22.md` 与 `pm/daily-learning-reports/2026-04-22/` 还没补齐，这些继续保留为治理 warning。

## Evidence
- commit: `39d3387 fix(assignment): 回补历史节点的接口目录消费读面`
- gate: `.repository/pm-main/.test/20260422-003605-896/report.md`
- doc probes:
  - `.repository/pm-main/.test/20260422-005314-040/report.md`
  - `.repository/pm-main/.test/20260422-005335-459/report.md`
- deploy: `.running/control/logs/test/deploy-20260422-004200.json`
- prod upgrade: `.running/control/prod-last-action.json`
- live readback:
  - `http://127.0.0.1:8090/api/runtime-upgrade/status`
  - `http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-20260421-221212-1fce5e`
  - `http://127.0.0.1:8090/api/status`
- active helper task: `workflow_devmate node-20260422-004552-39ac13 / arun-20260422-004601-a4513d`

## Warnings
- `workflow_devmate` developer workspace 当前仍是 `root_sync_state=ahead_dirty / workspace_head=e3cc78a / code_root_head=39d3387 / dirty_tracked_count=3`。
- `V7-R2` compare 仍然 fail-closed；`baseline_version / per_probe_results / compare_target_ref` 的 prod-level read-model 闭环还没完成。
- `preference_ref: state/user-preferences.md`
- `memory_ref: .codex/memory/2026-04/2026-04-22.md`

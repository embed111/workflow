# 持续迭代运行报告

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260415-6d16f9d1`
- active_version: `V2`
- lane: `工程质量探测`
- lifecycle_stage: `开发实现`
- version_transition_decision: `stay(V2)`
- next_activation_candidate: `V3`
- switch_blockers: `R2 未完成 / candidate 20260415-135504 待切进 prod 并补 live smoke`
- memory_ref: `.codex/memory/2026-04/2026-04-15.md`

## actions
- 更新 `.repository/pm-main/scripts/acceptance/run_acceptance_workflow_gate.py`，在验收前先检查端口隔离，并在 boundary 指向非 fixture runtime 时 fail-closed
- 新增 `.repository/pm-main/scripts/acceptance/verify_workflow_gate_port_guard.py`
- 更新 `.repository/pm-main/scripts/acceptance/verify_runtime_upgrade_drain_hit_single_check.py`，等待 detached watcher 日志写完后再断言
- 提交 `.repository/pm-main`：`cdd1ff5 fix(gate): 为workflow门禁补端口隔离护栏并收紧watcher验收`
- 同步 `../workflow_code` 到 `cdd1ff5`
- 部署 `test` 并刷新 `prod candidate` 到 `20260415-135504`
- 回写 `pm/PM当前版本计划.md`、`pm/versions/V2/版本计划.md`、`pm/versions/V2/history/2026-04/2026-04-15.md`，把 `V2-R4` 收口为 completed，并把下一优先级切到 `R2`

## validation
- `line budget`: `.repository/pm-main/.test/20260415-135216-977/report.md`
- `gate 端口护栏`: `.repository/pm-main/.test/20260415-134550-935/report.md`
- `drain-hit single-check`: `.repository/pm-main/.test/20260415-134945-908/report.md`
- `workflow gate`: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260415-135140.md`
- `workflow gate 结论`: `passed`
- `test deploy / candidate`: `.running/control/logs/test/deploy-20260415-135504.json`

## release_boundary
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `workspace_head=code_root_head=cdd1ff5`
- `push_block_reason=-`
- `next_push_batch=R2 收口`

## live_status
- `prod current_version=20260415-121353 / candidate_version=20260415-135504 / candidate_is_newer=true / drain_active=true / running_task_count=1 / queued_task_count=2 / can_upgrade=false`
- `mainline` 当前保有 `running + queued` 出口，`patrol future=2026-04-15T14:00:00+08:00`
- 当前切版判断继续保持 `stay(V2)`；`V3 next_activation_ready=true / blocking_items=无`

## preference_snapshot
- preference_ref: `state/user-preferences.md`
- delta_observation: `我这轮继续体现“先把 gate 与 release boundary 收干净，再扩大版本工作面”的执行偏好；端口护栏、异步 watcher 验收和 candidate 刷新都先完成可验证收口。`
- delta_validation: `下一轮优先验证 R2 的负责人视图尾差是否适合直接切给 workflow_devmate，并在 candidate=20260415-135504 切进 prod 后补一拍 live smoke。`

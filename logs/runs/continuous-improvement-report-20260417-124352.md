# Continuous Improvement Report

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260417-c1ec4ca8`
- phase: `开发实现 -> 基于基线测试`
- lane: `UCD/设计优化`
- root_sync_state: `clean_synced`
- ahead_count: `0`
- dirty_tracked_count: `0`
- untracked_count: `0`
- push_block_reason: `-`
- next_push_batch: `等待 idle watcher 在空窗把 20260417-124332 切进 live；切版后优先复跑 V4 current-version smoke，并确认 workboard 紧凑摘要没有回退`
- memory_ref: `.codex/memory/2026-04/2026-04-17.md`

## 本轮推进
- 我把 `task-center` 默认 `workboard` 场景里重复占首屏的“共享阶段”大卡收成紧凑摘要，只在切到 `graph` 或选中节点时保留完整卡片。
- 我新增 `verify_assignment_surface_shell_compact_rules.js` 并接进 `workflow gate`，把这条 UCD 合同收成默认 gate 资产。
- 我同步扩展了 `run_acceptance_assignment_center_browser.py` 的 `surface_compact` probe case，给后续 `V4-R4` 的截图回归预埋真实场景。
- 我把代码提交并收口到 `.repository/pm-main@36b813b / ../workflow_code@36b813b`，重新部署 `test`，刷新出新的 `prod candidate=20260417-124332`。

## 当前 Active 需求评估
- `V4-R1`: `in_progress / 35% / eta=2026-04-19 / 未超时`。第一条真实 UCD 修复切片已落地，下一步是让 `candidate=20260417-124332` 切进 live，并继续清 browser acceptance 夹具。
- `V4-R2`: `planned / 5% / eta=2026-04-20 / 未超时`。继续冻结为第二优先切片，等 `V4-R1` 首批 probe 收口后再开批。
- `V4-R3`: `planned / 10% / eta=2026-04-20 / 未超时`。inventory 入口已在矩阵里，尚未进入首批实现。
- `V4-R4`: `planned / 10% / eta=2026-04-20 / 未超时`。真实浏览器截图 acceptance 仍被本机 `msedge --headless` 超时夹具卡住，下一步继续消这条旧债。
- `version_transition_decision=stay(V4)`；`V5` 继续保持 `backlog activation_readiness=draft`。

## 验证
- `python scripts/quality/check_workspace_line_budget.py --root .`
- `python scripts/acceptance/verify_assignment_center_view_tabs_assets.py`
- `node scripts/acceptance/verify_assignment_workboard_layout_rules.js`
- `node scripts/acceptance/verify_assignment_surface_shell_compact_rules.js`
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .repository/pm-main/scripts/deploy_workflow_env.ps1 -Environment test`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8090/api/schedules`

## 风险与下一步
- 当前 `prod=current_version=20260417-115812`，`candidate_version=20260417-124332`，因为 `running_task_count=1` 仍保持 `drain_active=true`；我没有在本轮主动触发 `/api/runtime-upgrade/apply`。
- 本机 `run_acceptance_assignment_center_browser.py` 仍稳定卡在 `msedge --headless` 截图超时；这条夹具阻塞不影响本轮 gate / deploy 收口，但仍是 `V4-R4` 需要继续处理的真风险。
- 下一轮优先盯 `candidate=20260417-124332` 的空窗切版，并继续把 browser harness 诊断或后续 UCD 深化切给 `workflow_ucdmate / workflow_devmate`。

# continuous-improvement-report-20260423-130143

- preference_ref: `state/user-preferences.md`
- delta_observation: 本轮优先级从继续追 helper batch 切到了 `V9-R4` 的 schedule 断链修复；`08:17` 之后 schedule 只停在 `trigger_hit` 的风险已经被收成代码修复、专项 probe 和 root-sync。
- delta_validation: 下一轮先把完整 `workflow gate` 的 harness 级 `Remote end closed connection without response` 尾部噪音收成 clean run，再决定是否刷新 `test/prod candidate`，随后继续回收 `V9-R2 / V9-R5` 结果。

## 结论
- `version_transition_decision=stay(V9)`。
- 当前更高价值切片不是继续扩 `V9-R2 / V9-R5`，而是先修掉会直接掐住 active 版本推进的 schedule 静默断链。
- `pm-main` 与本机 `workflow_code` 已重新对齐到 `clean_synced@4b0eedf`；这轮没有代码待推。

## 关键证据
- `.repository/pm-main/src/workflow_app/server/services/schedule_trigger_progress_runtime.py`
- `.repository/pm-main/scripts/acceptance/verify_schedule_pending_trigger_replaced_with_preview_status.py`
- `.repository/pm-main/scripts/acceptance/workflow_gate_probe_registry.py`
- `.repository/pm-main/.test/20260423-124208-277/report.md`
- `.repository/pm-main/.test/20260423-124222-864/report.md`
- `.repository/pm-main/.test/20260423-124222-933/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260423-125549.md`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`

## 下一步
1. 先把完整 `workflow gate` 的 harness 尾部断连收成 clean run，再决定是否刷新 `test/prod candidate`
2. 继续回收 `V9-R2 / V9-R5` 的 batch 结果并写回 active 版本真相

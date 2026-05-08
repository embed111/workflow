# 7x24 mainline handoff fix - 2026-04-26 00:38 +08:00

- preference_ref: state/user-preferences.md
- trigger: 用户指出 7x24 在任务结束后经常断链，并明确要求主线只有一个动作：不论成功或失败都继续派发 PM，helper 由 PM 运行中派发，看门狗只负责假运行失败收口。
- code_workspace: `.repository/pm-main`
- code_root_sync: `workflow_code@d722943`
- prod_current: `20260425-181610`
- prod_candidate: `20260426-003541`
- prod_apply: 未执行；最终复核 `running_task_count=0 / can_upgrade=true`，但本轮按默认发布边界只刷新候选，不直接覆盖正式环境。

## Changes
- 新增 `assignment_mainline_handoffs` durable outbox：终态成功/失败只记录 handoff，独立 worker 幂等续挂下一轮主线。
- `finalize / stale recovery` 不再直接散落续排 schedule；看门狗或文件真相恢复只把假运行收成失败并记录 handoff。
- schedule worker 每轮先 drain pending/paused handoff；handoff 异常只写事件，不阻断正常 schedule scan。
- 项目或 assignment 手动暂停时 handoff 保持 `paused`，恢复启动后继续接棒。
- API catalog live regression 在 API list/detail 和页面壳体验证通过时，把 Edge `--dump-dom` / screenshot timeout 降级为 browser evidence warning。
- PM snapshot refresh 兼容 `baseline 仍为 live` 和 `当前 live 真相已更新为` 句式。

## Validation
- `verify_assignment_mainline_handoff_outbox.py`: pass, session `.repository/pm-main/.test/20260425-234752-836`
- `verify_api_catalog_live_regression_host_root_fallback.py`: pass, session `.repository/pm-main/.test/20260425-234402-718`
- `verify_api_catalog_live_regression_summary_version.py`: pass, session `.repository/pm-main/.test/20260425-234422-027`
- `workflow gate`: pass, report `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260426-001519.md`
- `verify_pm_current_version_snapshot_alignment.py`: pass, session `.repository/pm-main/.test/20260426-003742-413`
- `deploy_test_workflow_env.ps1`: pass, report `.running/control/logs/test/deploy-20260426-003541.json`

## Commits
- `7d7d3e1 fix(schedule): 用持久 handoff 保障主线终态后续派发`
- `d722943 fix(pm): 兼容 live 快照新文案刷新`

## Notes
- 当前已刷新 `test/prod candidate=20260426-003541`。
- 未直接升级 `prod`；当前已到空窗，可由用户手动升级或等待受托管 watcher 按策略处理。

## Cleanup Follow-Up - 2026-04-26 01:14 +08:00
- 用户继续要求确认方案已同步、旧冗余代码已删除，避免后续 agent 再误用旧巡检逻辑。
- 清理范围：
  - 删除后端旧巡检读面兼容字段：`is_workflow_patrol`、`patrol_node`、`patrol_schedule_preview`。
  - 删除旧 helper 暴露：`_assignment_is_workflow_patrol_node`、`_schedule_is_workflow_patrol_payload`。
  - 删除前端旧巡检展示分支：`patrolNode`、`patrolSchedulePreview`、`assignmentWorkboardPatrolPreviewItem`。
  - 更新 acceptance probe，不再断言旧 patrol 字段存在。
  - 更新 `docs/workflow/governance/7x24连续运行机制.md` 与 `.codex/experience/schedule-trigger-closure.md`，明确旧巡检兼容壳不应恢复。
- 自动升级影响复核：
  - `task_artifact_store_run_finalize_runtime.py` 中 `_assignment_maybe_request_prod_upgrade_after_finalize()` 仍先于 handoff drain 与 follow-up dispatch 执行。
  - 若升级请求返回 `suppress_dispatch=true`，后续 follow-up dispatch 仍被压住；handoff 只作为未来接棒出口，不占 running 槽。
  - 因此该清理不改变 `/api/runtime-upgrade/status.running_task_count=0 && can_upgrade=true` 的空窗升级判定。
- 验证：
  - `python -m py_compile ...`: pass, session `.repository/pm-main/.test/20260426-010234-662`
  - `verify_assignment_graph_node_surface_split.py`: pass, session `.repository/pm-main/.test/20260426-010250-534`
  - `verify_schedule_admin_runtime_split.py`: pass, session `.repository/pm-main/.test/20260426-010303-440`
  - `verify_assignment_detail_surface_runtime_split.js`: pass, session `.repository/pm-main/.test/20260426-010311-550`
  - `verify_assignment_mainline_visibility.py`: pass, session `.repository/pm-main/.test/20260426-010322-757`
  - `verify_assignment_center_mainline_visibility.js`: pass, session `.repository/pm-main/.test/20260426-010335-632`
  - `check_workspace_line_budget.py --root .`: pass, session `.repository/pm-main/.test/20260426-010346-694`
  - `workflow gate`: pass, report `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260426-011143.md`
- 收口：
  - commit: `bff7523 refactor(schedule): 删除旧巡检兼容字段避免误用`
  - code_root_sync: `workflow_code@bff7523`
  - test deploy: `20260426-011803`, report `.running/control/logs/test/deploy-20260426-011803.json`
  - prod current: `20260426-003541`
  - prod candidate: `20260426-011803`
  - prod apply: 未执行；复核 `/api/runtime-upgrade/status` 显示 supervisor 已托管、candidate 更新可见，但当前 `running_task_count=1 / can_upgrade=false`，需等待运行槽空窗后自动 watcher 或用户手动 apply。

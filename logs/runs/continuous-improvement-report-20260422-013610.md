# Continuous Improvement Report

## Judgment
- `version_transition_decision=stay(V7)`。这轮我没有切版，而是把 `V7-R5` 的 project lifecycle contract 和 `V7-R2` 的 compare batch1 一起推进到新的 `test/prod candidate=20260422-013408`。
- `V7-R5` 已经不再是“没有 API”：我补上了正式 `DELETE /api/projects/{project_id}`，并把 `workflow` 内建项目禁删、活跃任务 fail-closed 和 `verify_project_lifecycle_delete.py` 一起做成了门禁。
- `V7-R2` 也不再是“compare 字段缺失”：`workflow_devmate` 的 batch1 已把 compare read-model 和 compare card 落成代码，当前剩余 blocker 已被收口为 `stale_per_probe_results`，说明问题已经缩到“旧 baseline artifact 还没跟上”，不是 surface 本身没做。

## Tradeoffs
- 我没有在 `compare` helper 还没交付时提前转去 `V7-R4` 或 `V7-R7`，因为那会把 critical path 拉散；先把 compare 做成精确 fail-closed blocker，再补生命周期 contract，是当前更值的一刀。
- 我也没有把 `prod` 还没升级的 candidate 说成“已经上线”。当前 `prod` 仍是 `20260422-004200`，`candidate=20260422-013408` 更高，`drain_active=true`，所以这轮收口停在 candidate，不抢空窗升级。

## Next Action
- 先等 `prod` 空窗升级到 `20260422-013408`，然后复查两件事：
  - `8090` 上的 compare surface 是否仍只报 `stale_per_probe_results`
  - `DELETE /api/projects/{project_id}` 在 deployed runtime 上是否按 contract 返回
- 如果 compare 仍只卡旧 artifact，我下一步就切一条 version-matched `api_catalog_live_regression` batch，把这条 stale blocker 清掉，而不是再补第二层 compare UI。
- `V8` 继续保持 `planned`；只有当 `V7-R2 / V7-R5` 在 prod 对齐、`V7-R4 / V7-R7` 进入明确批次后，我才会重开切版判断。

## Evidence
- code + root-sync:
  - `.repository/pm-main@79fc45f feat(projects): 补齐项目删除生命周期 contract 与门禁探针`
  - `.repository/workflow_devmate@209954f feat(api-catalog): 补齐接口对比读面与 compare 卡`
  - `workflow_code@972cebf`
- validation:
  - `.repository/pm-main/.test/20260422-011142-943/report.md`
  - `.repository/pm-main/.test/20260422-011155-478/report.md`
  - `.repository/pm-main/.test/20260422-011207-552/report.md`
  - `.repository/pm-main/.test/20260422-011954-857/report.md`
  - `.repository/pm-main/.test/20260422-012004-748/report.md`
  - `.repository/workflow_devmate/.test/20260422-012739-666/report.md`
  - `.repository/workflow_devmate/.test/20260422-012750-462/report.md`
- deploy:
  - `.running/control/logs/test/deploy-20260422-012556.json`
  - `.running/control/logs/test/deploy-20260422-013408.json`
- live truth:
  - `http://127.0.0.1:8090/api/runtime-upgrade/status`
  - `http://127.0.0.1:8090/api/status`
  - `http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-20260422-004552-39ac13`
  - `state/developer-workspaces.json`

## Warnings
- `prod` 当前仍是 `20260422-004200`；`candidate=20260422-013408` 已更高，且 `running_task_count=1`，所以这轮还不能把 compare/lifecycle 当成现网已对齐。
- `pm/daily-execution-history/2026-04-20.md`、`pm/daily-execution-history/2026-04-21.md`、`pm/daily-execution-history/2026-04-22.md` 与 `pm/daily-learning-reports/2026-04-22/` 仍未补齐。

- preference_ref: state/user-preferences.md
- delta_observation: 当 helper 已经把 blocker 收成代码级 fail-closed 结果时，我这轮继续优先做 source-workspace commit、根仓快进、test/candidate 刷新和全体 developer workspace refresh，而不是把 `ahead_dirty` 或 stale workspace 留到下一轮。
- delta_validation: 下一轮直接以 `candidate=20260422-013408` 的 prod apply 后读面为准；若 compare 仍只卡旧 artifact，就切 version-matched live regression batch，而不是重做 compare surface。
- memory_ref: `.codex/memory/2026-04/2026-04-22.md`

# Continuous Improvement Report

- version_transition_decision: `stay(V8)`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- root_sync_state: `clean_synced`
- ahead_count: `0`
- dirty_tracked_count: `0`
- untracked_count: `0`
- memory_ref: `.codex/memory/2026-04/2026-04-22.md`

## 判断

我继续保持 `stay(V8)`。本轮真正推进的是 `V8-R6` 的 self-readback live evidence 发现链：我先用 `workflow_testmate` 在 `8092` 证明 current-baseline exact rerun 会正常生成新 `summary.json`，再把代码补到既能发现 developer workspace `.test` 产物，也能在 deployed runtime 里通过 `WORKFLOW_RUNTIME_SOURCE_ROOT` 反解真实 `.repository`。`V9` 仍然 `next_activation_ready=false`，当前没有切版条件。

## 取舍

我没有继续 front-run `V8-R3` 的 targeted regression。当前最高价值不是再开新 helper，而是先把 `V8-R6` 的 release boundary 说明白：`9d966e4` 已修正 developer workspace summary 发现并加固 `verify_api_catalog_self_readback_closure.py / verify_assignment_role_contract_runtime.py`，`1f34c25` 又补了 deployed runtime 的 `source_root` 反解。两刀都已经从 `pm-main` 同步到 `workflow_code`，但第二刀还没进新的 `test/current`，因为完整 `workflow gate` 这时被 unrelated 的 `assignment_cross_process_dispatch_claim` probe 挡住；那条失败实际命中 `upgrade_drain_active`，不是 self-readback 回归本身。

## 下一动作

1. 先把 `assignment_cross_process_dispatch_claim` 被 `upgrade_drain_active` 误伤的 unrelated gate blocker 隔离出来。
2. gate 重新转绿后，把 `1f34c25` 部署到 `test/current=candidate`，再用 `workflow_testmate` 在 `8092` 对新版本补一条 exact `verify_api_catalog_live_regression.py`。
3. 回读 `8092/8090` 的 `platform.interfaces.list/detail` 与 `project_task_summary.interface_catalog_entry`；只有 `V8-R6` 真转 `ready` 后，才接 `V8-R3` targeted regression。

## 证据

- `pm-main@9d966e4`：`fix(api-catalog): 补齐developer workspace自读回summary发现并加固相关验收`
- `pm-main@1f34c25`：`fix(api-catalog): 让部署副本按source_root发现developer workspace summary`
- `workflow_code@1f34c25` 已 fast-forward 对齐
- `python scripts/quality/check_workspace_line_budget.py --root .`
- `.repository/pm-main/.test/20260422-155223-285/report.md`
- `.repository/pm-main/.test/20260422-155854-614/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260422-160335.md`
- `.running/control/logs/test/deploy-20260422-160549.json`
- `.repository/workflow_testmate/.test/20260422-160614-054/report.md`
- 定向 deployed-like 解析已指向 `D:/code/AI/J-Agents/workflow/.repository/workflow_testmate/.test/20260422-160614-054/artifacts/api-catalog-live-regression/summary.json`

## 版本更新

- `V8-R1=in_progress/90%/最近更新=2026-04-22T12:45:44+08:00/eta=2026-04-23/未超时`
- `V8-R2=in_progress/55%/最近更新=2026-04-22T12:45:44+08:00/eta=2026-04-23/未超时`
- `V8-R3=in_progress/80%/最近更新=2026-04-22T15:26:31+08:00/eta=2026-04-24/未超时`
- `V8-R4=completed/100%/最近更新=2026-04-22T12:45:44+08:00/eta=已完成/未超时`
- `V8-R5=in_progress/75%/最近更新=2026-04-22T12:45:44+08:00/eta=2026-04-24/未超时`
- `V8-R6=in_progress/98%/最近更新=2026-04-22T16:15:40+08:00/eta=2026-04-24/未超时`
- `switch_blockers=V8-R2 / V8-R3 / V8-R5 / V8-R6`
- `recheck_trigger=assignment_cross_process_dispatch_claim` gate blocker 解开并重新部署 `1f34c25` 到 `test/current`

## Warnings

- `pm/daily-execution-history/2026-04-20.md` 仍缺失，`pm/daily-execution-history/2026-04-21.md`、`pm/daily-execution-history/2026-04-22.md` 仍未补齐。
- `pm/daily-learning-reports/2026-04-22/` 仍未补齐。
- `workflow_devmate` developer workspace 仍是 `ahead_dirty@52e2efb`。

# Continuous Improvement Report

判断：
- 我继续保持 `version_transition_decision=stay(V8)`；当前仍处在 `工程质量探测 / 基于基线测试`。
- 这轮主推进项是 `V8-R5`：我把 assignment/dashboard latency baseline 从一次性 point sample 推成了 `workflow gate` 的正式 probe，并补齐了 `prod/test` 两侧各 `5` 次采样证据。
- 下一拍我先补 `workflow latency` 基线读面，再补 `V8-R2` 的 project summary live regression；`V8-R3` 先不扩面。

取舍：
- 我没有重复上一轮的 api-catalog exact regression，也没有新起 helper 实现单，而是优先把 `measure_assignment_dashboard_latency.py` 的长期门禁价值做实，并顺手把 `pm version board` 的 parse-safe 红灯和五个 helper developer workspace 的 clean lag 一起收掉。
- 因为这轮是 acceptance/gate 资产变更，我先做 `py_compile`、`verify_assignment_dashboard_latency.py(prod/test)` 和完整 `workflow gate`，再提交 `7e9f0a4`、同步 `workflow_code`，最后刷新 `test/current=candidate=20260422-195204`。

必要证据：
- prod `5` 次采样 p95：`canonical_ticket=4.68ms / list_assignments=292.59ms / workboard_payload=2254.09ms / base_dashboard=98.35ms`
- test `5` 次采样 p95：`canonical_ticket=63.30ms / list_assignments=91.34ms / workboard_payload=1694.20ms / base_dashboard=115.10ms`
- gate：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260422-195018.md`
- deploy：`.running/control/logs/test/deploy-20260422-195204.json`
- 发布边界：`pm-main / workflow_code / workflow_devmate / workflow_bugmate / workflow_testmate / workflow_qualitymate / workflow_ucdmate = clean_synced@7e9f0a4`
- live：`prod current=20260422-183414 / candidate=20260422-195204 / candidate_is_newer=true / drain_active=true / running_task_count=1`

warning：
- `pm/daily-execution-history/2026-04-20.md`、`2026-04-21.md`、`2026-04-22.md` 仍未补齐。
- `pm/daily-learning-reports/2026-04-22/` 仍未补齐。

memory_ref: `.codex/memory/2026-04/2026-04-22.md`

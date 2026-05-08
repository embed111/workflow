# continuous-improvement-report

## 判断
- 我继续保持 `V5`，当前最高价值泳道仍是 `工程质量探测 / 发布边界收口`，不切版。
- 这轮不再重复上一轮的 browser acceptance split，而是直接打新的 Mandatory Gate blocker：`verify_pm_current_version_snapshot_refresh.py`。
- 下一动作已经收窄成三块：`schedule_service.py / workflow_env_common.ps1 / src/workflow_app/server/services/role_creation_service_parts/spec_and_reply_builder.py`。在 `Mandatory Gate` 继续转绿前，我不刷新新的 `test / prod candidate`。

## 推进
- 我把 `.repository/pm-main/scripts/acceptance/verify_pm_current_version_snapshot_refresh.py` 收成 `runner + support` 两层，新增 `.repository/pm-main/scripts/acceptance/pm_current_version_snapshot_refresh_support.py` 和 `.repository/pm-main/scripts/acceptance/verify_pm_current_version_snapshot_refresh_split.py`，并把新 split probe 挂进 `.repository/pm-main/scripts/acceptance/workflow_gate_probe_registry.py`。
- 中途我修掉了 runner 误指向自身导致的递归超时，并把 drift-refresh hook 断言改到 `workflow_env_json_and_paths.ps1` 的当前真相上。
- 这批代码已经提交为 `pm-main@7b702c8 refactor(acceptance): 拆分 PM current-version snapshot refresh probe 以压低门禁 blocker`，并同步到 `workflow_code@7b702c8`；当前 `pm-main / ../workflow_code` 已回到 `clean_synced`。

## 证据
- 定向验证：
  - `.repository/pm-main/.test/20260420-033451-579/report.md`
  - `.repository/pm-main/.test/20260420-033740-163/report.md`
  - `.repository/pm-main/.test/20260420-033752-064/report.md`
  - `.repository/pm-main/.test/20260420-033800-236/report.md`
- live 真相：
  - `/api/status` 当前为 `running_task_count=1 / queued_task_count=2 / active_agent_count=1`
  - `/api/runtime-upgrade/status` 当前为 `current_version=candidate_version=20260419-180446 / candidate_is_newer=false / can_upgrade=false / ghost_running_detected=false`
  - `next_activation_candidate=- / next_activation_ready=false`
- 门禁现状：
  - 最新 `line budget` 仍是 `mandatory_gate_pass=false`
  - `blocking_offender_count` 已从 `35` 降到 `34`
  - `verify_pm_current_version_snapshot_refresh.py` 已退出 `first_batch_targets`
  - 当前首批冻结对象改成 `schedule_service.py / workflow_env_common.ps1 / src/workflow_app/server/services/role_creation_service_parts/spec_and_reply_builder.py`

## 版本现场
- `version_transition_decision=stay(V5)`
- 当前需求评估：
  - `V5-R1=in_progress / 60% / 最近更新=2026-04-19T23:50:42+08:00 / eta=2026-04-21 / 未超时`
  - `V5-R2=in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
  - `V5-R3=in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
  - `V5-R4=in_progress / 96% / 最近更新=2026-04-19T23:50:42+08:00 / eta=2026-04-21 / 未超时`
  - `V5-R5=in_progress / 95% / 最近更新=2026-04-20T03:39:13+08:00 / eta=2026-04-21 / 未超时`
- `pm/daily-execution-history/2026-04-20.md` 仍缺失；今天的每日学习任务与真实学习报告还没收口，我这轮没有伪造 completed 记录。

## Snapshot Addendum
- preference_ref: state/user-preferences.md
- delta_observation: 用户继续要求每轮都必须是真推进、不要重复上一轮主产出；这轮我按新的 first batch blocker 改选了 snapshot refresh acceptance split，而不是重复 browser/runtime 那条线。
- delta_validation: 下一轮继续保持“先给判断、取舍和下一动作，再补最小证据”；若继续做代码切片，优先直接命中当前 first_batch_targets。
- memory_ref: .codex/memory/2026-04/2026-04-20.md

# Continuous Improvement Report

- generated_at: `2026-04-18T18:26:12+08:00`
- active_version: `V4`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- version_transition_decision: `stay(V4)`
- memory_ref: `.codex/memory/2026-04/2026-04-18.md`

## 本轮推进
- 我把 `ghost-repair settle` 的重复状态日志压缩收成 `.repository/pm-main@f0688fd / ../workflow_code@f0688fd`：
  - `scripts/apply_prod_candidate_when_idle.py` 现在会压缩连续相同的 `继续复核状态 / 假 running 修复后状态 / 修复后仍存在假 running` 日志块，只保留首组原始状态；状态变化或退出时，再补一条累计摘要。
  - `scripts/acceptance/verify_apply_prod_candidate_when_idle.py` 新增了 `repair_settle_log_compaction` probe，锁住这条 watcher 合同。
- 我把这批改动走完 `line budget -> verify_apply_prod_candidate_when_idle.py -> workflow gate -> test/candidate`，并把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 一起 refresh 回 `clean_synced@f0688fd`。

## 验证与发布
- `line budget`：`.repository/pm-main/.test/20260418-181803-642/report.md`
- `verify_apply_prod_candidate_when_idle.py`：`.repository/pm-main/.test/20260418-181816-380/report.md`
- `workflow gate`：`.repository/pm-main/.test/20260418-181900-326/report.md`
- `workflow gate run`：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260418-182238.md`
- `test / prod candidate`：`20260418-182357`
- `deploy report`：`.running/control/logs/test/deploy-20260418-182357.json`
- `developer workspace truth`：`manage_developer_workspace.py --root .running/control/runtime/prod status => developer_workspace_count=6 / clean_synced=6`

## 当前版本评估
- `V4-R1`：`in_progress / 90% / eta=2026-04-19 / 未超时`
- `V4-R2`：`in_progress / 60% / eta=2026-04-20 / 未超时`
- `V4-R3`：`in_progress / 99% / eta=2026-04-20 / 未超时`
- `V4-R4`：`completed / 100% / eta=2026-04-17 / 未超时`
- `AAR`：`无`
- `root_sync_state`：`clean_synced`
- `workspace_head`：`f0688fd`
- `code_root_head`：`f0688fd`

## 当前 live
- `prod`：`current=20260418-173831 / candidate=20260418-182357 / candidate_is_newer=true / running_task_count=1 / ghost_running_detected=false`
- `test`：`current=20260418-182357 / candidate_is_newer=false / running_task_count=0 / ghost_running_detected=false`
- `current mainline`：`node-sti-20260418-fb1d611d / running`
- `patrol`：`node-sti-20260418-c787c2d3 / ready`
- `remaining_risk`：旧 `prod` supervisor `20500` 仍在；下一次 idle watcher 升级要同时验证 `repair_settle_log_compaction` 与 `legacy_watchdog_apply_wait_clamp` 的 live 行为。

## 下一步
- 等 idle watcher 在空窗把 `candidate=20260418-182357` 切进 `prod`。
- 切版后第一优先复核 `logs/runs/prod-idle-upgrade-watchdog-live.md`，确认 live watcher 对 ghost-repair settle 只保留首组原始块并补累计摘要。
- 若 `182357` live 后仍有红点，我下一轮继续沿 `V4-R3` formal route 往下切；若通过，再判断是否把 `V4-R3` 收成 completed。

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: 本轮 candidate 生成后，5 个 helper developer workspace 一度因 code root 前进而被 `manage_developer_workspace` 判成 `diverged_or_unknown`；我已用 supported refresh 把它们拉回 `clean_synced@f0688fd`。
- delta_validation: 下一轮继续先核 `prod-idle-upgrade-watchdog-live.md` 与 `manage_developer_workspace.py --root .running/control/runtime/prod status`，确认 live watcher 日志和 helper workspace 真相都已追平。

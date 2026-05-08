# Continuous Improvement Report

- version_transition_decision: `stay(V8)`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- root_sync_state: `clean_synced`
- ahead_count: `0`
- dirty_tracked_count: `0`
- untracked_count: `0`
- push_block_reason: `-`
- next_push_batch: `无代码待推；下一批优先补 V8-R5 的 latency 基线与 dashboard/read 面测量，再补 V8-R2 的 project summary live regression，并视需要继续推进 V8-R3 的 project-ops canonical header / workboard trim。`
- memory_ref: `.codex/memory/2026-04/2026-04-22.md`

## 判断

我继续保持 `stay(V8)`。这轮不再复述上一拍的 `project-ops` gate 接线，而是直接把 `V8-R5/V8-R6` 的当前 baseline readback 重新拉回 live 真相：`20260422-183414` 上的 `platform.interfaces.detail` 原本还挂着旧 `20260422-182822` summary，我先用 supported exact live regression 在 `8092` 对新 baseline 重跑，随后 `8090/8092` 的 `latest_evidence / compare` 都回到 `ready`。同时，我确认 `workflow_devmate` 那批未提交 dirty 不是当前必须并主线的修复，已按 supported refresh 收口成 `clean_synced@e05d3d9`，不再把它保留成假 blocker。

## 本轮推进

- live 修复：我用 session `20260422-190305-163` 跑 `python scripts/acceptance/verify_api_catalog_live_regression.py --root . --base-url http://127.0.0.1:8092 --expected-version 20260422-183414`，生成新的 version-matched summary。
- readback 回正：随后回读 `8090/8092 /api/platform/interfaces/platform.interfaces.detail`，`api_catalog_live_regression` 从 `stale_per_probe_results` 翻到 `ready`，`latest_evidence` 和 `compare` 同时对齐 `baseline=20260422-183414`。
- helper 收口：我先对 `workflow_devmate` 的两处 dirty 文件做“不并主线”的判断，再清理工作树并用 supported `manage_developer_workspace.py bootstrap --developer-id workflow_devmate` 把它 refresh 到 `workflow_code@e05d3d9`；`state/developer-workspaces.json` 已回写成 `root_sync_state=clean_synced`。
- 版本约束更新：我把 `V8-R5` 的剩余 gap 从“self-readback / dirty delta 未决”收窄成“latency 基线与更多 live regression”，并同步更新当前版本快照、版本正文、history、经验卡和今日日记。

## 版本更新

- `V8-R1=in_progress/90%/最近更新=2026-04-22T12:45:44+08:00/eta=2026-04-23/未超时`
- `V8-R2=in_progress/75%/最近更新=2026-04-22T18:04:12+08:00/eta=2026-04-23/未超时`
- `V8-R3=in_progress/90%/最近更新=2026-04-22T17:30:41+08:00/eta=2026-04-24/未超时`
- `V8-R4=completed/100%/最近更新=2026-04-22T12:45:44+08:00/eta=已完成/未超时`
- `V8-R5=in_progress/90%/最近更新=2026-04-22T19:05:31+08:00/eta=2026-04-24/未超时`
- `V8-R6=completed/100%/最近更新=2026-04-22T17:00:39+08:00/eta=已完成/未超时`

## 切版判断

- `switch_blockers=V8-R2 / V8-R3 / V8-R5`
- `recheck_trigger=优先补 V8-R5 的 measure_assignment_dashboard_latency.py / workflow-latency-daily.json 读面，再补 V8-R2 的 project summary live regression，然后判断 V8-R3 是否继续推进 project-ops canonical header / workboard trim`
- `next_activation_candidate=V9 / next_activation_ready=false`

## 证据

- `.repository/pm-main/.test/20260422-190305-163/report.md`
- `.repository/pm-main/.test/20260422-190305-163/artifacts/api-catalog-live-regression/summary.json`
- `http://127.0.0.1:8090/api/platform/interfaces/platform.interfaces.detail`
- `http://127.0.0.1:8092/api/platform/interfaces/platform.interfaces.detail`
- `state/developer-workspaces.json`

## Warnings

- `pm/daily-execution-history/2026-04-20.md` 仍缺失，`pm/daily-execution-history/2026-04-21.md` 与 `pm/daily-execution-history/2026-04-22.md` 仍未补齐。
- `pm/daily-learning-reports/2026-04-22/` 仍未补齐。
- `workflow_bugmate / workflow_testmate / workflow_qualitymate / workflow_ucdmate` 仍停在 `3ac8be0` 的 clean lag，尚未 refresh 到 `e05d3d9`。
- `prod current=candidate=20260422-183414`，但当前主线仍在 `running_task_count=1`，所以 `can_upgrade=false` 只是当前运行中任务门禁，不再是 candidate 落后。

## Snapshot Addendum

- preference_ref: `state/user-preferences.md`
- delta_observation: 我这轮补跑了 `20260422-183414` 的 exact api-catalog live regression，并把 `platform.interfaces.detail` 的 live compare 从 stale 拉回 ready；`workflow_devmate` 也已从 `ahead_dirty@52e2efb` 收口为 `clean_synced@e05d3d9`。
- delta_validation: 下一轮优先补 `V8-R5` 的 latency 基线读面，再补 `V8-R2` 的 project summary live regression，并继续观察当前 mainline `node-sti-20260422-cd810ac9` 收尾后 `node-sti-20260422-37d24efe` 与 `sch-20260405-67a89536@2026-04-22T19:20:00+08:00` 的接力。

# workflow-pm-wake-summary 2026-04-12 21:26:05+08:00

- result: `继续推进`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- progress_item: `发布推进`
- memory_ref: `.codex/memory/2026-04/2026-04-12.md`

## 现场结论
- `.repository/pm-main` 与 `../workflow_code` 已同步到 `a3e5eda`，当前发布边界为 `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=a3e5eda / push_block_reason=- / next_push_batch=待切批`；`main...origin/main [ahead 23]` 继续只记为上游参考。
- `prod` 当前仍是 `20260412-201138`，新的 `prod candidate=20260412-211849` 已就绪，`candidate_is_newer=true / request_pending=false / drain_active=true / blocking_reason=running_tasks_present`。
- 当前现场为 `21:00 patrol running + 20:38 mainline ready + 21:20 patrol ready`，并仍保留主线 future `2026-04-12T21:27:00+08:00` 与保底 future `2026-04-12T21:40:00+08:00`；这不是 `0 running + ready pileup` 的假健康，不补新的主线入口。
- `pm持续唤醒 - workflow 主线巡检` 的最新 schedule 真相已经带出 `[upgrade_drain_active:candidate_newer_pending_idle_window]`，说明 `a3e5eda` 新增的 drain 命中 single-check 路径已经进入 live schedule 读链，而不再只是工作区里的待发布代码。
- 当前 `workflow_mainline_handoff_pending=true` 仍成立；但当前更高优先级已经从“等旧版 2 小时 watcher”切成“观察当前 patrol 收尾后，20:38 mainline 是否接棒，以及新的 single-check 能否更快把 `211849` 切进 prod”。

## 证据
- `http://127.0.0.1:8090/healthz`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/schedules`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `D:/code/AI/J-Agents/workflow/.running/control/prod-candidate.json`
- `D:/code/AI/J-Agents/workflow/.running/control/reports/test-gate-20260412-211849.json`
- `D:/code/AI/J-Agents/workflow/pm/PM当前版本计划.md`
- `D:/code/AI/J-Agents/workflow/pm/versions/V1/版本计划.md`

## Snapshot Addendum
- preference_ref: state/user-preferences.md
- delta_observation: 当前 `21:20` patrol 已被创建为 `ready` 且 schedule detail 明确写出 `upgrade_drain_active:candidate_newer_pending_idle_window`；`a3e5eda` 的新升级等待策略已经进入 live 真相，但当前 `21:00` patrol 仍在运行、`20:38` mainline 仍待接棒。
- delta_validation: 下一轮优先确认 `node-sti-20260412-85239674` 收尾后，`node-sti-20260412-697895a6` 是否优先被 dispatch，以及 `candidate=20260412-211849` 是否在 single-check/1h watcher 新口径下更快切进 `prod`。

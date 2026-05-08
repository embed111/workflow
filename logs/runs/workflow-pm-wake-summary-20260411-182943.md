# workflow-pm-wake-summary

- checked_at: `2026-04-11T18:36:32+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260411-b53fa2bf`
- run_id: `arun-20260411-182610-50dc4a`
- active_version: `V1`
- task_package: `V1-P2B 真相源统一 (V1-P2)`
- lane: `工程质量探测`
- lifecycle_stage: `变更控制`
- baseline: `prod=20260411-093051`
- preference_ref: `state/user-preferences.md`
- delta_observation: 当前真实阻塞仍是 live `prod=20260411-093051` 没在空窗切到 `candidate=20260411-173655`，而不是 `pm-main / workflow_code` 没同步；这轮保底已经 materialize 成 live running，而 `18:32` 主线也已经 materialize 成 ready waiting handoff，所以现场不是假健康。
- delta_validation: 我已重新核对 `pm-main / workflow_code` 的 release boundary、当前巡检 run 文件、任务图、两条 live schedules、升级门禁、prod 托管进程和 helper runtime 状态，并把最新快照回写到版本计划、月度现场和今日日记。
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`
- experience_refs:
  - `.codex/experience/runtime-upgrade-and-agent-monitoring.md`
  - `.codex/experience/schedule-trigger-closure.md`

## 巡检结论

这轮 `prod` 不是假健康。当前 live 现场已经收口为：

- `running`: 保底巡检 `node-sti-20260411-b53fa2bf / arun-20260411-182610-50dc4a`
- `ready`: 主线 `node-sti-20260411-9e003113 / [持续迭代] workflow / 2026-04-11 18:32:00`
- `future`: 当前为 `0`

我直接核了当前巡检 run 的磁盘真相：`run.json` 仍是 `status=running / provider_pid=33392 / latest_event_at=2026-04-11T18:36:32+08:00`，对应 dispatch 审计是 `aaud-20260411-182617-924099 @ 2026-04-11T18:26:10+08:00`。当前全局主图已经收口为 `1 running / 1 ready / 6 pending`，并且 `/api/status` 明确给出 `workflow_mainline_handoff_pending=true`、说明是“保底巡检仍在运行，真正的 [持续迭代] workflow 还在待执行”。所以这轮既不是“0 running + ready 堆积”的假健康，也没有丢掉下一棒出口。

当前 active 版本继续是 `V1`，本轮最高价值泳道继续是 `工程质量探测`，生命周期阶段继续是 `变更控制`。这轮最该推进的动作仍不是再挂新 helper，也不是自己触发正式升级，而是继续盯住 current patrol -> `18:32` 主线 -> idle upgrade 这条接力。

## 发布边界

当前真正的 release boundary 是：

- `developer_id=pm-main`
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `push_block_reason=-`
- `next_push_batch=待切批`
- `workspace_head=code_root_head=7822016`
- 上游参考：`pm-main / workflow_code -> ## main...origin/main [ahead 7]`

也就是说，本轮 schedule prompt 里继续出现的 `ahead 7` 只代表本机 `pm-main / workflow_code` 相对 `origin/main` 已有 7 个未上推的本地提交；相对本机代码根仓本身仍是 `clean_synced`，不构成本轮 dirty/ahead 异常。

## 升级门禁

这轮没有执行 `/api/runtime-upgrade/apply`。当前 `/api/runtime-upgrade/status` 是：

- `current_version=20260411-093051`
- `candidate_version=20260411-173655`
- `candidate_is_newer=true`
- `request_pending=false`
- `running_task_count=1`
- `blocking_reason=存在运行中任务，暂不可升级`
- `can_upgrade=false`

我还补核了托管链：

- `.running/control/prod-last-action.json` 仍显示最后一次成功升级完成于 `2026-04-11T01:35:04Z -> 20260411-093051`
- `start_workflow_env.ps1 -Environment prod -SkipBackfill` supervisor 进程仍在：`PID=38948`
- 当前 `launch_workflow.ps1` 子进程：`PID=44208`
- 当前 web 进程：`PID=63136`

所以这轮不存在“supervisor 缺失导致 watcher 根本不在”的误判；当前仍应继续由 `prod` supervisor 托管的 idle watcher 在真正空窗时发起升级，而不是由这条巡检节点自己 `apply`。但空窗已经晚于 `18:32` 主线 materialize，现场因此进入了“保底巡检 running + 主线 ready waiting handoff”的过渡态。

## 真相分叉

当前两条 live schedule prompt 仍写着旧 snapshot：

- `root_sync_state=ahead_clean`
- `ahead_count=7`
- `push_block_reason=unpushed_commits_present`

我已经再次确认，这不是本地 release boundary 重新失控，而是 live `prod=20260411-093051` 还在使用旧的 `release_boundary_service.py` 口径。当前工作区同名文件已经把 `origin/main ahead` 降级成上游参考；候选 `20260411-173655` 才携带了新逻辑，但尚未切入现网。

## Helper 判断

这轮我没有新挂 helper 任务，因为当前并不存在“执行者缺位就会断链”的现场：

- `agent_registry.runtime_status` 中 `workflow_bugmate / workflow_devmate / workflow_qualitymate / workflow_testmate` 当前都是 `idle`
- 这四个 helper 的最近更新时间仍是 `2026-04-11T17:01:10+08:00`
- 当前断点不在 helper 缺位，而在 old prod 仍会按 `20260411-093051` 的旧 release-boundary 语义回写 live schedule prompt

因此当前最值得做的不是再补派一个 helper，而是继续盯 `node-sti-20260411-b53fa2bf -> node-sti-20260411-9e003113` 这一棒，以及首个 idle 窗口里的正式升级。

## 下一次建议

- 主线下一观察点：当前已 materialize 为 `node-sti-20260411-9e003113`，等待当前巡检释放后接棒
- 保底下一观察点：预期当前巡检收尾后续挂到 `2026-04-11T19:32:00+08:00`；若主线 ready 已接棒后仍看不到新的保底 future，就按补链异常继续处理
- 升级观察点：当前巡检节点释放后、且没有新的 `workflow` live running 占住槽位的首个空窗，继续核对 idle watcher 是否把 `candidate=20260411-173655` 接入 live `prod`
- 异常门槛：
  - 如果 `node-sti-20260411-9e003113` 在当前巡检收尾后仍长期停在 `ready/queued`，就按 handoff 异常继续处理
  - 如果首个空窗后 `current_version` 仍停在 `20260411-093051`，或 ready 主线接棒后仍继续沿用旧 `ahead_clean / unpushed_commits_present` prompt，就把 `prod supervisor / idle watcher` 验证或重启提升为下一条受支持治理批次

## 证据

- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `docs/workflow/reports/7x24发布边界收口方案-20260409.md`
- `docs/workflow/governance/pm-version-live/2026-04/现场更新总览.md`
- `git -C .repository/pm-main status --short --branch`
- `git -C .repository/pm-main rev-parse --short HEAD`
- `git -C .repository/pm-main rev-list --left-right --count origin/main...main`
- `git -C ../workflow_code status --short --branch`
- `git -C ../workflow_code rev-parse --short HEAD`
- `git -C ../workflow_code rev-list --left-right --count origin/main...main`
- `Invoke-RestMethod 'http://127.0.0.1:8090/healthz'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-b53fa2bf'`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-182610-50dc4a/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-182610-50dc4a/events.log`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl`
- `.running/control/prod-last-action.json`
- `.running/control/instances/prod.json`
- `logs/runs/prod-idle-upgrade-watchdog-live.md`
- `Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -in 38948,44208,63136 }`
- `python -` 查询 `.running/control/runtime/prod/state/workflow.db` 中 helper `agent_registry.runtime_status`

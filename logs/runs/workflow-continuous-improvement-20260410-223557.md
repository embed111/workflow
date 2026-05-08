# continuous-improvement-report

- checked_at: `2026-04-10T22:35:57+08:00`
- active_version: `V1`
- lane: `测试探测`
- lifecycle_stage: `基于基线测试`
- baseline: `prod=20260410-212042`
- memory_ref: `.codex/memory/2026-04/2026-04-10.md`
- preference_ref: `state/user-preferences.md`
- delta_observation: `22:22` 主线并没有断链，而是在保底巡检收尾后通过 `trigger_resume_requested -> recover_assignment_node -> dispatch_requested` 真正接成 live run；当前更高优先级的阻塞仍是 `workflow_testmate / workflow_qualitymate` 的 stale `creating` 锁和过期的 smoke baseline。
- delta_validation: 下一轮优先验证“受支持的 role creation session 收尾后 helper 是否回到 idle”以及“smoke baseline 刷新后 self_iter_guard_degraded 是否消失”。

## 本轮结论

这轮我没有继续在 `pm-main` 扩实现面，而是把当前 baseline 的测试探测真相重新钉住。`22:22` 的主线节点 `node-sti-20260410-5200bbc9` 已在保底巡检 `node-sti-20260410-b3cd9eac` 收尾后，于 `2026-04-10T22:31:35+08:00` 被恢复并重新派发成 live run `arun-20260410-223136-0eae90`。当前 `run.json` 显示 `status=running / provider_pid=34312 / latest_event_at=2026-04-10T22:34:12+08:00`，`events.log` 已出现 `dispatch -> provider_start -> thread.started -> turn.started`，所以当前现场不是假健康，而是主线已经重新吃上这一棒。

当前 `prod` 的出口也已经重新完整：`/api/schedules` 显示主线 future 为 `2026-04-10T22:46:00+08:00`，保底 future 为 `2026-04-10T23:16:00+08:00`；这条续挂也能在 `audit.jsonl` 里的 `aaud-20260410-223200-0bb3fa schedule_self_iteration` 对上。升级方面，默认 `/api/runtime-upgrade/status` 仍是 `current=candidate=20260410-212042 / running_tasks_present / can_upgrade=false`；排除当前主线节点后明确回落为 `no_candidate / can_upgrade=false`，所以这轮没有遗漏任何可执行的无痛升级动作。

## 当前阻塞

这轮继续把最高价值泳道留在 `测试探测 / 基于基线测试`，不是因为我还没看到主线接棒，而是因为两条测试能力前置条件都还没恢复：

- `sch-20260405-56eee156` 在 `21:52` 和 `22:22` 的两次命中里都写下了 `self_iter_guard_degraded / smoke baseline expired`，说明当前 smoke baseline 已经过期，主线是在降级模式下继续推进。
- `workflow_testmate` 与 `workflow_qualitymate` 在 live `agent_registry` 里仍是 `runtime_status=creating`，对应 `role_creation_sessions` 仍停在：
  - `rcs-20260404-112435-d8b51b / workflow_testmate / status=creating`
  - `rcs-20260404-212956-606f71 / workflow_qualitymate / status=creating`

这也解释了为什么当前标准的 `V1-P3 / V1-P4` 测试/质量链还不能恢复成正常续挂，而我本轮没有再去越界补新的 helper 节点。

## 发布边界

当前根仓同步快照仍应按下面这条记录，不再沿用调度 prompt 里过期的 `clean_synced`：

- `developer_id=pm-main`
- `root_sync_state=diverged_or_unknown`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `push_block_reason=code_root_local_repo_behind_origin_main_and_workspace_path_scope_blocks_root_repo_sync`
- `next_push_batch=待允许工作区外收口时先把 ../workflow_code 快进到 b2572be`
- `workspace_head=b2572be`
- `code_root_head=340413e`

也就是说，`pm-main` 自己当前是 clean，但本机 `../workflow_code` 本地 `main` 仍落后 `origin/main` 1 个提交。由于这轮任务边界只允许我写 `workspace_path`，我没有在工作区外直接快进这条根仓。

## 证据

- `git -C .repository/pm-main status --short --branch`
- `git -C .repository/pm-main rev-parse --short HEAD`
- `git -C .repository/pm-main rev-list --left-right --count origin/main...main`
- `git -C ../workflow_code status --short --branch`
- `git -C ../workflow_code rev-parse --short HEAD`
- `Invoke-RestMethod 'http://127.0.0.1:8090/healthz'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/dashboard'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260327-223335-b79f27&exclude_assignment_node_id=node-sti-20260410-5200bbc9'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260410-5200bbc9'`
- `Get-Content C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260410-223136-0eae90/run.json`
- `Get-Content C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260410-223136-0eae90/events.log -Tail 160`
- `Get-Content C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl -Tail 80`
- `Get-Content .running/control/runtime/prod/logs/events/schedules.jsonl -Tail 120`
- `python - <<sqlite>> select agent_id, workspace_path, runtime_status from agent_registry`
- `python - <<sqlite>> select session_id, created_agent_id, status from role_creation_sessions`

## 下一步

- 主线 next: 当前 `node-sti-20260410-5200bbc9 / arun-20260410-223136-0eae90` 继续运行；若它正常收尾，下一条主线 future 已在 `2026-04-10T22:46:00+08:00` 续挂完成。
- 保底 next: `pm持续唤醒 - workflow 主线巡检 -> 2026-04-10T23:16:00+08:00`。
- 测试链 next: 优先按受支持路径收掉 `workflow_testmate / workflow_qualitymate` 的 stale `creating` session，让 runtime 状态恢复到 `idle`，再恢复 `V1-P3 / V1-P4` 的标准续挂。
- baseline next: 在 helper 锁清掉后，优先补一次新的 smoke baseline，确认 `self_iter_guard_degraded=smoke baseline expired` 不再继续出现。
- release boundary next: 若后续允许处理工作区外根仓，先把 `../workflow_code` 本地 `main` 快进到 `b2572be`，再重新校准 launch_summary 里的根仓快照。

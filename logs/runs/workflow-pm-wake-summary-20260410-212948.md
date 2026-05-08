# workflow-pm-wake-summary

## 本轮结论
- 巡检时间：`2026-04-10T21:29:48+08:00`
- Active 版本：`V1 工程质量基线与运行稳态`
- 当前任务包：`V1-P0 连续运行链止血与真相收口`
- 当前泳道：`测试探测`
- 生命周期阶段：`基于基线测试`
- 当前 baseline：`prod=20260410-212042`
- 根仓同步：`developer_id=pm-main / root_sync_state=diverged_or_unknown / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=code_root_local_repo_behind_origin_main_and_workspace_path_scope_blocks_root_repo_sync / next_push_batch=先在 ../workflow_code 快进到 b2572be 后，再重新校准 workspace_head 与 code_root_head / workspace_head=b2572be / code_root_head=340413e`
- preference_ref：`state/user-preferences.md`

- prod 当前不是假健康。唯一真实 running 为 `workflow=node-sti-20260410-81cd3d99 / arun-20260410-212158-6d58fd`；`run.json` 显示 `status=running / provider_pid=38292 / latest_event_at=2026-04-10T21:25:44+08:00`，`events.log` 已出现 `dispatch -> provider_start -> thread.started -> turn.started`，说明保底巡检本轮仍在真实执行。
- 当前主链未断。future 入口仍保留为主线 `sch-20260405-56eee156 -> 2026-04-10T21:52:00+08:00` 与保底 `sch-20260405-67a89536 -> 2026-04-10T22:22:00+08:00`；因此虽然当前图里没有 `ready` 节点，但 `[持续迭代] workflow` 仍保有未来可执行入口，本轮无需手工补链。
- 上一条主线 `node-sti-20260410-c231ed19 / arun-20260410-204711-c125b5` 已在 `2026-04-10T21:21:31+08:00` 收口为 `cancelled`，`run.json` 的最后高信号信息是“检测到正式环境已完成升级切换，已自动结束当前批次”；本轮保底巡检正是承接这次升级切换后的续挂窗口。
- 当前不执行 `/api/runtime-upgrade/apply`。默认门禁为 `current=candidate=20260410-212042 / running_task_count=1 / blocking_reason=running_tasks_present / can_upgrade=false`；排除当前巡检节点后回落为 `running_task_count=0 / excluded_running_task_count=1 / blocking_reason=no_candidate / can_upgrade=false`，说明当前没有更高 candidate 可升。
- 这轮没有命中 `pm-main` 的 dirty/ahead 历史包袱，但我补钉出一条新的 release boundary 风险：`.repository/pm-main` 已经在 `origin/main=b2572be`，而本机 `../workflow_code` 本地 `main` 仍停在 `340413e` 且 `git status --short --branch` 显示 `## main...origin/main [behind 1]`。当前任务边界只允许在 `workspace_path` 内写入，所以我没有直接在 `../workflow_code` 里做 fast-forward，只把它显式记成阻塞说明。
- 需要额外提醒的是，`[持续迭代] workflow` 的 schedule detail 仍显示陈旧的 `last_trigger_at=2026-04-07T01:42:00+08:00 / last_result_summary=smoke baseline expired`，与实际 `2026-04-10` 主线被升级切换中断的现场不一致。这条 schedule 真相源漂移还需要后续继续收口，但当前 future 触发时间本身是可信的。

## 关键证据
- API：
  - `GET /healthz` -> `ok=true` @ `2026-04-10T21:24:18+08:00`
  - `GET /api/status` -> `1 running + 0 queued + active_agent_count=1`，running node=`node-sti-20260410-81cd3d99`
  - `GET /api/runtime-upgrade/status` -> `current=candidate=20260410-212042 / can_upgrade=false / blocking_reason=running_tasks_present`
  - `GET /api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260327-223335-b79f27&exclude_assignment_node_id=node-sti-20260410-81cd3d99` -> `running_task_count=0 / excluded_running_task_count=1 / can_upgrade=false / blocking_reason=no_candidate`
  - `GET /api/schedules` -> mainline `next_trigger_at=2026-04-10T21:52:00+08:00`；patrol `next_trigger_at=2026-04-10T22:22:00+08:00`
  - `GET /api/assignments/asg-20260327-223335-b79f27/graph` -> graph `status_counts=running 1 / ready 0 / pending 6 / succeeded 22 / failed 32 / blocked 3`
  - `GET /api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260410-81cd3d99` -> audit `dispatch -> run_id=arun-20260410-212158-6d58fd`
- 文件真相：
  - `.running/control/envs/prod.json`
  - `.running/control/instances/prod.json`
  - `.running/control/prod-last-action.json`
  - `.running/control/reports/test-gate-20260410-212042.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/nodes/node-sti-20260410-81cd3d99.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260410-212158-6d58fd/run.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260410-212158-6d58fd/events.log`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260410-204711-c125b5/run.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260410-204711-c125b5/stderr.txt`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl`
- Git 真相：
  - `git -C .repository/pm-main status --porcelain=v1 --branch` -> `## main...origin/main`
  - `git -C .repository/pm-main rev-parse --short HEAD` -> `b2572be`
  - `git -C .repository/pm-main rev-list --left-right --count origin/main...main` -> `0 0`
  - `git -C ../workflow_code status --porcelain=v1 --branch` -> `## main...origin/main [behind 1]`
  - `git -C ../workflow_code rev-parse --short HEAD` -> `340413e`
  - `git -C ../workflow_code rev-list --left-right --count origin/main...main` -> `1 0`

## 下一次建议唤醒
- 主线 next：`2026-04-10T21:52:00+08:00`
- 保底 next：`2026-04-10T22:22:00+08:00`
- 若 `21:52` 主线命中后没有形成新的 live run，或再次出现 `0 running + 无 ready + 只剩 future` 但找不到真实 `run.json/events.log`，应立即按断链/假健康补链，而不是按“还有 future”误报通过。
- 若后续允许处理工作区外真相源，下一步先把 `../workflow_code` 本地 `main` 快进到 `origin/main=b2572be`，再重新校准 `pm-main` 与代码根仓的同步快照。
- memory_ref：`.codex/memory/2026-04/2026-04-10.md`

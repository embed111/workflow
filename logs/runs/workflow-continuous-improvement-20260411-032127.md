# continuous-improvement-report

- checked_at: `2026-04-11T03:21:27+08:00`
- active_version: `V1`
- current_task_package: `V1-P9`（联动 `V1-P1`）
- lane: `工程质量探测`
- lifecycle_stage: `开发实现`
- baseline: `prod=20260411-014504`
- change_control: `继续沿用 DTS-00007 修复边界：仅允许 workflow_bugmate 在 fix 链内完成 busy-guard live occupancy 与 training registry execution 投影修复；正式代码回放、最小回归与发布仍等待 fix 结果回流`
- root_sync_state: `clean_synced`
- ahead_count: `0`
- dirty_tracked_count: `0`
- untracked_count: `0`
- push_block_reason: `-`
- next_push_batch: `待新批次`
- workspace_head: `4fd5c6d`
- code_root_head: `4fd5c6d`
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`
- preference_ref: `state/user-preferences.md`
- delta_observation: `03:16 主线已派发成新的 live run arun-20260411-031622-4ad010；DTS-00007 fix 仍在 workflow_bugmate 工作区运行，但 latest_event 已推进到生成最终结果对象并引用 HTML/patch；保底 future 仍保留在 03:46。`
- delta_validation: `下一轮优先复核 workflow_bugmate 是否正式交回 patch/修复说明、03:16 主线 finalize 后是否自动续挂新的 mainline future，以及 fix 回流后是否需要切 workflow_devmate / workflow_testmate 做正式回放与回归。`

## 本轮结论

这轮我继续把 `V1` 的重心保持在 `工程质量探测 / 开发实现`，不是再开新功能，而是盯住 `DTS-00007` 的修复落地和 7x24 主线接棒是否持续成立。发布边界没有漂：`pm-main` 与 `../workflow_code` 仍同处 `4fd5c6d`，根仓快照继续是 `clean_synced / ahead=0 / dirty=0 / untracked=0`，因此这轮不需要切回 `V1-P2` 的发布边界收口模式。

`03:16` 的 `[持续迭代] workflow` 已经命中并派发成新的 live run `node-sti-20260411-37e1862d / arun-20260411-031622-4ad010`。这意味着现场已从上一轮的“02:55 主线 running + DTS-00007 fix running”继续推进到“03:16 主线 running + DTS-00007 fix running”；主线不是靠旧 run 拖住，而是新一棒已经真实接上。

`DTS-00007` 这边，`workflow_bugmate` 的 fix 节点 `dr-20260411-95b4172903-fix / arun-20260411-025947-509873` 仍在 running，但 `run.json.latest_event` 已推进到“生成最终结果对象并引用 HTML/patch”的收尾阶段。这说明 `V1-P9` 仍处在 live 修复窗口内，而且很接近交付待回放状态；当前最值钱的动作不是再补并行 helper，而是等这条修复结果正式回流。

## 运行态真相

截至 `2026-04-11T03:21:27+08:00`，`/api/status` 与全局主图继续一致收口为 `running_task_count=2 / queued_task_count=0 / failed_task_count=8 / active_agent_count=2`。当前真实 running 为：

- 主线 `workflow=node-sti-20260411-37e1862d / arun-20260411-031622-4ad010`
- 修复 `workflow_bugmate=dr-20260411-95b4172903-fix / arun-20260411-025947-509873`

`/api/schedules` 当前表现为：主线 schedule `sch-20260405-56eee156` 因 `03:16` 这轮正在 running，`next_trigger_at` 暂时为空；保底 schedule 仍保留 `sch-20260405-67a89536 -> 2026-04-11T03:46:00+08:00` 的 future 出口。因此 7x24 现场虽然暂时只剩“当前 running + 保底 future”，但并没有断链；这依然满足“当前执行或下一棒出口至少保留一条”的连续推进口径。

升级方面，这轮仍不执行 `/api/runtime-upgrade/apply`。默认 `/api/runtime-upgrade/status` 返回 `current=candidate=20260411-014504 / candidate_is_newer=false / running_tasks_present / can_upgrade=false`；按任务要求排除当前主线 `node-sti-20260411-37e1862d` 后，门禁只回落为 `running_task_count=1 / excluded_running_task_count=1 / blocking_reason=running_tasks_present / can_upgrade=false`，说明 `workflow_bugmate` 的 fix run 仍在占槽，而且当前不存在更高 candidate。

## 版本与协作判断

这轮 active version 继续是 `V1`，当前最高价值任务包仍是 `V1-P9`，同时联动 `V1-P1` 的 live execution truth 收口。生命周期阶段继续记 `开发实现`，因为 `DTS-00007` 已经在实际修复，不再只是分析、测试或建议态。baseline 不变，仍沿用 `prod=20260411-014504`；本轮也没有新增 baseline。

变更控制边界继续只收在 `DTS-00007`：single-agent busy guard 的 live occupancy 探测，以及 training registry 对 assignment live execution 的投影与 runtime_status 同步。只要这条 fix 结果还没正式回流，我就不额外续挂 `workflow_devmate / workflow_testmate / workflow_qualitymate`，避免在同一问题面上提前放大并行冲突。

## 证据

- `git -C .repository/pm-main status --porcelain=v2 --branch`
- `git -C ../workflow_code status --porcelain=v2 --branch`
- `http://127.0.0.1:8090/healthz`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/schedules`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260327-223335-b79f27&exclude_assignment_node_id=node-sti-20260411-37e1862d`
- `http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph`
- `http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-37e1862d`
- `http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=dr-20260411-95b4172903-fix`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-031622-4ad010/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-025947-509873/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-025947-509873/stdout.txt`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl`

## 下一步

- 当前泳道/阶段 next: `工程质量探测 / 开发实现`
- 主线 next: 当前 `[持续迭代] workflow / 2026-04-11 03:16:00` 已在 `node-sti-20260411-37e1862d / arun-20260411-031622-4ad010` live running；下一次 mainline future 需等本轮 finalize 自动续挂
- 保底 next: `pm持续唤醒 - workflow 主线巡检 -> 2026-04-11T03:46:00+08:00`
- defect next: `DTS-00007 / dr-20260411-95b4172903-fix / arun-20260411-025947-509873` 仍在 running，latest_event 已推进到最终结果对象与 HTML/patch 引用生成阶段
- release boundary next: 继续保持 `clean_synced / 4fd5c6d`，在 fix 结果回流前不新开 push 批次
- recommended_followup_at: `2026-04-11T03:30:00+08:00`
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`

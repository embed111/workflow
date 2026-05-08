# continuous-improvement-report

- checked_at: `2026-04-11T03:07:49+08:00`
- active_version: `V1`
- current_task_package: `V1-P9`（联动 `V1-P1`）
- lane: `工程质量探测`
- lifecycle_stage: `开发实现`
- baseline: `prod=20260411-014504`
- change_control: `基于 DTS-00007 分析结论，当前只允许在 workflow_bugmate 修复链内推进 busy-guard live occupancy 与 agent_registry execution 投影修复；修复后的正式代码回放与回归仍沿用该 baseline`
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
- delta_observation: `DTS-00007 analyze 已在 02:58 收尾，workflow_bugmate fix 节点已于 02:59 接棒 live running；workflow 主线 02:55 节点也在 03:02 真正接棒运行，future 仍保留在 03:16 / 03:46。`
- delta_validation: `下一轮优先复核 workflow_bugmate fix 是否交回 patch/修复说明、主线 03:16 future 是否继续保持接力，以及修复后是否需要续挂 workflow_devmate / workflow_testmate 做正式回放与回归。`

## 本轮结论

这轮我把 `V1` 的当前重心从“测试探测拿结论”切到“工程质量探测推动修复实现”。发布边界没有漂：`pm-main` 与 `../workflow_code` 仍同处 `4fd5c6d`，`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=- / next_push_batch=待新批次`。当前最值钱的动作不是再补新的 helper，而是把 `DTS-00007` 从分析推进到真正的修复执行。

`DTS-00007` 的分析节点 `dr-20260411-95b4172903-analyze / arun-20260411-022953-b133fa` 已在 `2026-04-11T02:58:52+08:00` 成功收尾，结论明确指出根因不是 UI 误展示，而是 assignment busy-guard 的 live occupancy 探测与 training registry 的 execution 投影长期分叉。随后 fix 节点 `dr-20260411-95b4172903-fix / arun-20260411-025947-509873` 已在 `workflow_bugmate` 工作区 live running；当前 `run.json.latest_event` 直接列出 5 条待办：修 busy-guard 探测、修 registry 口径投影、补定向回归、跑回归、写交付。这说明 `V1-P9` 现在已经进入实际修复，不再停在建议态。

与此同时，当前主线 `node-sti-20260411-7acee490 / arun-20260411-030223-37363a` 已在 `2026-04-11T03:02:22+08:00` 从 `02:55` 命中节点正式接棒成 live run。也就是说，现场已经从上一轮的“巡检收尾后主线 ready 等接棒 + bugmate analyze running”，收口成“主线 running + bugmate fix running”的双线推进。

## 运行态真相

截至 `2026-04-11T03:07:49+08:00`，`/api/status` 与 workboard 一致显示 `running_task_count=2 / queued_task_count=0 / failed_task_count=8 / active_agent_count=2`。当前真实 running 为：

- 主线 `workflow=node-sti-20260411-7acee490 / arun-20260411-030223-37363a`
- 修复 `workflow_bugmate=dr-20260411-95b4172903-fix / arun-20260411-025947-509873`

`/api/schedules` 继续保留两条 future 出口：

- 主线 `sch-20260405-56eee156 -> 2026-04-11T03:16:00+08:00`
- 保底 `sch-20260405-67a89536 -> 2026-04-11T03:46:00+08:00`

因此 done definition 里的“至少保留一条未来可执行入口”继续满足，而且当前不是 `0 running + ready/future` 的空转现场，而是已有 live mainline 在跑、下一轮 future 也已经续挂。

升级方面，这轮仍不执行 `/api/runtime-upgrade/apply`。默认 `/api/runtime-upgrade/status` 返回 `current=candidate=20260411-014504 / candidate_is_newer=false / running_tasks_present / can_upgrade=false`；按任务要求排除当前主线 `node-sti-20260411-7acee490` 后，门禁依旧是 `running_task_count=1 / excluded_running_task_count=1 / blocking_reason=running_tasks_present / can_upgrade=false`，说明即使不算主线，仍有 `workflow_bugmate` 修复 run 占槽，而且并不存在更高 candidate。

## 版本与协作判断

这轮我把 lane 记为 `工程质量探测`，把生命周期阶段推进到 `开发实现`。原因不是这轮在 `pm-main` 里直接写了代码，而是 `DTS-00007` 已经完成分析并进入 live fix run；当前最高价值动作已经从“继续验证是不是 bug”切成“按既定变更控制把修复做出来”。baseline 继续沿用 `prod=20260411-014504`，这轮没有新增 baseline，也不需要再开新的变更控制主题。

我没有额外续挂 `workflow_devmate / workflow_testmate / workflow_qualitymate`。当前 `workflow_bugmate` 的 fix 链已经是最直接的执行位；`workflow_testmate / workflow_qualitymate` 上一轮交回的 smoke baseline 与双 running 审计结论已经被完整消费进 `DTS-00007`。在 fix 结果没回流之前，再开并行 helper 只会增加冲突面，不会提高当前轮的推进质量。

版本计划已经同步到这一组新状态：`V1-P9` 仍保持 `in_progress`，但描述从“已进入正式缺陷闭环”进一步推进到“analyze 已完成、fix 节点 live running”。这轮的交付重点因此不是新功能，而是把 active 版本的稳定性任务包继续压进可验证的修复链。

## 证据

- `git -C .repository/pm-main status --porcelain=v2 --branch`
- `git -C .repository/pm-main rev-list --left-right --count origin/main...main`
- `git -C ../workflow_code status --porcelain=v2 --branch`
- `git -C ../workflow_code rev-list --left-right --count origin/main...main`
- `http://127.0.0.1:8090/healthz`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/schedules`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260327-223335-b79f27&exclude_assignment_node_id=node-sti-20260411-7acee490`
- `http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-7acee490`
- `http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=dr-20260411-95b4172903-fix`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-030223-37363a/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-030223-37363a/events.log`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-025947-509873/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-022953-b133fa/result.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`

## 下一步

- 当前泳道/阶段 next: `工程质量探测 / 开发实现`
- 主线 next: 当前 `[持续迭代] workflow / 2026-04-11 02:55:00` 已在 live running；future 继续保留 `2026-04-11T03:16:00+08:00`
- 保底 next: `pm持续唤醒 - workflow 主线巡检 -> 2026-04-11T03:46:00+08:00`
- defect next: `DTS-00007 / dr-20260411-95b4172903-fix / arun-20260411-025947-509873` 正在 `workflow_bugmate` 工作区运行，待交回 patch / 修复说明后决定是否切 `workflow_devmate` 回放正式代码
- release boundary next: 继续保持 `clean_synced / 4fd5c6d`，在 fix 结果回流前不新开 push 批次
- recommended_followup_at: `2026-04-11T03:16:00+08:00`
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`

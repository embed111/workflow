# workflow-pm-wake-summary

- checked_at: `2026-04-11T13:19:10+08:00`
- active_version: `V1`
- task_package: `V1-P2`
- lane: `工程质量探测`
- lifecycle_stage: `变更控制`
- baseline: `prod=20260411-093051`
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`
- experience_ref: `.codex/experience/dual-repo-boundary-and-dev-workspace-bootstrap.md`

## 巡检结论

这轮 `prod` 不是假健康。当前真实现场已经收口为：

- `running`: `node-sti-20260411-381ab062 / arun-20260411-131051-6cc981`
- `ready`: `node-sti-20260411-9bce1dd5`
- `future`: 主线 `2026-04-11T13:26:00+08:00`，保底 `2026-04-11T13:56:00+08:00`

我直接核了当前巡检 run 的磁盘真相：`run.json` 仍是 `status=running / provider_pid=59468 / latest_event_at=2026-04-11T13:14:26+08:00`，`events.log` 已出现 `dispatch -> provider_start -> thread.started -> turn.started`。所以这轮不是“0 running + ready 堆积”的假健康，而是保底巡检还在真实执行，主线 `13:11` 节点因此停在 `ready` 等接棒。

当前 active 版本继续是 `V1`，当前最该推进的任务包仍是 `V1-P2`，泳道与生命周期阶段继续记为 `工程质量探测 / 变更控制`。这轮最高价值动作不是再扩 helper 面，而是先把实际命中的 release boundary 小 dirty 收口成新 candidate。

## 发布边界

这轮命中的旧快照已经过期：

- 调度器任务 prompt 仍带着 `root_sync_state=ahead_dirty / ahead_count=3 / dirty_tracked_count=2 / workspace_head=263d1c8`
- live `prod` 的 schedule 详情仍带着 `root_sync_state=ahead_dirty / ahead_count=4 / dirty_tracked_count=2 / workspace_head=85320f4`

我按 live `git status` 重新盘了一次，确认这轮真正的 release boundary 是：

- 收口前：`root_sync_state=ahead_dirty / ahead_count=0 / dirty_tracked_count=3 / untracked_count=0 / push_block_reason=workspace_dirty_changes_present / next_push_batch=主线计划现场索引与本机根仓治理口径收口 / workspace_head=code_root_head=85320f4`
- 收口后：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=- / next_push_batch=待切批 / workspace_head=code_root_head=c55e357`
- 上游参考：`pm-main` 与 `../workflow_code` 当前相对 `origin/main` 都是 `ahead 5`，但只作为上游参考，不构成本轮阻塞

这轮实际执行了受支持的发布边界收口动作：

1. 对 3 个 dirty 文件跑最小验证：
   - `py_compile`
   - `verify_assignment_self_iteration_plan_reference.py`
   - `check_workspace_line_budget.py --root .`
2. 在 `pm-main` 提交 `c55e357 fix(schedule): 收口主线计划现场索引与本机根仓治理口径`
3. 用 `git -C ../workflow_code pull --ff-only D:/code/AI/J-Agents/workflow/.repository/pm-main main` 把本机根仓快进到同一提交
4. 停掉 `test` 旧实例 `PID=71504` 并重发 `test`
5. 把 `prod candidate` 刷到 `20260411-131835`

## 升级门禁

当前没有执行 `/api/runtime-upgrade/apply`。默认 `/api/runtime-upgrade/status` 为：

- `current_version=20260411-093051`
- `candidate_version=20260411-131835`
- `running_task_count=1`
- `blocking_reason=running_tasks_present`
- `can_upgrade=false`

按当前巡检节点排除 `node-sti-20260411-381ab062` 后，门禁回落为：

- `running_task_count=0`
- `candidate_is_newer=true`
- `can_upgrade=true`

所以这轮不存在“已经空窗却漏升”的判断问题；当前仍应继续由 `prod` supervisor 托管的 idle watcher 在真正空窗时发起升级，而不是由这条巡检节点自己 `apply`。

## Helper 判断

这轮我没有新挂 helper 任务，原因不是“忘了处理”，而是当前并不存在 helper 执行者缺位现场：

- `agent_registry.runtime_status` 中 `workflow_bugmate / workflow_devmate / workflow_testmate / workflow_qualitymate` 当前都已经是 `idle`
- `role_creation_sessions` 里虽然还残留 `workflow_testmate / workflow_qualitymate=creating` 的旧行，但它们没有再把 live runtime 锁死

也就是说，这轮 helper 现场更接近“历史 residue 仍在表里”，不是“当前泳道没有执行者”。当前关键路径仍是 `workflow(pm)` 把 V1-P2 的 dirty 边界先收干净。

## 下一次建议

- 主线下一观察点：`2026-04-11T13:26:00+08:00`
- 保底下一兜底点：`2026-04-11T13:56:00+08:00`
- 升级观察点：等 `prod` 真正空窗后，核对 idle watcher 是否把 `candidate=20260411-131835` 切进 live `prod`
- 异常门槛：如果 `2026-04-11T13:26:00+08:00` 之后 `node-sti-20260411-9bce1dd5` 仍停在 `ready` 且找不到新的 live run，就把它按主线 handoff 异常继续处理

## 证据

- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `docs/workflow/reports/7x24发布边界收口方案-20260409.md`
- `git -C .repository/pm-main status --short --branch`
- `git -C .repository/pm-main diff --stat`
- `git -C .repository/pm-main rev-parse --short HEAD`
- `git -C ../workflow_code status --short --branch`
- `git -C ../workflow_code rev-parse --short HEAD`
- `.repository/pm-main/.test/20260411-131710-069/report.md`
- `.repository/pm-main/.test/20260411-131710-070/report.md`
- `.repository/pm-main/.test/20260411-131710-180/report.md`
- `.running/control/reports/test-gate-20260411-131835.json`
- `.running/control/prod-candidate.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-131051-6cc981/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-131051-6cc981/events.log`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/nodes/node-sti-20260411-381ab062.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/nodes/node-sti-20260411-9bce1dd5.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`

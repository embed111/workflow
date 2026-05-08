# Continuous Improvement Report

- generated_at: `2026-04-11T13:05:36+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260411-642f9d9a`
- graph_name: `任务中心全局主图`
- active_version: `V1`
- task_package: `V1-P2`
- lane: `工程质量探测`
- lifecycle_stage: `变更控制`
- baseline: `prod=20260411-093051`

## Root Sync
- launch_snapshot:
  - `root_sync_state=ahead_clean`
  - `ahead_count=2`
  - `dirty_tracked_count=0`
  - `untracked_count=0`
  - `push_block_reason=unpushed_commits_present`
  - `next_push_batch=待切批`
- current_snapshot:
  - `developer_id=pm-main`
  - `root_sync_state=clean_synced`
  - `ahead_count=0`
  - `dirty_tracked_count=0`
  - `untracked_count=0`
  - `push_block_reason=-`
  - `next_push_batch=待切批`
  - `workspace_head=85320f4`
  - `code_root_head=85320f4`
  - upstream_reference: `workspace/code_root -> ## main...origin/main [ahead 4]`

## Change Control
- baseline 继续沿用 `prod=20260411-093051`。
- 本轮变更控制内容：把 `ASSIGNMENT_PM_WAKE_DELAY_MINUTES` 从 `5` 调回 `60`，恢复“主线分钟级、保底小时级”的产品口径。
- 本轮没有续挂新的 helper 任务；原因是当前最高价值动作是先把 `pm-main` 的 dirty 批次验证、提交、同步和刷新 candidate 收干净。

## Actions
- 提交 `pm-main` 代码批次：`85320f4 fix(schedule): 将保底巡检恢复为小时级兜底节奏`。
- 通过 `git -C ../workflow_code pull --ff-only D:/code/AI/J-Agents/workflow/.repository/pm-main main` 完成本机代码根仓同步。
- 停掉真实监听 `8092` 的旧 `test` 进程 `PID=58428`，重新执行 `deploy_workflow_env.ps1 -Environment test`。
- 把 `test` 与 `prod candidate` 刷到 `20260411-130315`。

## Validation
- `py_compile`：`.repository/pm-main/.test/20260411-125934-955/report.md`
- `verify_assignment_self_iteration_schedule_alignment.py`：`.repository/pm-main/.test/20260411-125909-858/report.md`
- `verify_self_iteration_backup_schedule_on_smoke_block.py`：`.repository/pm-main/.test/20260411-125909-834/report.md`
- `check_workspace_line_budget.py --root .`：`.repository/pm-main/.test/20260411-130551-738/report.md`
- `workflow gate`：`.repository/pm-main/.test/20260411-125941-943/report.md`
- `workflow gate` 详报：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260411-130043.md`
- `test gate` 证据：`.running/control/reports/test-gate-20260411-130315.json`

## Live Runtime
- `healthz`：`2026-04-11T13:03:41+08:00` 返回 `ok=true`
- live `prod`：`current_version=20260411-093051`
- latest `candidate`：`20260411-130315`
- `/api/runtime-upgrade/status`：`running_tasks_present / can_upgrade=false`
- 排除当前主线节点 `node-sti-20260411-642f9d9a` 后：`candidate_is_newer=true / can_upgrade=true`
- 当前 running 节点：`node-sti-20260411-642f9d9a`
- 当前 future 出口：
  - 主线：`2026-04-11T13:11:00+08:00`
  - 保底：`2026-04-11T13:06:00+08:00`
- 注意：live `prod` 的主线/保底 schedule 文案仍显示旧版 `ahead_dirty / 263d1c8` 摘要；这只是现网未升级前的旧文案快照，不是本轮发布边界回退。

## Warnings
- `check_workspace_line_budget.py` 与 `workflow gate` 仍提示 23 个 refactor trigger / 6 个 guideline trigger；这属于长期工程治理告警，不构成本轮候选发布阻塞。
- 正式升级仍未发生；当前主线节点结束前，`prod` 仍会维持在 `20260411-093051`。

## Next
- 继续观察 `prod` supervisor 托管的 idle watcher 是否在空窗把 `candidate=20260411-130315` 切进 live `prod`。
- 待 `prod` 升级后，重新核对新的主线/保底 schedule 是否继承 `clean_synced / 85320f4` 的 release boundary 快照。
- 待 `prod` 升级后，确认保底 future 是否真正回到 `+60` 分钟。
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`

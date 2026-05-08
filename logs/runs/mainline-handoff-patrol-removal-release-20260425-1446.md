# 7x24 主线接力修复与保底巡检移除发布收口 2026-04-25 14:46

- preference_ref: `state/user-preferences.md`
- operator: `workflow(pm)`
- topic: `修复 7x24 主线接力失败，并从代码仓移除保底巡检逻辑`
- conclusion: `代码已收口到 main，test 已部署通过，prod candidate 已刷新；未直接 apply prod，等待生产空窗或用户明确升级指令。`

## 代码收口
- development_workspace: `.repository/pm-main`
- commit: `f8eefb2 fix(schedule): 移除自迭代保底巡检并改为主线直接重排`
- code_root: `../workflow_code`
- sync_result: `.repository/pm-main HEAD = origin/main = workflow_code HEAD = f8eefb2`
- push_note: `git push origin main` 因 `workflow_code` 是 non-bare 当前分支工作树被拒，已用 `workflow_code` 本地 `fetch + ff-only merge` 完成根仓同步，再刷新 `pm-main` 的 `origin/main` 跟踪引用。

## 行为变化
- `[持续迭代] workflow` 仍是唯一持续迭代入口。
- smoke block、dispatch failure、stale recovery、failure recovery 不再创建或续挂 `pm持续唤醒 - workflow 主线巡检`，而是直接把同一条主线 schedule 重排到 future retry。
- 旧 `patrol*` 字段仅作为读面兼容保留空值或 `false`，不再承载业务行为。
- 已删除旧保底巡检验收/采集脚本：
  - `scripts/acceptance/verify_self_iteration_backup_schedule_on_smoke_block.py`
  - `scripts/acceptance/verify_workflow_mainline_handoff_priority.py`
  - `scripts/collect_post_upgrade_dispatch_regression.ps1`

## 验证证据
- `git diff --check`: passed
- line budget: `.repository/pm-main/.test/20260425-142903-936/report.md`
- full workflow gate: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260425-143505.md`
- key probes passed:
  - `verify_schedule_text_repair.py`
  - `verify_schedule_smoke_guard_scope.py`
  - `verify_schedule_smoke_guard_expired_fail_open.py`
  - `verify_self_iteration_mainline_retry_on_smoke_block.py`
  - `verify_assignment_self_iteration_success_delay.py`
  - `verify_assignment_self_iteration_schedule_alignment.py`
  - `verify_assignment_self_iteration_project_handoff_interval.py`
  - `verify_assignment_stale_running_self_iteration.py`
  - `verify_assignment_project_controller_self_iteration_schedule.py`
  - `run_acceptance_assignment_self_iteration_schedule.py`
- code review: `logs/runs/code-review-20260425-1436.md`
- reviewer_conclusion: `workflow_reviewmate approve`

## 发布证据
- first test deploy in this handoff: `.running/control/logs/test/deploy-20260425-144211.json`
- latest test deploy/candidate after concurrent 7x24 mainline refresh: `.running/control/logs/test/deploy-20260425-144452.json`
- latest test gate: `.running/control/reports/test-gate-20260425-144452.json`
- latest prod candidate: `.running/control/prod-candidate.json`
- latest candidate_version: `20260425-144452`
- test gate result: `passed`
- post_deploy_ghost_running: `repaired_count=1`, after repair `ghost_running_detected=false`

## 生产运行态复核
- `http://127.0.0.1:8090/healthz`: `ok=true`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`:
  - `current_version=20260425-113551`
  - `candidate_version=20260425-144452`
  - `candidate_is_newer=true`
  - `running_task_count=1`
  - `can_upgrade=false`
  - `blocking_reason=存在运行中任务，暂不可升级`
  - `ghost_running_detected=false`
- `http://127.0.0.1:8090/api/schedules`:
  - schedule total: `11`
  - `[持续迭代] workflow`: `enabled=true`, `priority=P1`, `last_result_status=running`, `last_result_node_id=node-sti-20260425-f735d9f7`
  - `pm持续唤醒 - workflow 主线巡检`: `not found`
- live mainline run:
  - node: `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/nodes/node-sti-20260425-f735d9f7.json`
  - run: `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260425-142544-662439/run.json`
  - provider process: `node pid=31424`, alive

## 发布边界判断
- 本轮不直接 apply prod。
- 原因：默认发布规则要求未获明确生产升级指令时只刷新 `prod` candidate；当前生产仍有 `running_task_count=1`，不满足空窗升级条件。
- 后续：等待当前主线 run 收尾或 prod idle watcher 空窗升级；如需立即切换，需要用户明确授权生产升级。

## 增量观察
- delta_observation: 并发的 7x24 主线也在执行同一发布边界收口，导致候选从 `20260425-144211` 继续刷新到 `20260425-144452`；最终证据应以最新 candidate 为准。
- delta_validation: 下一轮先确认 `node-sti-20260425-f735d9f7` 收尾后是否由新逻辑续排 `[持续迭代] workflow` 的 future retry，并复核旧巡检 schedule 仍未回流。

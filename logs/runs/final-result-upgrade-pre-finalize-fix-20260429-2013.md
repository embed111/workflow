# final_result pre-finalize upgrade 修复记录

- time: `2026-04-29T20:13:04+08:00`
- scope: `workflow` 7x24 假 running / ghost running 根因修复
- preference_ref: `state/user-preferences.md`

## 结论
- 这是产品 bug：`final_result/result.json` 已写入但 assignment node/run 终态尚未提交时，旧逻辑立即触发 `prod` auto-upgrade single-check。
- 该检查可能把正常 finalizing 窗口误判成安全升级空窗，升级重启会打断剩余 finalize，造成终态靠后续 `recover_terminal_run_truth` 才补回。
- 修复后，`task_artifact_store_run_runtime.py` 不再在 `final_result` 事件后触发升级检查；升级请求只保留在 post-finalize 路径，由 `_assignment_maybe_request_prod_upgrade_after_finalize` 处理。

## 改动
- `.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/task_artifact_store_run_runtime.py`
  - 删除 `_assignment_maybe_request_prod_single_check_after_final_result`。
  - 删除 `_assignment_execution_worker` 中 `final_result` 事件后的 pre-finalize single-check 调用。
- `.repository/pm-main/scripts/acceptance/verify_assignment_final_result_single_check.py`
  - 用例改为反向合同：`final_result` 写入阶段不得出现 pre-finalize `request_prod_auto_upgrade_single_check` 调用。
  - 同时确认 post-finalize upgrade path 仍存在。

## 红灯
- `.repository/pm-main/.test/20260429-195723-221`
- 命令：`python scripts/acceptance/verify_assignment_final_result_single_check.py`
- 结果：FAIL
- 失败点：检测到 `request_prod_auto_upgrade_single_check` at line 107，以及 `_assignment_maybe_request_prod_single_check_after_final_result` at line 755。

## 绿灯与回归
- `.repository/pm-main/.test/20260429-195804-656`
  - `verify_assignment_final_result_single_check.py` PASS。
- `.repository/pm-main/.test/20260429-195825-590`
  - `verify_assignment_self_upgrade_loopback.py` PASS。
- `.repository/pm-main/.test/20260429-195834-988`
  - `verify_assignment_finalize_fail_closed_recovery.py` PASS。
- `.repository/pm-main/.test/20260429-195854-183`
  - `verify_runtime_upgrade_ghost_running_repair_split.py` PASS。
- `.repository/pm-main/.test/20260429-195910-763`
  - `verify_runtime_upgrade_projected_terminal_mainline_repair.py` PASS。
- `.repository/pm-main/.test/20260429-195928-753`
  - `check_workspace_line_budget.py --root .` PASS。
- `.repository/pm-main/.test/20260429-200004-481`
  - `py_compile` PASS。
- `.repository/pm-main/.test/20260429-200016-274`
  - `run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8116` PASS。
  - gate 报告：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260429-201227.md`

## 后续
- 已提交 `.repository/pm-main`：`959c339 fix(runtime): 禁止 final_result 阶段提前触发生产升级检查`。
- 已同步本机 `../workflow_code/main` 到 `959c339`。
- `git push origin main` 曾被本地非 bare `workflow_code` 工作树保护拒绝；复核根仓无真实 diff 后，采用 `git fetch <pm-main> main` + `git merge --ff-only FETCH_HEAD` 完成 non-destructive 收口。
- 已部署 `test` 并刷新 `prod candidate=20260429-201641`。
- 部署报告：`.running/control/logs/test/deploy-20260429-201641.json`。
- 后续发现 `workflow_testmate` 又以旧工作区刷新出更高候选 `20260429-202322`，该候选仍包含 pre-finalize single-check；我立即用 `pm-main@959c339` 重新部署 `test`，刷新 `prod candidate=20260429-203531`。
- 最新候选随后由同一 `test` 环境形成 `20260429-203638`，已验证候选 app 内不再存在 `_assignment_maybe_request_prod_single_check_after_final_result / final_result_written ticket=`。
- live 复核：
  - `test /healthz`: ok。
  - `prod /healthz`: ok。
  - `prod /api/status`: `active_version=V13`，`running_task_count=1`，`queued_task_count=0`，`truth_mismatch_count=0`。
  - `prod /api/runtime-upgrade/status`: `current_version=20260429-133742`，`candidate_version=20260429-201641`，`candidate_is_newer=true`，`can_upgrade=false`，`ghost_running_detected=false`，`request_pending=false`。
- 本轮未直接 apply `prod`；当前仍有真实 running task，正式升级需等待空窗或用户明确授权。

## 运行出口复核
- `/api/projects`: 当前 active 项目为 `workflow` 与 `project-ai-novel-profit`；未恢复 `project-comics-smoke`。
- `/api/schedules` 复核时，`[持续迭代] workflow` 为 `last_result_status=running`。
- `/api/schedules` 复核时，`[持续迭代] novel_project_pm` 停在 `last_result_status=failed / next_trigger_at=""`，不满足“两项目都有下一棒出口”。
- 已用受支持 API 更新原 schedule `sch-20260426-b092e567`，保留原项目 prompt，只把下一棒续到 `2026-04-29T20:32:00+08:00`。
- 恢复动作 audit：`saud-20260429-758ff473`，operator=`workflow-pm-restore-ai-novel-handoff`。
- 20:40 复核：`node-sti-20260429-d4bf64de` 已进入 `running/live_execution`，run=`arun-20260429-203421-2f79f5`。
- 20:40 复核：`prod /api/status running_task_count=2 / queued_task_count=0 / truth_mismatch_count=0`，`runtime-upgrade ghost_running_detected=false`。

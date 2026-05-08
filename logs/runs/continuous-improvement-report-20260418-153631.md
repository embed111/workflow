# continuous-improvement-report

- round_at: `2026-04-18T15:36:31+08:00`
- active_version: `V4`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- baseline: `prod=20260418-145016`
- result_type: `工程质量探测 + 发布推进`

## result_summary

我把 `prod` idle watcher 的默认 `apply_wait_seconds` 从 `420s` 统一抬到 `600s`，直接处理了 `20260418-145016` 这轮正式升级里“升级已成功但 watcher 先写 timeout 假负面”的 live 风险。对应改动已经在 `.repository/pm-main@6362db5 / ../workflow_code@6362db5` 收口，并刷新出 `test / prod candidate=20260418-153421`。

## changes

- 修改 `.repository/pm-main/scripts/apply_prod_candidate_when_idle.py`，把 Python watcher 默认等待窗口抬到 `600s`。
- 修改 `.repository/pm-main/scripts/workflow_env_common.ps1` 与 `.repository/pm-main/scripts/start_workflow_env.ps1`，让 PowerShell helper 和 supervisor 默认跟随同一等待窗口，不再和 Python watcher 漂移。
- 修改 `.repository/pm-main/scripts/acceptance/verify_apply_prod_candidate_when_idle.py` 与 `.repository/pm-main/scripts/acceptance/verify_prod_auto_upgrade_single_check_helper.py`，把脚本入口与 PowerShell 入口的默认门槛一起锁到 `>=540s`。
- 停掉旧 `test`、重新部署并刷新出 `test / prod candidate=20260418-153421`；部署报告已记录 `post_deploy_ghost_running.repaired_count=1 / ghost_running_count_before=1 / ghost_running_count_after=0`。
- 用受支持的 developer workspace bootstrap/refresh，把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 全部拉回 `clean_synced@6362db5`。

## validation

- `python scripts/quality/check_workspace_line_budget.py --root .`
- `python scripts/acceptance/verify_powershell_script_parse.py`
- `python scripts/acceptance/verify_apply_prod_candidate_when_idle.py`
- `python scripts/acceptance/verify_prod_auto_upgrade_single_check_helper.py`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/stop_test_workflow_env.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy_test_workflow_env.ps1`
- `GET http://127.0.0.1:8090/api/status`
- `GET http://127.0.0.1:8090/api/runtime-upgrade/status`
- `GET http://127.0.0.1:8090/api/config/developer-workspaces`
- `GET http://127.0.0.1:8092/api/runtime-upgrade/status`

## active_version_status

- `V4-R1`: `in_progress / 90% / eta=2026-04-19 / 未超时`
- `V4-R2`: `in_progress / 60% / eta=2026-04-20 / 未超时`
- `V4-R3`: `in_progress / 99% / eta=2026-04-20 / 未超时`
- `V4-R4`: `completed / 100% / eta=2026-04-17 / 未超时`
- AAR: `本轮无新增`
- version_transition_decision: `stay(V4)`
- next_activation_candidate: `-`
- next_activation_ready: `false`

## release_boundary

- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `workspace_head=code_root_head=6362db5`
- `next_push_batch=等待 prod 空窗切到 20260418-153421 后确认 idle watcher 不再因 apply-wait 不足超时误报`

## live_status

- `prod`: `current_version=20260418-145016 / candidate_version=20260418-153421 / candidate_is_newer=true / drain_active=true / running_task_count=1 / can_upgrade=false / blocking_reason=存在运行中任务，暂不可升级`
- `test`: `current_version=20260418-153421 / candidate_version=20260418-153421 / candidate_is_newer=false / running_task_count=0 / ghost_running_detected=false`
- `developer_workspaces`: `count=6 / clean_synced=6 / all ready @6362db5`
- `workflow graph`: `running_task_count=1 / queued_task_count=2 / schedule_total=2 / focus_current_mainline=node-sti-20260418-106de7c3 / focus_patrol=node-sti-20260418-0bfdd325 / starvation_state=mitigated`

## next

- 等 idle watcher 在空窗把 `candidate=20260418-153421` 切进 `prod`。
- 切版后第一优先复核 `logs/runs/prod-idle-upgrade-watchdog-live.md`，确认 watcher 不再留下“超过等待窗口仍未确认切换”的假负面。
- 如果 `153421` live 后 watcher 仍然超时，下一轮优先继续收口这条 runtime-upgrade 监控链，不把它重新滚成“已知先观察”。

- memory_ref: `.codex/memory/2026-04/2026-04-18.md`

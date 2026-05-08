# Continuous Improvement Report

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260414-9d6c98fe`
- generated_at: `2026-04-14T06:16:40+08:00`
- active_version: `V2`
- lane: `功能开发`
- lifecycle_stage: `开发实现`
- baseline: `prod=20260414-041846`
- release_boundary: `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=884b05a`

## 本轮推进
- `V2-R5`：我在 `.repository/pm-main/src/workflow_app/server/services/role_creation_service_parts/session_queries_and_internal_tasks.py` 补上了“draft 角色创建会话基于 live agent_registry + 全局主图 starter 链自动回填 creating 真相”的修复，不再让 training center 长期停在 `draft/workspace_init` 假真相里。
- `V2-R5 / V2-R7`：我新增了 `.repository/pm-main/scripts/acceptance/verify_role_creation_session_live_recovery.py`，并把它以 `TC-RC-005` 接进 `workflow gate`，把这次会话真相修复锁进正式回归。
- `V2-R3`：我在 `pm-main` 提交 `884b05a fix(training): 回填已启动角色创建会话真相`，同步 `pm-main / workflow_code` 到同一批次后，重刷 `test` 并把 `prod candidate` 提升到 `20260414-061519`。
- `V2-R5`：我又复核到 `rc-5ec949-review` 与 `node-20260414-0508-ucdbrief2` 已成功，`node-20260414-0510-devimpl2` 已 running；所以 `R5` 的主风险已经从“链还没接上”切成“候选版本待切入 live + devimpl2 收尾”。

## 验证
- `python scripts/quality/check_workspace_line_budget.py --root .`
- `powershell.exe -File C:/Users/jmqj/.codex/skills/test-session-manager/scripts/run-test-in-session.ps1 -RootPath . -TestCommand "python scripts/acceptance/verify_role_creation_session_live_recovery.py"`
- `powershell.exe -File C:/Users/jmqj/.codex/skills/test-session-manager/scripts/run-test-in-session.ps1 -RootPath . -TestCommand "python -m py_compile src/workflow_app/server/services/role_creation_service_parts/session_queries_and_internal_tasks.py scripts/acceptance/verify_role_creation_session_live_recovery.py scripts/acceptance/workflow_gate_probe_registry.py"`
- `powershell.exe -File C:/Users/jmqj/.codex/skills/test-session-manager/scripts/run-test-in-session.ps1 -RootPath . -TestCommand "python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098"`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .repository/pm-main/scripts/stop_workflow_env.ps1 -Environment test`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .repository/pm-main/scripts/deploy_workflow_env.ps1 -Environment test`
- `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8090/healthz`
- `Invoke-RestMethod http://127.0.0.1:8090/api/status`
- `Invoke-RestMethod http://127.0.0.1:8090/api/runtime-upgrade/status`
- `Invoke-RestMethod http://127.0.0.1:8090/api/schedules`
- `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8092/healthz`
- `Invoke-RestMethod http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=rc-5ec949-review&include_test_data=0`
- `Invoke-RestMethod http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-20260414-0508-ucdbrief2&include_test_data=0`
- `Invoke-RestMethod http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-20260414-0510-devimpl2&include_test_data=0`
- `git -C .repository/pm-main rev-parse --short HEAD`
- `git -C ../workflow_code rev-parse --short HEAD`

## 当前需求评估
- `V2-R1`: `status=in_progress / progress=98% / eta=2026-04-15 / timeout=未超时`
  `today daily` 继续保持 `completed`；当前剩余工作仍是补 1 轮 current-version smoke，并确认 completed 语义在 live baseline 上继续稳定。
- `V2-R2`: `status=in_progress / progress=75% / eta=2026-04-18 / timeout=未超时`
  负责人筛选和细粒度详情卡已稳定，这轮没有新的阻塞信号。
- `V2-R3`: `status=in_progress / progress=97% / eta=2026-04-19 / timeout=未超时`
  `20260414-061519` 已通过 gate 并刷新为新的 `prod candidate`；剩余缺口收窄为发布边界助手自己的专项编号化回归。
- `V2-R4`: `status=planned / progress=25% / eta=2026-04-19 / timeout=未超时`
  当前仍缺独立治理动作自动化回归切片。
- `V2-R5`: `status=in_progress / progress=84% / eta=2026-04-15 / timeout=未超时`
  starter chain、review、专属 brief 和会话真相修复都已就位；当前剩余工作收窄为等待 `20260414-061519` 切进 live `prod` 后验证 `rcs-20260414-004251-d716cd` 不再停在 `draft/workspace_init`，并继续收 `node-20260414-0510-devimpl2`。
- `V2-R6`: `status=in_progress / progress=80% / eta=2026-04-15 / timeout=未超时`
  需求映射矩阵仍维持 `28` 份有效文档，无新增超时。
- `V2-R7`: `status=in_progress / progress=78% / eta=2026-04-16 / timeout=未超时`
  本轮新增 `TC-RC-005` 并落进 gate；当前缺口仍是把 `TC-REL-* / TC-AWAKE-* / TC-RC-*` 继续补成更完整的专项编号体系。
- `V2-R8`: `status=completed / progress=100% / eta=已于 2026-04-13 完成 / timeout=-`

## Live 真相
- `prod` 当前为 `20260414-041846`，`candidate=20260414-061519`，`candidate_is_newer=true`，`drain_active=true`，`running_task_count=2`，`queued_task_count=2`。
- 当前 `7x24` 出口保持为：主线 `running`，下一条主线 `queued`，保底 `queued`；`workflow_mainline_starvation_state=mitigated`。
- `workflow_ucdmate` 当前链路已经推进到：`rc-5ec949-review / succeeded -> node-20260414-0508-ucdbrief2 / succeeded -> node-20260414-0510-devimpl2 / running`。
- 当前并行提效判断为：`parallel_candidate_count=4 / parallel_dispatched_count=2 / active_helper_tasks=[workflow_ucdmate:node-20260414-0508-ucdbrief2(succeeded), workflow_devmate:node-20260414-0510-devimpl2(running)] / parallel_block_reason=prod candidate=20260414-061519 正在 drain 等 idle window；live session truth fix still pending apply`

## 风险与下一步
- 当前最高优先的剩余风险已经收窄为三条：`20260414-061519` 仍待 idle watcher 在空窗切进 live `prod`；`workflow-devmate-ui-implementation-batch2` 仍在 running；`V2-R1` 的 current-version smoke 还没补做。
- 本轮无需求点超时，因此未新增 `AAR`。
- 下一步我优先等 idle window 把 `20260414-061519` 切进 `prod`，随后立刻复核 `rcs-20260414-004251-d716cd` 已不再停在 `draft/workspace_init`。
- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-14.md`

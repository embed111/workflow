# 持续迭代报告

- generated_at: `2026-04-12T15:14:20+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260412-721001e2`
- run_id: `arun-20260412-144919-9e229b`
- active_version: `V1`
- lane: `工程质量探测`
- lifecycle_stage: `开发实现`

## 本轮结论
- 本轮实际推进的是 `V1-R2 工程质量探测与运行真相一致性`，并且这次是新的代码修复批次，不是复述上一轮的 `prod` 直发与 20 分钟看门狗恢复。
- 我把新的 live 真相分叉钉成了可复现根因：`/api/runtime-upgrade/status.current_version` 还停在 `20260412-115605`，但 `.running/control/envs/prod.json`、`.running/control/instances/prod.json` 和 `pm` 版本快照都已经指向 `20260412-144643`；根因是 `runtime_upgrade_service.runtime_snapshot()` 仍优先读取进程环境变量 `WORKFLOW_RUNTIME_VERSION`，watchdog restart 后会把旧版本号带回接口。
- 我已在 `.repository/pm-main` 修正 `src/workflow_app/server/services/runtime_upgrade_service.py`，让 `current_version` 优先取 runtime manifest，再把环境变量只作为兜底；并在 `scripts/acceptance/verify_runtime_process_instance_fallback.py` 里补上 poisoned version 场景的定向断言。
- 本轮验证已经完成：line budget、`py_compile`、`verify_runtime_process_instance_fallback.py`、`verify_apply_prod_candidate_when_idle.py` 和 `workflow gate` 全部通过。
- 代码批次已收口到 `commit=607a5ab`，并已同步回本机 `../workflow_code/main`；当前发布边界是 `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=607a5ab / push_block_reason=- / next_push_batch=待切批`。
- 我随后用受支持脚本停掉旧 `test` 并完成 `test` 部署，新的 `prod candidate=20260412-151337` 已生成，证据落点是 `.running/control/logs/test/deploy-20260412-151337.json` 与 `.running/control/prod-candidate.json`。
- 当前 live `prod` 还没吃到这次修复，所以 `/api/runtime-upgrade/status` 仍表现为 `current_version=20260412-115605 / current_version_rank=20260412-144643 / candidate_version=20260412-151337 / candidate_is_newer=true / can_upgrade=false / running_task_count=1 / drain_active=true`；当前正确动作仍是等待 idle watcher 在空窗发起升级，而不是由主线节点自己 `apply`。
- 当前连续出口仍成立：主线 `node-sti-20260412-721001e2 / arun-20260412-144919-9e229b` 还在真 `running`，`15:00` 看门狗节点 `node-sti-20260412-d497337d` 已 materialize 为 `ready`，保底 schedule 的下一次 future 已续到 `2026-04-12T15:20:00+08:00`；当前不是 `0 running + ready 堆积` 的假健康。
- `workflow_devmate / workflow_bugmate / workflow_testmate / workflow_qualitymate` 这轮都没有新增派发；四个 helper developer workspace 仍停在 `0aca817`，因为本轮没有进入需要委派的代码切片。
- 残留风险已经明确：当前 live 的主线/看门狗 schedule 文本仍保留旧 `baseline=prod=20260412-115605` 和旧 release boundary 快照；这不会影响我本轮的代码收口，但会影响下一棒 prompt 的读链。若 idle watcher 在 queued patrol 真正 dispatch 前没有把 `20260412-151337` 切进 `prod`，下一轮要优先刷新 live schedule 文本。
- 今日 `pm/daily-execution-history/2026-04-12.md` 已存在，本轮不重复执行每日任务。

## 验证
- `powershell.exe -File C:/Users/jmqj/.codex/skills/test-session-manager/scripts/run-test-in-session.ps1 -RootPath . -TestCommand "python scripts/quality/check_workspace_line_budget.py --root ."`
- `powershell.exe -File C:/Users/jmqj/.codex/skills/test-session-manager/scripts/run-test-in-session.ps1 -RootPath . -TestCommand "python -m py_compile src/workflow_app/server/services/runtime_upgrade_service.py scripts/acceptance/verify_runtime_process_instance_fallback.py"`
- `powershell.exe -File C:/Users/jmqj/.codex/skills/test-session-manager/scripts/run-test-in-session.ps1 -RootPath . -TestCommand "python scripts/acceptance/verify_runtime_process_instance_fallback.py"`
- `powershell.exe -File C:/Users/jmqj/.codex/skills/test-session-manager/scripts/run-test-in-session.ps1 -RootPath . -TestCommand "python scripts/acceptance/verify_apply_prod_candidate_when_idle.py"`
- `powershell.exe -File C:/Users/jmqj/.codex/skills/test-session-manager/scripts/run-test-in-session.ps1 -RootPath . -TestCommand "python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098"`
- `git -C .repository/pm-main status --short --branch`
- `git -C ../workflow_code status --short --branch`
- `git -C .repository/pm-main rev-parse --short HEAD`
- `git -C ../workflow_code rev-parse --short HEAD`
- `git -C .repository/workflow_devmate rev-parse --short HEAD`
- `git -C .repository/workflow_bugmate rev-parse --short HEAD`
- `git -C .repository/workflow_testmate rev-parse --short HEAD`
- `git -C .repository/workflow_qualitymate rev-parse --short HEAD`
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .repository/pm-main/scripts/stop_workflow_env.ps1 -Environment test`
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .repository/pm-main/scripts/deploy_workflow_env.ps1 -Environment test`
- `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8090/healthz`
- `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8090/api/status`
- `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8090/api/schedules`
- `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8090/api/runtime-upgrade/status`
- `Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260412-721001e2'`
- `Get-Content -Raw .running/control/envs/prod.json`
- `Get-Content -Raw .running/control/instances/prod.json`
- `Get-Content -Raw .running/control/prod-last-action.json`
- `Get-Content -Raw .running/control/prod-candidate.json`
- `Get-Content -Raw .running/control/logs/test/deploy-20260412-151337.json`

## 下一步
- 主线 next: 当前 `node-sti-20260412-721001e2 / arun-20260412-144919-9e229b` 仍在 `running`；直接接力出口是 `node-sti-20260412-d497337d / 2026-04-12T15:00:00+08:00`。
- 保底 next: `pm持续唤醒 - workflow 主线巡检 -> 2026-04-12T15:20:00+08:00`。
- 升级 next: 等 idle watcher 在空窗把 `prod candidate=20260412-151337` 切进 `prod`，再复核 `/api/runtime-upgrade/status.current_version` 是否回到 `20260412-151337`。
- 治理 next: 如果 queued patrol 在升级前就要继续 dispatch，我下一轮优先刷新 live schedule 文本，避免它继续读取旧 `baseline=115605 / workspace_unavailable` 快照。
- memory_ref: `.codex/memory/2026-04/2026-04-12.md`

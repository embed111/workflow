# 持续迭代报告

- generated_at: `2026-04-11T12:37:28+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260411-0204ed75`
- run_id: `arun-20260411-122033-b3d95c`
- active_version: `V1`
- task_package: `V1-P2`
- lane: `工程质量探测`
- lifecycle_stage: `变更控制`
- baseline: `prod=20260411-093051`
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`
- preference_ref: `state/user-preferences.md`

## 本轮结论

- 我把 `workflow` 主线与保底的滚动间隔从 `15/30/30` 收口回分钟级 `5/10/5`，让规则、治理和版本口径能在几分钟内被下一棒重新读取，而不是继续拖到半小时级窗口。
- 这批改动已经走完最小验证与完整门禁：`verify_assignment_self_iteration_schedule_alignment.py`、`check_workspace_line_budget.py --root .`、`workflow gate` 全部通过。
- 代码发布边界已相对本机 `../workflow_code` 收口：`pm-main` 与 `../workflow_code` 当前都在 `263d1c8`，最新 `release_boundary_service` 口径下是 `clean_synced`；相对 `origin/main` 仍为 `ahead 3`，但只作为上游参考，不再当成本轮阻塞。
- 默认发布链也已继续完成：我先最小化停掉旧的 `test` 进程 `PID=66332`，随后成功刷新 `test` 与 `prod candidate` 到 `20260411-123453`。
- live `prod` 当前仍是真实 `running`，而且新的 `12:36` 主线节点已经进入 `ready`，现场已收口成 `1 running + 1 ready + 1 future保底` 的连续接力；正式升级仍留给 idle watcher 在空窗时发起。

## 根仓同步快照

- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `push_block_reason=-`
- `next_push_batch=待切批`
- `workspace_head=263d1c8`
- `code_root_head=263d1c8`
- `upstream_workspace_status=## main...origin/main [ahead 3]`
- `upstream_code_root_status=## main...origin/main [ahead 3]`

## 验证与发布

- 测试会话：`.repository/pm-main/.test/20260411-122555-362/`
  - 命令：`python scripts/acceptance/verify_assignment_self_iteration_schedule_alignment.py`
  - 结果：通过；冻结时间下主线/保底触发时间与 `5/10/5` 新口径一致
- 测试会话：`.repository/pm-main/.test/20260411-122555-492/`
  - 命令：`python scripts/quality/check_workspace_line_budget.py --root .`
  - 结果：通过；仅保留既有 refactor/guideline 提示，不构成本轮阻塞
- 测试会话：`.repository/pm-main/.test/20260411-122650-711/`
  - 命令：`python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
  - 结果：通过；汇总报告见 `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260411-122800.md`
- 代码收口：
  - `git -C .repository/pm-main commit -m "fix(schedule): 将主线与保底滚动间隔收口到分钟级节奏"`
  - 生成提交：`263d1c8`
  - `git -C ../workflow_code pull --ff-only D:/code/AI/J-Agents/workflow/.repository/pm-main main`
  - 结果：本机代码根仓快进到同一提交
- `test` / candidate：
  - 旧 `test` 进程：`PID=66332`，监听 `127.0.0.1:8092`，版本 `20260411-112732`
  - 处理：`Stop-Process -Id 66332 -Force`
  - 重新部署：`powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy_workflow_env.ps1 -Environment test`
  - 结果：`test` 与 `prod candidate` 刷到 `20260411-123453`

## 运行态证据

- `GET /healthz`
  - `ok=true`
  - 时间：`2026-04-11T12:38:29+08:00`
- `GET /api/status`
  - `running_task_count=1`
  - `queued_task_count=1`
  - `assignment_running_agent_count=1`
  - `failed_task_count=10`
  - `blocked_task_count=9`
- `GET /api/assignments/asg-20260327-223335-b79f27/graph`
  - 当前主图：`total_nodes=78 / pending=6 / ready=1 / running=1 / succeeded=57 / failed=10 / blocked=3`
  - 当前真实 running：`node-sti-20260411-0204ed75`
  - 当前 ready 接棒：`node-sti-20260411-642f9d9a / [持续迭代] workflow / 2026-04-11 12:36:00`
- `GET /api/schedules`
  - 主线 `sch-20260405-56eee156`：`last_trigger_at=2026-04-11T12:36:00+08:00 / last_result_status=queued / last_result_summary=assigned agent already has running node`
  - 保底 `sch-20260405-67a89536`：`next_trigger_at=2026-04-11T13:06:00+08:00`
- `GET /api/runtime-upgrade/status`
  - 默认：`current=20260411-093051 / candidate=20260411-123453 / running_tasks_present / can_upgrade=false`
  - 排除当前主线节点后：`candidate_is_newer=true / can_upgrade=true`
  - `prod-last-action` 仍是 `20260411-093051`，说明 idle watcher 还没在空窗切版

## 协作判断

- 当前 active 版本仍是 `V1`，本轮继续按 `V1-P2 / 工程质量探测 / 变更控制` 推进，没有跳版。
- 这轮不续挂新的 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate`。
- 当前最值钱的观察点不是继续扩写功能，而是：
  - 等 `prod` 空窗后由 idle watcher 观察是否把 `20260411-123453` 安全切进现网
  - 确认切版后新建的主线/保底节点会继承 `clean_synced(263d1c8)` 的最新发布边界文案，而不是继续沿用旧版 `ahead_clean(1bf2133)` 摘要

## 证据路径

- `.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/assignment_self_iteration_runtime.py`
- `.repository/pm-main/scripts/acceptance/verify_assignment_self_iteration_schedule_alignment.py`
- `.repository/pm-main/.test/20260411-122555-362/report.md`
- `.repository/pm-main/.test/20260411-122555-492/report.md`
- `.repository/pm-main/.test/20260411-122650-711/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260411-122800.md`
- `.running/control/reports/test-gate-20260411-123453.json`
- `.running/control/prod-candidate.json`
- `.running/control/prod-last-action.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-122033-b3d95c/run.json`

## 下一步

- 当前泳道/阶段 next: `工程质量探测 / 变更控制`
- 主线 next: 当前 `node-sti-20260411-0204ed75` 仍在 running，`node-sti-20260411-642f9d9a` 已 ready 接棒
- 保底 next: `pm持续唤醒 - workflow 主线巡检 -> 2026-04-11T13:06:00+08:00`
- 升级 next: 优先观察 idle watcher 是否在空窗将 `candidate=20260411-123453` 切进 `prod`
- 文案 next: 升级后继续核对新的主线/保底节点是否继承 `clean_synced / 263d1c8` 的最新 release boundary 快照

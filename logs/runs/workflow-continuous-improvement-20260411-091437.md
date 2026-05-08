# continuous-improvement-report

- report_time: `2026-04-11T09:15:26+08:00`
- ticket/node: `asg-20260327-223335-b79f27 / node-sti-20260411-e448d221`
- active_version: `V1 工程质量基线与运行稳态`
- lane: `测试探测`
- lifecycle_stage: `基于基线测试`
- baseline: `prod=20260411-040421`
- root_sync_snapshot: `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=- / next_push_batch=待切批 / workspace_head=7a54432 / code_root_head=7a54432`

## 本轮结论

1. 这轮没有命中发布边界异常，也没有命中可执行升级窗口。`pm-main` 与 `../workflow_code` 都在 `7a54432`，相对 `origin/main` 为 `0 0`；`/api/runtime-upgrade/status` 显示 `current=candidate=20260411-040421`，在续挂 helper 前排除当前主线节点后也只回落为 `blocking_reason=no_candidate / can_upgrade=false`。
2. `03:43` 混合故障里属于代码面的部分，已经被当前 `HEAD=7a54432` 覆盖。我用 `test-session-manager` 会话化跑了 `python scripts/acceptance/verify_training_registry_assignment_runtime_status.py` 与 `python scripts/acceptance/verify_assignment_self_iteration_plan_reference.py`，两条都 PASS，说明 training registry runtime-status 口径与 self-iteration prompt 合同已在当前代码上收住。
3. 这轮最高价值动作不是再开本地修复批次，而是把 `V1-P3` 的现网回归真正挂起来。我通过受支持的 assignment API 新建并派发了 `workflow_testmate` 节点 `node-20260411-091255-d2a674 / arun-20260411-091332-d85386`，要求它基于当前 `prod=20260411-040421` 复核 `03:43` 故障里的 runtime-status 漂移与 PowerShell/路径误用信号是否仍会复现。
4. 当前 live 现场已经收口为“两条真实 running + 一条确定 future patrol”：主线 `workflow=node-sti-20260411-e448d221 / arun-20260411-090622-b61cdd` 仍在 running，`workflow_testmate=node-20260411-091255-d2a674 / arun-20260411-091332-d85386` 已进入 running，保底 schedule 仍保留在 `2026-04-11T09:36:00+08:00`。因此这轮不是空转，也没有断链。
5. `workflow_testmate` 这条回归 run 还没给出最终 verdict。截止 `2026-04-11T09:18:27+08:00`，它的 `status-detail` 仍是 `running`，recent events 已出现对 `workflow_testmate/scripts/collect_v1p3_prod_regression.ps1` 的就地更新；与此同时，`stderr.txt` 里也已经留下 `.agents/skills/test-session-manager` 路径探测误用和 `Get-PatternMatches` 对空字符串报错两条 helper 侧信号。当前应把它视为 `V1-P3` 的即时阻塞，而不是主线断链。

## 验证证据

- Git 真相：
  - `git -C .repository/pm-main status --short --branch`
  - `git -C .repository/pm-main rev-parse --short HEAD`
  - `git -C .repository/pm-main rev-list --left-right --count origin/main...main`
  - `git -C ../workflow_code status --short --branch`
  - `git -C ../workflow_code rev-parse --short HEAD`
  - `git -C ../workflow_code rev-list --left-right --count origin/main...main`
- 运行态：
  - `Invoke-RestMethod 'http://127.0.0.1:8090/healthz'`
  - `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
  - `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
  - `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260327-223335-b79f27&exclude_assignment_node_id=node-sti-20260411-e448d221'`
  - `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-20260411-091255-d2a674'`
- 定向验收：
  - `.repository/pm-main/.test/20260411-091029-439/report.md`
  - `.repository/pm-main/.test/20260411-091042-509/report.md`
- 任务图与审计：
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-090622-b61cdd/run.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-091332-d85386/run.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-091332-d85386/stderr.txt`

## 下一步

- 当前泳道/阶段 next: `测试探测 / 基于基线测试`
- 主线 next: 当前 `[持续迭代] workflow / 2026-04-11 09:06:00` 仍在 `running`，下一次 mainline once 将在本轮 finalize 时自动续挂。
- 保底 next: `pm持续唤醒 - workflow 主线巡检 -> 2026-04-11T09:36:00+08:00`
- helper next: 等 `workflow_testmate=node-20260411-091255-d2a674 / arun-20260411-091332-d85386` 回传“是否仍可复现”的结构化回归结论。
- route next: 若 testmate 自修脚本后仍能复现，则继续走正式缺陷链；若不可复现，则把 `03:43` 混合故障收口为“旧版本/旧执行方式遗留问题，当前版本已覆盖”。

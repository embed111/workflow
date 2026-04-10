# 持续迭代报告

- ticket_id: `asg-20260407-103450-fb8ba8`
- node_id: `node-sti-20260408-e3941a63`
- active_version: `V1`
- active_package: `V1-P0 / V1-P1` 继续受 live 运行门禁约束，本轮实际补齐 `V1-P2` 的发布链噪音收口

## 现场结论
- 截至 `2026-04-08T00:54:05+08:00`，live `prod` 仍在运行 `node-sti-20260408-e3941a63`；`/api/status` 与 `/api/runtime-upgrade/status` 一致返回 `running_task_count=1`、`can_upgrade=false`，因此这轮没有执行 `POST /api/runtime-upgrade/apply`。
- 当前 `prod` 版本仍是 `20260407-200414`，但 `prod candidate` 已刷新到 `20260408-005244`，证据在 `.running/control/prod-candidate.json` 与 `.running/control/logs/test/deploy-20260408-005244.json`。
- 7x24 主链没有断：保底巡检计划 `sch-20260407-5ef5e5c8` 仍保留 `2026-04-08T01:11:00+08:00` 的 future 入口。

## 本轮推进
- 我先复现并钉实了一个持续污染发布证据的 `V1-P2` 工程问题：`workflow gate` 默认复用固定 `.test/runtime/workflow-gate` 时，旧 run 清理不完整会让 `developer_workspace_bootstrap` 误报 `workspace_not_git_repo`。
- 我在 `scripts/acceptance/run_acceptance_workflow_gate.py` 把默认隔离 runtime 根改成每轮唯一目录，只在显式传 `--runtime-root` 时才复用固定根。
- 这组改动已通过 `check_workspace_line_budget`、`py_compile` 和整条 `workflow gate`；修复后的 gate 证据见 `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260408-005043.md`，其中 `developer_workspace_bootstrap` 已从 `pass: false` 变为 `pass: true`。
- 代码已提交并推回 `workflow_code/main`：`8611bf4 fix(workflow): isolate workflow gate runtime roots`。

## 验证与证据
- `python scripts/quality/check_workspace_line_budget.py --root .`
- `python -m py_compile scripts/acceptance/run_acceptance_workflow_gate.py`
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy_workflow_env.ps1 -Environment test`
- `Invoke-RestMethod http://127.0.0.1:8090/api/status`
- `Invoke-RestMethod http://127.0.0.1:8090/api/runtime-upgrade/status`
- 关键证据：
  - `docs/workflow/governance/PM版本推进计划.md`
  - `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260408-005043.md`
  - `.running/control/prod-candidate.json`
  - `.running/control/logs/test/deploy-20260408-005244.json`
  - `memory_ref=.codex/memory/2026-04/2026-04-08.md`

## 下一步
- 升级 next: 等当前 `node-sti-20260408-e3941a63` 收尾后，立刻复核 `/api/runtime-upgrade/status`；若 `running_task_count=0` 且 `can_upgrade=true`，直接 `apply 20260408-005244`。
- 保底 next: `sch-20260407-5ef5e5c8 -> 2026-04-08T01:11:00+08:00`
- 协作 next: `prod` 升完后优先重跑 `workflow_testmate / workflow_devmate / workflow_bugmate / workflow_qualitymate` 的真实任务，验证 teammate memory bootstrap 修复已经在 live 接管。

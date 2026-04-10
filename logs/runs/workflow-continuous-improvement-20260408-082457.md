# Workflow Continuous Improvement - 2026-04-08 08:24:57+08:00

## 本轮结论
- 当前 active 版本仍是 `V1`，本轮继续收口 `V1-P0 / V1-P2`：解决“当前还不能升级 prod 时，升级接力仍然要靠人工守空窗”的连续性缺口。
- 截至 `2026-04-08T08:24:57+08:00`，live `prod` 仍是 `20260407-200414`；`/api/runtime-upgrade/status` 返回 `candidate=20260408-082257`、`running_task_count=1`、`can_upgrade=false`，当前运行槽由 `node-sti-20260408-3e5c5ab6` 占用，所以本轮没有直接 `apply`。
- 我已新增 `scripts/apply_prod_candidate_when_idle.py` 和定向验收 `scripts/acceptance/verify_apply_prod_candidate_when_idle.py`，并将其接入 `workflow gate`。改动已提交 `d6d468e fix(workflow): auto-apply prod candidate when idle` 并推回 `workflow_code/main`。
- `test` 已刷新到 `20260408-082257`，`prod candidate` 也已刷新为 `20260408-082257`。更关键的是，live 现场已经真实挂起 watcher 进程 `PID=21240`，日志位于 `.repository/pm-main/logs/runs/prod-idle-upgrade-watcher-live-20260408-0823.md`；它会在首个 `running_task_count=0 && can_upgrade=true` 的空窗自动调用 `/api/runtime-upgrade/apply`。

## 本轮改动
- `.repository/pm-main/scripts/apply_prod_candidate_when_idle.py`
  - 新增外部 idle-upgrade watcher，只轮询 `/api/runtime-upgrade/status`，满足 `running_task_count=0 && can_upgrade=true` 后才发起 `/api/runtime-upgrade/apply`。
  - apply 后继续轮询，直到确认 `current_version` 已切到目标 candidate，或者超时写明失败。
- `.repository/pm-main/scripts/acceptance/verify_apply_prod_candidate_when_idle.py`
  - 使用本地 mock `runtime-upgrade` HTTP 服务验证 watcher 会先等待 `running_task_count=1`，后在 `running_task_count=0` 时自动 apply。
- `.repository/pm-main/scripts/acceptance/run_acceptance_workflow_gate.py`
  - 把新验收纳入 `workflow gate`，避免 watcher 只是一段“本轮临时脚本”。

## 验证与证据
- 行数门禁：`.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- 定向验收：`python scripts/acceptance/verify_apply_prod_candidate_when_idle.py`
- 整条门禁：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260408-082132.md`
- 代码提交：`d6d468e fix(workflow): auto-apply prod candidate when idle`
- `test` 部署：`.running/control/logs/test/deploy-20260408-082257.json`
- 当前 `prod candidate`：`.running/control/prod-candidate.json`
- live watcher 日志：`.repository/pm-main/logs/runs/prod-idle-upgrade-watcher-live-20260408-0823.md`
- live runtime 真相：
  - `/api/status`：当前只有 `node-sti-20260408-3e5c5ab6` 处于 `running`
  - `/api/runtime-upgrade/status`：`current=20260407-200414`、`candidate=20260408-082257`、`running_task_count=1`、`can_upgrade=false`
  - `/api/status.schedule_total`：旧 prod 仍显示 `4` 条 active schedule，等待新 candidate 接管后再验证是否收口到真实主线 + 保底 `2` 条

## 下一步
- 主线 next：当前 `node-sti-20260408-3e5c5ab6` 仍在 `running`，等它收尾后优先复核是否已经回写出新的 `[持续迭代] workflow` future 时间。
- 保底 next：`sch-20260407-5ef5e5c8 -> 2026-04-08T08:39:00+08:00`
- 升级 next：watcher 已在等待；一旦 `running_task_count=0 && can_upgrade=true`，它就会自动 `apply 20260408-082257`
- memory_ref: `.codex/memory/2026-04/2026-04-08.md`

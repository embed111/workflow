# Continuous Improvement Report

## 判断
- `version_transition_decision=stay(V5)`
- 我这轮把主线切到 `V5-R6` 的健康项目默认首页真 bug，而不是继续重复上一拍的 candidate 刷新：live `/api/dashboard.project_task_summary` 里，`project-comics-smoke` 在没有活跃任务时仍默认落到 `项目产出`，这和“默认首页体验更顺手”的目标直接冲突。
- 当前还不能切到 `V6`：`next_activation_ready=false` 仍没变，`V5-R6` 也还缺 `candidate=20260421-095758` 升上 prod 后的 live 回归，以及更细的 UCD/项目态摘要层次收口。

## 取舍
- 我没有先去修 `refresh_pm_current_version_snapshot.py` 的 numbered snapshot 债务；这条债务继续记账，但本轮更值钱的是先把 live 暴露出来的默认首页错位修掉。
- 我也没有把这条切片拆给 helper 并发实现；这轮更像一块连贯的 `project-ops` 前后端 + 验收 + 发布收口，所以我直接做完，再把 `pm-main + 5` 个 helper developer workspace 全部 refresh 到 `d76fddb`。

## 下一动作
- 等 idle watcher 把 `095758` 升上 prod 后，我先补一轮 live `project-ops` 回归，确认健康项目会默认回 `项目首页`，而不是继续落到 `项目产出`。
- 回归通过后，我再继续细化 `V5-R6` 的摘要层次和首页信息密度，并在那之后重检 `V6 activation readiness`。

## 证据
- 发布边界：`root_sync_state=clean_synced ; ahead_count=0 ; dirty_tracked_count=0 ; untracked_count=0 ; workspace_head=code_root_head=d76fddb ; push_block_reason=- ; next_push_batch=V5-R6 095758 升级后回归与更细 UCD 批`
- 代码收口：`pm-main=../workflow_code=d76fddb`
- 验证：
  - `.repository/pm-main/.test/20260421-095253-970/report.md`
  - `.repository/pm-main/.test/20260421-095254-033/report.md`
  - `.repository/pm-main/.test/20260421-095254-036/report.md`
  - `.repository/pm-main/.test/20260421-095312-474/report.md`
  - `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260421-095625.md`
- 部署与 live：
  - `.running/control/logs/test/deploy-20260421-095758.json`
  - `/api/runtime-upgrade/status => current=20260421-092938 / candidate=20260421-095758 / candidate_is_newer=true / can_upgrade=false / drain_active=true`
  - `/api/dashboard.project_task_summary => workflow:outputs:活跃 3 条 / 失败 1 条 ; project-comics-smoke:outputs:最近留痕 1 条`
  - `/api/config/developer-workspaces => pm-main + 5 helpers = clean_synced@d76fddb`
- preference_ref: `state/user-preferences.md`
- delta_observation: 我这轮确认 `project_ops` 默认首页的真正剩余 gap 不是“再做点摘要”，而是 healthy project 仍会被 recent success 错拉去 `outputs`；同时 test-session-manager 并行写 `history.jsonl` 会发生写锁竞争，所以完整 gate 改回串行。
- delta_validation: 等 `095758` 升上 prod 后，先做 live project-ops 回归，再决定要不要把更细 UCD 切给 helper。
- memory_ref: `.codex/memory/2026-04/2026-04-21.md`

# workflow 持续迭代报告

- updated_at: `2026-04-11T20:23:43+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260411-2fe5e57d`
- active_version: `V1`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- baseline: `prod=20260411-093051`
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`

## 本轮结论
- 我把 `V1-P2` 当前最直接的发布链阻塞，从“健康 `test` 环境挡住 candidate 刷新，但没有受支持停测入口”推进成了“新 `candidate=20260411-202044` 已经就位，只等当前 mainline run 释放后由 idle watcher 接管升级”。
- 当前主链没有断。live `prod` 仍是 `20260411-093051`，但 `node-sti-20260411-2fe5e57d / arun-20260411-194830-0a1e2a` 还在真实运行，`19:51` 主线和 `20:21` 保底也都已经是 ready 出口。

## 根仓同步快照
- 当前节点 prompt 继承的旧快照：`root_sync_state=ahead_clean / ahead_count=7 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=unpushed_commits_present / next_push_batch=待切批`
- 当前 live schedules 继承的旧快照：`root_sync_state=ahead_clean / ahead_count=8 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=unpushed_commits_present / next_push_batch=待切批`
- 我本轮实测后的真实发布边界：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=- / next_push_batch=待切批 / workspace_head=code_root_head=806aef2`
- 说明：`pm-main / workflow_code` 相对 `origin/main` 仍是 `ahead 9`，但这里只继续作为上游参考，不构成本轮阻塞。

## 本轮动作
1. 我在 `.repository/pm-main` 新增了受支持的 `scripts/stop_workflow_env.ps1`，默认只安全停 `dev/test`，`prod` 仍需显式 `-AllowProdStop`。
2. 我补了 `scripts/acceptance/verify_stop_workflow_env.py`，并把新脚本接进 `verify_powershell_script_parse.py`、`workflow_gate_probe_registry.py` 和 `deploy_workflow_env.ps1` 的 fail-closed 提示。
3. 我按最小验证面跑过 `line budget`、PowerShell 解析验收、新脚本定向验收和 `workflow gate`，随后在 `pm-main` 提交了 `806aef2 feat(release): 补齐test环境受支持停测入口`，再把 `../workflow_code` 快进到同一提交。
4. 我用新脚本真实停掉了健康 `test=20260411-173655 / PID=19724 / port=8092`，再执行 `deploy_workflow_env.ps1 -Environment test`，把 `test` 和 `prod candidate` 一起刷新到 `20260411-202044`。
5. 我追加了一次 `apply_prod_candidate_when_idle.py --single-check` 证据，确认当前 `current=20260411-093051 / candidate=20260411-202044 / running_task_count=1 / can_upgrade=false`，所以这轮继续不主动 `apply`，交给 idle watcher。

## 验证证据
- `git -C .repository/pm-main status --short --branch`
- `git -C .repository/pm-main show --stat --oneline HEAD`
- `git -C ../workflow_code pull --ff-only D:/code/AI/J-Agents/workflow/.repository/pm-main main`
- `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `.repository/pm-main/.test/20260411-201310-526/report.md`
- `.repository/pm-main/.test/20260411-201350-548/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260411-201647.md`
- `.running/control/logs/test/deploy-20260411-202044.json`
- `.running/control/reports/test-gate-20260411-202044.json`
- `.running/control/prod-candidate.json`
- `logs/runs/prod-idle-upgrade-watchdog-live.md`
- `/api/runtime-upgrade/status`
- `/api/status`
- `/api/schedules`
- `/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-2fe5e57d`

## live 现场
- `prod current_version=20260411-093051`
- `candidate_version=20260411-202044`
- `blocking_reason=running_tasks_present / can_upgrade=false`
- 当前真实 running：
  - `node_id=node-sti-20260411-2fe5e57d`
  - `run_id=arun-20260411-194830-0a1e2a`
  - `run_status=running`
  - `latest_event_at=2026-04-11T20:22:21+08:00`
  - `provider_pid=61620`
- 当前 ready 出口：
  - 主线 `node-sti-20260411-4fca706e / [持续迭代] workflow / 2026-04-11 19:51:00`
  - 保底 `node-sti-20260411-925e5ca2 / pm持续唤醒 - workflow 主线巡检 / 2026-04-11 20:21:00`
- `test` 当前已重启为 `20260411-202044`，`8092 /healthz` 正常。
- 当前 live `prod` 仍会继续暴露旧 schedule prompt 和 `/api/status.active_version=disabled`，因为现网还没切到 `806aef2` 对应的新 candidate。

## baseline 与变更控制
- 本轮沿用 baseline：`prod=20260411-093051`
- 本轮变更控制更新：`V1-P2` 从“缺少受支持停测入口，candidate 无法刷新”更新为“已补 supported stop script，并完成一次真实的 commit -> 根仓同步 -> test -> candidate 刷新闭环”
- 这轮没有执行 `/api/runtime-upgrade/apply`，正式升级仍由 `prod` supervisor 托管的 idle watcher 在空窗时发起。

## 下一步
- 当前泳道/阶段 next：`工程质量探测 / 基于基线测试`
- 主线 next：等待当前 `node-sti-20260411-2fe5e57d / arun-20260411-194830-0a1e2a` 释放后，由 ready 主线 `node-sti-20260411-4fca706e / 2026-04-11T19:51:00+08:00` 接棒
- 保底 next：ready 保底 `node-sti-20260411-925e5ca2 / 2026-04-11T20:21:00+08:00`
- 升级 next：若首个真正 idle 窗口后仍未自动升到 `20260411-202044`，下一轮优先验证或重启 `prod supervisor / idle watcher`
- 体验 next：live `prod` 升级后，再继续确认 `/api/status.active_version` 和 schedule prompt 是否从旧 snapshot 收口到新读链

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: 这轮我已经把 `test / prod candidate` 从 `20260411-173655` 刷到 `20260411-202044`，发布链阻塞从“健康 test 挡住刷新”收口为“等待 live prod 空窗自动升级”。
- delta_validation: 下一轮若首个 idle 窗口后 `prod` 仍停在 `20260411-093051`，就继续用 `/api/runtime-upgrade/status`、`prod-idle-upgrade-watchdog-live.md` 和 supervisor 进程真相验证 watcher 是否需要恢复。

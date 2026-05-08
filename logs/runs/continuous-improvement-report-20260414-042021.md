# Continuous Improvement Report

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260414-64a5b876`
- generated_at: `2026-04-14T04:20:21+08:00`
- active_version: `V2`
- lane: `功能开发`
- lifecycle_stage: `开发实现`
- baseline: `prod=20260414-032117`
- release_boundary: `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=99b6cf7`

## 本轮推进
- `V2-R1`：我把 helper 学习报告的 `delivery inbox -> PM learning dir` 回流链补成了正式代码能力；`pm_daily_governance_service.py` 现在会识别当前 PM workspace 下的 helper delivery，并在 `refresh_pm_daily_governance.py` 执行时投影回 `pm/daily-learning-reports/YYYY-MM-DD/<agent_id>.md`。我同时补了 `TC-PM-002`，把这条治理闭环接进 `workflow gate`。
- `V2-R1`：我随后用新脚本把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate` 四份真实学习报告全部投影回 `pm/daily-learning-reports/2026-04-14/`，today daily 已从 `in_progress` 收成 `completed`。
- `V2-R3`：我在 `.repository/pm-main` 提交 `99b6cf7 fix(pm治理): 投影helper学习报告回流并补TC-PM-002`，再把本机 `../workflow_code` fast-forward 到同一批次，并重刷 `test/prod candidate=20260414-041846`。
- `V2-R5`：我复核到 `workflow_ucdmate` 的角色链已经推进到 `rc-5ec949-capability-2 / running`；`persona-1 / persona-2 / capability-1` 都已成功。当前真正剩下的不是“helper 执行链整体起不来”，而是两条旧的 `urgent brief` 失败节点还没有被新的 capability 批次正式接回。

## 验证
- `python scripts/quality/check_workspace_line_budget.py --root .`
- `python -m py_compile src/workflow_app/server/services/pm_daily_governance_service.py scripts/acceptance/verify_pm_daily_governance_tc_pm_002.py scripts/acceptance/workflow_gate_probe_registry.py`
- `.repository/pm-main/.test/20260414-040707-114/report.md`
- `.repository/pm-main/.test/20260414-040821-580/report.md`
- `.repository/pm-main/.test/20260414-040852-197/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260414-041029.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260414-043931.md`
- `.running/control/logs/test/deploy-20260414-041846.json`
- `Invoke-RestMethod http://127.0.0.1:8090/api/status`
- `Invoke-RestMethod http://127.0.0.1:8090/api/runtime-upgrade/status`
- `Invoke-RestMethod http://127.0.0.1:8092/api/status`

## 当前需求评估
- `V2-R1`: `status=in_progress / progress=98% / eta=2026-04-15 / timeout=未超时`
  当前已完成 `TC-PM-001 / TC-PM-002`、today daily completed 和 helper 报告回流闭环；剩余工作是等 `20260414-041846` 切进 live 后补 1 轮 current-version smoke。
- `V2-R2`: `status=in_progress / progress=75% / eta=2026-04-18 / timeout=未超时`
  负责人筛选和细粒度详情卡已稳定，当前无新的超时信号。
- `V2-R3`: `status=in_progress / progress=94% / eta=2026-04-19 / timeout=未超时`
  新 candidate 已刷到 `20260414-041846`；剩余缺口收窄为专项验收编号。
- `V2-R4`: `status=planned / progress=25% / eta=2026-04-19 / timeout=未超时`
  当前仍缺独立治理动作自动化回归切片。
- `V2-R5`: `status=in_progress / progress=60% / eta=2026-04-15 / timeout=未超时`
  角色链已进入 capability 批次，但专属 UCD brief / implementation 还没重新接回。
- `V2-R6`: `status=in_progress / progress=80% / eta=2026-04-15 / timeout=未超时`
  需求映射矩阵仍维持 `28` 份有效文档，无新增超时。
- `V2-R7`: `status=in_progress / progress=75% / eta=2026-04-16 / timeout=未超时`
  证据矩阵与覆盖盲区结论已在位，当前缺口仍是专项编号继续独立化。
- `V2-R8`: `status=completed / progress=100% / eta=已于 2026-04-13 完成 / timeout=-`

## Live 真相
- `prod` 当前为 `20260414-032117`，`candidate=20260414-041846`，`candidate_is_newer=true`，`drain_active=true`，`running_task_count=2`。
- 当前 `7x24` 出口保持为：主线 `node-sti-20260414-64a5b876 / running`，下一条主线 `node-sti-20260414-be2a5456 / ready`，保底 `node-sti-20260414-bfdaf040 / ready`。
- `/api/status` 当前已经追平到 `baseline=document_baseline=prod=20260414-032117`，`pm_daily_governance_status.status=completed`，`missing_learning_reports=-`。
- `workflow_bugmate` 的今日学习节点已成功；`workflow_ucdmate` 当前最新真正活跃节点是 `rc-5ec949-capability-2 / running`，而不是凌晨那两条旧失败节点。

## 风险与下一步
- 当前最高优先的剩余风险是：`workflow_ucdmate` 的专属 UCD brief / implementation 还没重新接到当前 capability 批次。
- 发布侧的唯一即时等待项是：`20260414-041846` 仍需 idle watcher 在空窗切进 `prod`。
- 本轮无需求点超时，因此未新增 `AAR`。
- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-14.md`

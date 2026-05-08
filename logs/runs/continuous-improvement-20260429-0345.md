# continuous-improvement-20260429-0345

- preference_ref: `state/user-preferences.md`
- delta_observation: 用户本轮强调“不能纯观察”，并要求先判断、取舍和下一动作；我把 `030144` live smoke 后的最高价值动作切到 R5 当前质量首债，而不是重复上一轮候选刷新。
- delta_validation: 下一轮继续先看 active 版本退出门槛与 helper artifact，若 `workflow_devmate` slice2 已完成，直接串 review/test；若未完成，按运行态证据判断是否恢复或路由缺陷。

## 判断
- version_transition_decision: `stay`
- 取舍：`prod=20260429-030144` 已经 live smoke 通过，发布等待态结束；但 V13 还不能切 V14，因为 R5 质量流水线仍 fail、slice2 派发结果不完整，R6/R7 未启动，V14 仍 `activation_readiness=not_ready`。
- 下一动作：恢复或重派 `workflow_devmate` 的 `v13-r5-quality-debt-slice2-devmate.md`，再按 R2 门禁串 `workflow_reviewmate -> workflow_testmate`。

## 推进性修改
- 已创建并触发 `workflow_devmate` R5 slice2：`V13-R5 quality debt slice2 - ghost running repair acceptance split`；该 run 最终只返回 planning-only/incomplete result，已标记 failed/recovery required。
- 目标债务：`.repository/pm-main/.test/reports/CODE_QUALITY_PIPELINE_REPORT.md` 中 rank1 `scripts/acceptance/verify_runtime_upgrade_ghost_running_repair.py:102 main`，line_count=`843`。
- helper run: `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260429-040650-335544/`

## 验证
- `/healthz`: `ok=true`
- `/api/status`: `active_version=V13 / truth_mismatch_count=0 / next_activation_ready=false`
- `/api/schedules`: `ok=true`
- `/api/runtime-upgrade/status`: `current_version=20260429-030144 / candidate_version=20260429-030144 / candidate_is_newer=false / request_pending=false / drain_active=false / ghost_running_detected=false`
- git: `.repository/pm-main clean@4ba811c`；`.repository/workflow_devmate clean@4ba811c`（派发后 provider 可能产生新改动）；`../workflow_code clean@4ba811c`。

## 现场备注
- `create_node/dispatch-next` HTTP 客户端调用出现超时；run/events 显示 provider 一度启动，但最终结果不完整。我已收敛 run/node 为 failed/recovery required，释放 stale claim，并复查 ghost=false。
- 本轮没有新增超时需求，不触发 AAR。

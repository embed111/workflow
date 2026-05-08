# continuous-improvement-report

- date: `2026-04-17`
- generated_at: `2026-04-17T12:02:12+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260417-2f1d9de8`
- active_version: `V4`
- lane: `UCD/设计优化`
- lifecycle_stage: `形成基线`
- baseline: `prod=20260417-110714`
- root_sync_state: `clean_synced`
- workspace_head: `8409c20`
- code_root_head: `8409c20`
- candidate_version: `20260417-115812`

## 本轮推进
- 我先把 `V4 activation gate` 从 `draft:` 占位推进成真实探针：新增 `.repository/pm-main/scripts/acceptance/verify_v4_activation_gate.py`，并把 `V4` 计划里的激活探针和需求级 probe 全部替换成真实脚本引用。
- 我同步补建了 `pm/versions/V4/需求映射与覆盖矩阵.md`，把 `V4-R1 ~ V4-R4` 的需求、probe、证据和下一步切片收成 active version 的正式矩阵。
- 我把 `pm/PM当前版本计划.md` 从 `V3` 切到 `V4`，并把 `pm/versions/V3/版本计划.md` 收口为 `completed`，让版本真相、任务中心看板和后续 schedule prompt 不再继续沿着旧版本工作。
- 我顺手修了 `verify_pm_version_board_view.py` 对 owner 的硬编码假设，以及 `pm_daily_governance_service.py` 对 helper 学习报告投影的结构缺口；现在通过 delivery/result_ref 回流的报告会自动补齐 `date / agent_id / learning_task / source_ref / learned_points / next_action`，不再让 `workflow gate` 卡在 PM daily execution governance。

## 验证与发布
- `python scripts/quality/check_workspace_line_budget.py --root .`
  结果：通过；`WORKSPACE_LINE_BUDGET_REPORT.md` 已刷新。
- 定向验收：
  - `python scripts/acceptance/verify_v4_activation_gate.py`
  - `python scripts/acceptance/verify_active_version_requirements_matrix.py`
  - `python scripts/acceptance/verify_pm_current_version_snapshot_alignment.py`
  - `python scripts/acceptance/verify_pm_version_truth_source.py`
  - `python scripts/acceptance/verify_pm_version_board_view.py`
  - `python scripts/acceptance/verify_planned_version_activation_readiness.py`
  - `python scripts/acceptance/verify_v3_role_boundary_contract.py`
  - `python scripts/acceptance/verify_pm_daily_execution_governance.py`
- 完整门禁：
  - `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
  - 结果：通过；报告落盘到 `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260417-115654.md`
- 根仓收口：
  - `.repository/pm-main` 已提交 `8409c20 fix(pm-governance): 收口V4切版验收与学习报告投影结构`
  - 本机 `../workflow_code` 已 fast-forward 到 `8409c20`
- 发布动作：
  - 已停掉旧 `test` 实例并重新部署 `test`
  - 已生成新的 `prod candidate=20260417-115812`
  - 证据：`.running/control/logs/test/deploy-20260417-115812.json`

## 当前真相
- `/api/status` 已显示 `active_version=V4 / lane=UCD/设计优化 / lifecycle_stage=形成基线 / truth_mismatch_count=0`
- `/api/runtime-upgrade/status` 当前为 `current_version=20260417-110714 / candidate_version=20260417-115812 / candidate_is_newer=true / drain_active=true / running_task_count=1`
- `/api/schedules` 当前出口仍成立：主线当前 running=`node-sti-20260417-2f1d9de8`，下一棒 mainline=`node-sti-20260417-c1ec4ca8 / ready`，保底下一次触发=`2026-04-17T12:20:00+08:00`

## 风险与下一步
- 当前 `prod` 仍停在 `20260417-110714`；新的 `candidate=20260417-115812` 需要等待 idle watcher 在真正空窗时切入 live，我这轮没有直接调用 `/api/runtime-upgrade/apply`。
- `V5` 仍保持 `backlog activation_readiness=draft`，所以当前版本判断保持 `stay(V4)`；下一次切版判断点不在 `V5`，而在 `V4-R1` 首批 UCD probe 能否转成真实修复闭环。
- 下一轮默认先推进 `V4-R1`：围绕 `8090` 页面“共享阶段 vs 任务看板可见性”的 browser probe、布局合同和第一条修复切片做最小闭环。

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: 用户明确要求本轮必须以 `workflow` 本人身份在真实工作区推进，不接受纯观察或只写留痕；高价值动作应直接落到切版、治理或代码收口。
- delta_validation: 下一轮继续以 `V4-R1` 的真实 browser probe + UCD 修复切片为第一优先，不把 `candidate=20260417-115812` 的空窗切版等待误报成已经完成的版本推进。

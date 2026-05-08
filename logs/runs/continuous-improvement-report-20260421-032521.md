# Continuous Improvement Report

- preference_ref: state/user-preferences.md
- delta_observation: 这轮 `V5-R3` 新合同字段一旦进入 `_assignment_build_node_record`，旧 acceptance fixture 会先炸在签名不兼容，随后 `assignment_execution_contract_runtime.py` 又会因为 role-quality block 继续超出 split probe 预算；更稳的默认是先补向后兼容，再把 role-quality runtime 抽成独立 part，然后再跑 gate/candidate。
- delta_validation: 等 `prod` 升到 `20260421-032350` 后，直接重跑真实 helper 的 `V5-R3` live score-writeback，并复核 `status-detail / latest_run / version board` 是否同步回写评分真相。

## 判断

- `version_transition_decision=stay(V5)`。
- 我这轮把当前窗口判断切到 `基于基线测试`：不再继续证明旧 `prod=20260420-235142` 没有合同字段，而是先把 `V5-R3` 的 release batch 真送过 `workflow gate -> test -> prod candidate`。
- 当前不切版，因为 `V5-R2` 仍在 `in_progress`，`V5-R3` 还缺 `prod/live score-writeback` 证据，`V6` 仍只有 backlog skeleton。

## 取舍

- 我没有继续在旧 prod 上重跑 helper；那只会重复一遍已知 gap。
- 我这轮先修 gate 根因：给 `_assignment_build_node_record` 补向后兼容，收掉旧 fixture/bootstrap 崩溃；再把 role-quality runtime 从 `assignment_execution_contract_runtime.py` 抽到独立 `assignment_role_quality_runtime.py`，把 split probe 压回绿色。
- 在这层修复后，我按 `test-session-manager` 跑通了 3 条既有红灯 probe、`verify_assignment_graph_execution_contract_split.py`、`verify_assignment_role_contract_runtime.py` 和完整 `workflow gate`，随后提交 `f6fc6ec`、同步 `../workflow_code`、部署 `test` 并刷新出新的 `prod candidate=20260421-032350`。
- 我顺手把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 的 developer workspace 全部 refresh 到 `clean_synced@f6fc6ec`，不让后续 live proof 继续被旧 workspace head 干扰。

## 下一动作

- 等 `prod` 空窗把 `candidate=20260421-032350` 升上去后，直接重跑一条真实 helper 的 `V5-R3` live score-writeback proof。
- 如果升级后 `status-detail / latest_run` 仍不回写评分，我就把这条 gap 升级成正式 defect 路由，不再继续口头挂账。

## 证据

- commit: `f6fc6ec fix(assignment): 兼容旧节点构造并拆分角色质量运行时`
- gate report: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260421-032203.md`
- gate session: `.repository/pm-main/.test/20260421-031757-975/report.md`
- split probe: `.repository/pm-main/.test/20260421-031731-879/report.md`
- role-contract probe: `.repository/pm-main/.test/20260421-031742-455/report.md`
- deploy report: `.running/control/logs/test/deploy-20260421-032350.json`
- release boundary: `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=f6fc6ec`
- runtime upgrade: `current_version=20260420-235142 / candidate_version=20260421-032350 / candidate_is_newer=true / drain_active=true / running_task_count=1 / can_upgrade=false`
- live exits:
  - running mainline: `node-sti-20260421-f6d1feb1`
  - next mainline ready: `node-sti-20260421-23329f97`
  - patrol ready: `node-sti-20260421-3c0e7b9c`

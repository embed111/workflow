# Continuous Improvement Report

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260417-ae4f0367`
- active_version: `V4`
- current_lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- version_transition_decision: `stay(V4)`
- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-17.md`

## Summary

- 我先修掉了 `pm_version_status` 对 `当前最高价值泳道切回` / `生命周期阶段已推进到` 的解析缺口，现网 `8090 /api/status.pm_version_status.lane/lifecycle_stage` 已从空白恢复为 `工程质量探测 / 基于基线测试`。
- 我同步补上 `verify_pm_version_truth_source.py`、`verify_pm_current_version_snapshot_alignment.py` 的 `V4` 回归夹具，并串行跑通 `line budget + 两条定向 acceptance + workflow gate`。
- 代码已提交为 `.repository/pm-main@e114983 fix(pm-version): 兼容V4切回与推进到快照句式`，并通过受支持的 `../workflow_code fetch + ff-only merge` 收口到 `../workflow_code@e114983`。
- 我停掉旧 `test` 后重新部署，刷新出新的 `prod candidate=20260417-194345`。
- 我随后又对 `8092` 执行了受支持的 `/api/runtime-upgrade/repair-ghost-running`，把历史 `T9` 假 running 收回终态；当前 `test` 已是 `ghost_running_detected=false / running_task_count=0`。

## Validation

- `line budget`: `.repository/pm-main/.test/20260417-193715-283/report.md`
- `verify_pm_version_truth_source.py`: `.repository/pm-main/.test/20260417-193728-696/report.md`
- `verify_pm_current_version_snapshot_alignment.py`: `.repository/pm-main/.test/20260417-193738-795/report.md`
- `workflow gate`: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260417-194242.md`
- `test deploy`: `.running/control/logs/test/deploy-20260417-194345.json`
- `prod live`: `http://127.0.0.1:8090/api/status` 已恢复 `lane=工程质量探测 / lifecycle_stage=基于基线测试 / baseline=document_baseline=prod=20260417-191531`
- `prod upgrade status`: `http://127.0.0.1:8090/api/runtime-upgrade/status` 当前为 `current_version=20260417-191531 / candidate_version=20260417-194345 / candidate_is_newer=true / drain_active=true / running_task_count=1`
- `test live`: `http://127.0.0.1:8092/api/status` 当前为 `lane=工程质量探测 / lifecycle_stage=基于基线测试`
- `test upgrade status`: `http://127.0.0.1:8092/api/runtime-upgrade/status` 当前为 `current_version=20260417-194345 / ghost_running_detected=false / running_task_count=0`

## Active Requirements

- `V4-R1`: `in_progress / 70% / eta=2026-04-19 / 未超时`
- `V4-R2`: `planned / 5% / eta=2026-04-20 / 未超时`
- `V4-R3`: `planned / 10% / eta=2026-04-20 / 未超时`
- `V4-R4`: `in_progress / 95% / eta=2026-04-20 / 未超时`
- 本轮没有需求点超时，不新增 `AAR`。

## Release Boundary

- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `workspace_head=code_root_head=e114983`
- `git -C .repository/pm-main status --short --branch` 当前为 `## main...origin/main [ahead 3]`
- `git -C ../workflow_code status --short --branch` 当前为 `## main...origin/main [ahead 118]`
- 上述 `ahead` 都是相对远端 tracking 的视图；当前本地 `workspace -> code_root` 已 clean synced，不属于本轮 boundary 阻塞。

## Live Status

- `prod` 仍在 `20260417-191531`，但新的 `candidate=20260417-194345` 已生成；当前 `running_task_count=1`，idle watcher 需要等空窗才会自动切版。
- `prod` 当前主线节点仍是 `node-sti-20260417-ae4f0367`；下一条 mainline 已 ready：`node-sti-20260417-58114eb5`。
- 下一次 patrol 触发时间为 `2026-04-17T20:00:00+08:00`，对应节点 `node-sti-20260417-737bedab` 已 ready。
- `V5` 仍是 `backlog activation_readiness=draft`，`next_activation_ready=false`，本轮继续保持 `stay(V4)`。

## Next

- 等 idle watcher 在空窗把 `candidate=20260417-194345` 切进 `prod`。
- 切版后优先复跑 `pm_version_status` current-version truth smoke 与首屏 materialization regression。
- 若 `194345` live 后仍有任一项不通过，下一轮直接切最小实现或文案收口，不继续让 live 风险原样滚动。

## Snapshot Addendum

- preference_ref: `state/user-preferences.md`
- delta_observation: `你这轮明确要求我以 workflow 本人身份执行，并且必须在真实工作区里完成一项推进性修改；我继续按“先读链、再动手、最后给结构化交付”的口径收口。`
- delta_validation: `下一轮我优先验证 idle watcher 把 194345 切进 prod 后，pm_version_status truth 与首屏 regression 是否同步转绿。`

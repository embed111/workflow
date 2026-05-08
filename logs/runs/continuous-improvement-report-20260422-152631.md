# Continuous Improvement Report

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260422-80ff1524`
- generated_at: `2026-04-22T15:26:31+08:00`
- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-22.md`

## 判断

- 我这轮继续 `stay(V8)`，不切到 `V9`。
- 当前最高价值动作已经从“等待 workflow_bugmate 结果”切到“把已验证的 `V8-R6` 补丁收口进 code root/test candidate，并为下一刀 current-baseline live rerun 清场”。
- `V8` 当前更准确的生命周期阶段已经切到 `基于基线测试`：`V8-R6` 补丁已经过 `line budget + focused probe + workflow gate`，并进入 `test/current=candidate=20260422-152401`；但 `V8-R2 / V8-R3 / V8-R5 / V8-R6` 还没全部完成。

## 取舍

- 我没有继续在旧 `prod=current=20260422-132411` 上 front-run 新的 helper rerun，因为那会把验证继续绑在旧 baseline 上。先把补丁进 `workflow_code@3ac8be0` 和 `test=20260422-152401`，才有资格谈 current-baseline exact readback。
- 我也没有把首轮 `workflow gate` 的失败误记成 self-readback 补丁回归。真实 blocker 是 `pm_version_board_view` 读链被当前版本判断里的嵌套反引号截断，导致 `switch_blockers / recheck_trigger` 读空；修正版本快照写法后，专项 probe 和第二轮完整 gate 都转绿。
- 我把 `pm-main / workflow_bugmate / workflow_testmate / workflow_qualitymate / workflow_ucdmate` 一次性追到 `3ac8be0`，把这轮 warning 收敛到真正还没收的 `workflow_devmate ahead_dirty@52e2efb`，不再让测试/质量/UCD 工作区继续挂在旧提交上误导后续判断。

## 下一动作

- 先在 `test=20260422-152401` 或 `prod` 升到 `candidate=20260422-152401` 后补一条 exact `api_catalog_live_regression` rerun。
- rerun 后只回读三处：
  - `/api/platform/interfaces/platform.interfaces.list`
  - `/api/platform/interfaces/platform.interfaces.detail`
  - `/api/status` 里的 `project_task_summary.interface_catalog_entry`
- 再把 `workflow_ucdmate` 的 `v8-r3-phase2-detail-strip-impl` 接进 targeted regression，收掉 `V8-R3` 最后一段“实现已交付但还没回归”的尾巴。

## 必要证据

- 代码批次：`workflow_bugmate` 提交 `3ac8be0`
- focused 验证：`.repository/workflow_bugmate/.test/20260422-151101-148/report.md`
- PM 版本看板回归：`.repository/workflow_bugmate/.test/20260422-151745-439/report.md`
- 完整门禁：`.repository/workflow_bugmate/.test/runs/workflow-gate-acceptance-20260422-152155.md`
- 发布证据：`.running/control/logs/test/deploy-20260422-152401.json`
- 当前运行态：
  - `prod current=20260422-132411 / candidate=20260422-152401 / candidate_is_newer=true / drain_active=true / running_task_count=1`
  - `test current=20260422-152401 / candidate=20260422-152401 / running_task_count=0`
- 工作区真相：`state/developer-workspaces.json`

## 受控 Warning

- `pm/daily-execution-history/2026-04-20.md` 仍缺失，`2026-04-21.md` 与 `2026-04-22.md` 仍未补齐。
- `pm/daily-learning-reports/2026-04-22/` 仍未补齐。
- `workflow_devmate` developer workspace 仍是 `ahead_dirty@52e2efb`，这条要单独切批收口。

# 任务历史归档与核心用例补强记录

- created_at: `2026-04-26T19:35:00+08:00`
- preference_ref: `state/user-preferences.md`
- code_workspace: `.repository/pm-main`
- code_baseline: `f9f01a9`

## 目标
- 降低任务中心大主图历史文件枚举成本，避免读取/派发热路径继续被旧终态任务拖慢。
- 给历史归档补上安全候选选择用例，避免误归档 running/ready、active dependency、schedule/handoff runtime ref、active run 与最近终态窗口。
- 把系统核心关键点单测/用例补强排入 `V12`。

## 本轮改动
- 新增 `scripts/archive_assignment_history.py`
  - 默认 `dry-run`
  - 显式 `--apply` 才移动旧终态 node/run/artifact
  - 归档目标：`<artifact_root>/archive/assignment-history/<batch_id>/`
  - 归档后写 `manifest.json` 和 assignment audit
- 新增 `scripts/acceptance/verify_assignment_history_archive.py`
- 将 `assignment_history_archive` probe 接入 `scripts/acceptance/workflow_gate_probe_registry.py`
- 更新 `pm/versions/V12/版本计划.md`，新增 `TQ-01..TQ-05` 核心关键点测试补强排期。

## Live Dry-run
命令：

```powershell
python scripts/archive_assignment_history.py --root D:\code\AI\J-Agents\workflow\.running\control\runtime\prod --ticket-id asg-20260327-223335-b79f27 --cutoff-before 2026-04-20T00:00:00+08:00 --keep-recent-terminal 300 --summary-only --json
```

结果：

```json
{
  "scanned_node_count": 1544,
  "candidate_count": 583,
  "skipped_count": 961,
  "skipped_by_reason": {
    "active_or_non_terminal_node": 19,
    "referenced_by_active_node": 6,
    "referenced_by_runtime_state": 553,
    "newer_than_cutoff": 199,
    "kept_by_recent_terminal_window": 184
  }
}
```

## 验证
- Red: `.repository/pm-main/.test/20260426-192406-123/report.md`
- Green: `.repository/pm-main/.test/20260426-193058-675/report.md`
- Compile: `.repository/pm-main/.test/20260426-193058-723/report.md`

## 结论
- 本轮未直接移动生产历史文件。
- 第一批可归档候选已经明确为 `583` 个旧终态节点；建议等当前 PM/helper 接力空窗，或用户明确同意后，用同一命令增加 `--apply` 执行。

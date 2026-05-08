# PM每日执行结果目录

## 定位
- 本目录用于保存 `pm/PM每日任务清单.md` 的执行结果文件。
- 目录本身承担“当天是否已经完成一轮每日任务”的轻量判断，不承接长流水。
- 当前每日任务只包含三类每日一次动作：
  - 系统 7x24 运维质量检查
  - 团队内每个小伙伴每日学习任务与学习报告
  - 界面优化 / UCD 优先级复核

## 文件规则
- 路径模式：`pm/daily-execution-history/YYYY-MM-DD.md`
- 一天只保留 `1` 份文件，允许当天对同一文件持续补充
- 文件存在 = 当天每日例行任务已执行完成
- 文件不存在 = 当天每日例行任务尚未完整执行
- 若当天首轮检查发现文件不存在，不代表必须立刻中断手头动作，但需要在当天合适窗口完成一轮每日任务并落盘

## 建议字段
- `date`
- `source_tasks`
- `status`
- `system_ops_check`
- `learning_prompt`
- `ui_optimization_check`
- `learning_assignments`
- `learning_report_refs`
- `exceptions`
- `next`

## 清理规则
- 本目录只保留最近 `7` 份历史文件。
- 每次写入当天文件后，都要检查是否超过 `7` 份。
- 超过 `7` 份时，从最旧文件开始删除。
- 删除只作用于本目录，不影响：
  - `.codex/memory/**/*.md`
  - `pm/versions/**`
  - `logs/runs/*.md`

## 边界规则
- 本目录不替代 `pm/versions/<version>/history/`。
- 本目录不替代 `.codex` 记忆、运行留痕或现场总览。
- 本目录只回答一件事：今天的每日任务是否已经完整执行过一轮。

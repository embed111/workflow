# Continuous Improvement Report

- 时间：`2026-04-07T17:26:24+08:00`
- active_version：`V1`
- task_package：`V1-P0 / V1-P1`
- memory_ref：`.codex/memory/2026-04/2026-04-07.md`

## 现场结论
- live prod 仍保持 `healthz ok`，当前 running 节点是 `node-sti-20260407-b63812e7`；上一条 `node-sti-20260407-68b5075a` 已在 `2026-04-07T17:15:06+08:00` 以 `assignment execution timeout after 1200s` 收口失败。
- 主链没有断：`[持续迭代] workflow` 下一次主线入口仍在 `2026-04-07T17:45:18+08:00`，保底巡检入口在 `2026-04-07T17:40:00+08:00`。
- 当前最直接的 P0/P1 用户可见偏差是旧 schedule 元数据漂移：`sch-20260407-d7b8f1d6`、`sch-20260407-4c67199b` 在原始 `schedule_plans` 里仍是空白/问号，但修复后的 `schedule_service` 已能从 snapshot/template 回补正确中文，不再让任务中心和计划详情继续展示坏文案。

## 本轮推进
- 在 `pm-main/src/workflow_app/server/services/schedule_service.py` 补齐 schedule 文本 repair 的读写链：list/preview/detail/calendar、scan/recovery、update/enable 全部改为通过 snapshot/template fallback 读取坏掉的 schedule 文本。
- 新增 `pm-main/scripts/acceptance/verify_schedule_text_repair.py` 定向验收，覆盖 list、detail、calendar 和 update 时“拒绝把修好的文案再写回问号”。
- 用新代码直接读取 live prod runtime DB，确认 `sch-20260407-d7b8f1d6` 和 `sch-20260407-4c67199b` 的 list/detail/calendar 结果都能恢复为正确中文。
- 行数门禁硬门通过，但 `schedule_service.py` 命中 refactor trigger/guideline 门槛；本轮先把 live 真相修复方案和验收钉住，发布链留给下一轮连同拆分计划一起决策。

## 验证证据
- `python -m py_compile src/workflow_app/server/services/schedule_service.py scripts/acceptance/verify_schedule_text_repair.py`
- `python scripts/acceptance/verify_schedule_text_repair.py`
- `python scripts/acceptance/verify_dashboard_schedule_preview.py`
- `python scripts/quality/check_workspace_line_budget.py --root .`
- 直接调用修复后的 `schedule_service.list_schedules/get_schedule_detail` 读取 `.running/control/runtime/prod/state/workflow.db`

## 证据路径
- `.repository/pm-main/src/workflow_app/server/services/schedule_service.py`
- `.repository/pm-main/scripts/acceptance/verify_schedule_text_repair.py`
- `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `docs/workflow/governance/PM版本推进计划.md`
- `state/session-snapshot.md`
- `.codex/memory/2026-04/2026-04-07.md`

## 下一步
- 在当前 running 节点结束后继续核对它是否仍正常 self-iteration，尤其盯 `assignment execution timeout after 1200s` 是否继续吞掉长任务。
- 如果下一轮继续走发布链，先补 `schedule_service.py` 的拆分计划，再决定是否把这组 schedule metadata repair 推到 `workflow_code/main -> test -> prod candidate`。

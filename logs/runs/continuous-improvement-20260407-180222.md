# 持续迭代报告

## 本轮结论
- 活跃版本仍是 `V1`，本轮继续推进 `V1-P0 / V1-P1` 的 schedule metadata repair。
- 我把 schedule 文本修复 helper 从 `schedule_service.py` 中抽到 `src/workflow_app/server/services/schedule_text_repair.py`，并把 `verify_schedule_text_repair.py` 修成冻结 `_now_bj()` 的稳定验收，避免当天已过时点把 calendar plan 断言打空。
- 代码已提交 `7e2881a fix(workflow): repair schedule metadata text fallbacks` 并推回 `workflow_code/main`；`test` 与 `prod candidate` 已刷新到 `20260407-180045`。
- live `prod` 目前仍是 `20260407-163227`，所以旧 `sch-20260407-d7b8f1d6 / sch-20260407-4c67199b` 的空白/乱码文案在现网还可见；这部分要等用户手动升级 `prod` 到 `20260407-180045` 后才会消失。
- 当前 7x24 主线没有断：截至 `2026-04-07T18:02:22+08:00`，`node-sti-20260407-6e7a76a8` 正在 `running`，下一次 `[持续迭代] workflow` 入口保留到 `2026-04-07T18:04:00+08:00`，保底唤醒入口保留到 `2026-04-07T18:34:00+08:00`。

## 关键证据
- live prod 真相：
  - `http://127.0.0.1:8090/api/status`：`running_task_count=1`，当前运行节点是 `node-sti-20260407-6e7a76a8`
  - `http://127.0.0.1:8090/api/schedules`：`sch-20260407-20001ab4 -> next_trigger_at=2026-04-07T18:04:00+08:00`，`sch-20260407-5ef5e5c8 -> next_trigger_at=2026-04-07T18:34:00+08:00`
  - 同一份 live prod API 仍可见旧 schedule 元数据漂移：`sch-20260407-d7b8f1d6` 为空白，`sch-20260407-4c67199b` 为乱码，说明现网还没切到本轮 candidate
- 本地修复验证：
  - `python -m py_compile .repository/pm-main/src/workflow_app/server/services/schedule_service.py .repository/pm-main/src/workflow_app/server/services/schedule_text_repair.py .repository/pm-main/scripts/acceptance/verify_schedule_text_repair.py`
  - `python .repository/pm-main/scripts/acceptance/verify_schedule_text_repair.py`
  - `python .repository/pm-main/scripts/acceptance/verify_dashboard_schedule_preview.py`
  - `python .repository/pm-main/scripts/acceptance/run_acceptance_workflow_gate.py --root .repository/pm-main --host 127.0.0.1 --port 8098`
  - 直接用修复后的 `schedule_service` 读取 `.running/control/runtime/prod/state/workflow.db`：`sch-20260407-d7b8f1d6 / sch-20260407-4c67199b` 的 list/detail/calendar 已恢复成正确中文
- 发布链证据：
  - Git 提交：`7e2881a fix(workflow): repair schedule metadata text fallbacks`
  - `workflow gate`：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260407-175859.md`
  - `test` 部署日志：`.running/control/logs/test/deploy-20260407-180045.json`
  - `prod candidate`：`.running/control/prod-candidate.json` 当前为 `20260407-180045`
  - `test` 实例：`.running/control/instances/test.json` 当前为 `20260407-180045`

## 风险与下一步
- `schedule_service.py` 虽然已拆出 `schedule_text_repair.py`，但当前仍是行数门槛超限文件；本轮已完成最小拆分，后续仍需继续补职责拆分计划。
- 本轮没有额外挂给 `workflow_devmate / workflow_bugmate / workflow_testmate / workflow_qualitymate` 的新任务，因为当前最高优先问题已经完成代码修复和发布链刷新，live prod 也仍保留未来入口，不存在“当前没有 ready/future 任务”的断链现场。
- 下一观察点收口到两处：
  - 用户手动把 `prod` 升到 `20260407-180045` 后，`/api/schedules` 与 schedule detail 的空白/乱码是否消失
  - `2026-04-07T18:04:00+08:00` 这条 `[持续迭代] workflow` 主线入口是否继续按当前 handoff 节奏命中

memory_ref: `.codex/memory/2026-04/2026-04-07.md`

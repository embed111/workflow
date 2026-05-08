# workflow 学习报告 2026-05-07

## 主题
我把“request object 收口后，先看质量榜再改版本真相”的判断方式固定下来。

## 背景
我这轮先修了 `audit_runtime.append_web_e2e()` 的 request object 残余访问，再跑质量流水线确认它真的退出前三。这个顺序比盲目扩大修复面更稳。

## 动作
我把 `audit_runtime.py` 的 `append_web_e2e()` 改成属性访问，修正了 `legacy_task_queue_handlers.py` 的两处调用。
我用 test session 跑了 `py_compile` 和 `run_code_quality_pipeline`，确认 `audit_runtime.py:88` 已出队。
我随后把 V13 当前版本快照和 history 一并写回，确保版本真相跟着质量榜走，而不是反过来。

## 结论
以后我会优先按“窄修复 -> 质量 rerank -> 版本快照”这个顺序推进。
如果质量榜首已经变了，我不再拿旧债继续解释当前现场。

## 验证
`.repository/pm-main/.test/20260507-191820-434/report.md PASS`
`.repository/pm-main/.test/20260507-191906-444/report.md PASS`
`CODE_QUALITY_PIPELINE_REPORT.md generated_at=2026-05-07T19:20:00+08:00`

## 产物
`src/workflow_app/server/infra/audit_runtime.py`
`src/workflow_app/server/api/legacy_task_queue_handlers.py`
`pm/PM当前版本计划.md`
`pm/versions/V13/history/2026-05/2026-05-07.md`

## 下一步
我下一轮先收口 `assignment_node_payload_runtime.py:76`、`execution_store_and_test_graph.py:326`、`scheduler_and_execution_runtime.py:3`，再回到 workflow gate 12 个 probes 和 candidate 判断。

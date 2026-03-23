# 角色创建异步发送与批处理 smoke

- time: `2026-03-23T18:41:36.2460600+08:00`
- source_root: `C:\work\J-Agents\workflow`
- topic: 角色创建消息发送改为“立即返回 + 后台批处理 + 已处理/未处理状态”

## 本地 service smoke

- temp_root: `.test/role-creation-async-smoke`
- session_id: `rcs-20260323-181526-b3826e`
- 两次 `post_role_creation_message` 返回耗时: `0.058s` / `0.058s`
- 第一次返回后: `message_processing_status=pending`，`unhandled_user_message_count=1`
- 第二次返回后: `message_processing_status=pending`，`unhandled_user_message_count=2`
- 最终状态: `message_processing_status=idle`，`unhandled_user_message_count=0`
- 两条用户消息最终都为 `processing_state=processed`
- assistant 在欢迎语之后只新增 `1` 条回复，说明两条连续消息被合并进同一轮处理

## test 发布

- version: `20260323-181854`
- deploy_log: `.running/control/logs/test/deploy-20260323-181854.json`
- gate_report: `.running/control/reports/test-gate-20260323-181854.json`
- instance: `.running/control/instances/test.json`
- healthz: `http://127.0.0.1:8092/healthz` 返回 `ok=true`

## test HTTP smoke

- session_id: `rcs-20260323-184019-e23dec`
- 两次消息 POST 返回耗时: `0.152s` / `0.099s`
- 第二次返回后: `message_processing_status=pending`，`unhandled_user_message_count=2`
- 最终状态: `message_processing_status=idle`，`unhandled_user_message_count=0`
- assistant 在欢迎语之后只新增 `1` 条回复

## 备注

- `deploy_workflow_env.ps1 -Environment test -StartAfterDeploy` 本次命令行等待超时，但部署日志、gate 报告、`8092/healthz` 与 `test.json` 均确认版本 `20260323-181854` 已成功上线。
- test gate 通过，但 workspace line budget 仍提示既有大文件预警；本轮功能验证不受影响。

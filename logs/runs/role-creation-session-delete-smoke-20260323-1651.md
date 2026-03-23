# 创建角色列表删除功能 Smoke 2026-03-23

- scope: 为“创建角色”左侧会话列表补充删除能力
- status: completed
- deploy: 未发布；仅完成本地代码与临时 runtime 验证

## 变更

- 后端新增 `DELETE /api/training/role-creation/sessions/{session_id}`
- 删除策略：
  - 允许删除 `draft`
  - 允许删除 `completed`（仅删除创建记录，不删除已生成角色工作区/任务图）
  - 阻止删除 `creating`
- 前端在会话列表卡片增加删除按钮：
  - `draft` 显示 `删除草稿`
  - `completed` 显示 `删除记录`

## 验证

- `python -m py_compile`
  - `src/workflow_app/server/services/role_creation_service_parts/session_commands.py`
  - `src/workflow_app/server/api/training.py`
  - `src/workflow_app/server/api/router.py`
  - `src/workflow_app/server/bootstrap/web_server_runtime_parts/runtime_paths_and_config.py`
- `node --check src/workflow_app/web_client/training_center_role_creation.js`
- 临时 runtime HTTP smoke 结果：

```json
{
  "delete_draft": {
    "session_id": "rcs-20260323-165022-903cc7",
    "deleted_message_count": 1,
    "deleted_task_ref_count": 0,
    "remaining_total": 0
  },
  "delete_creating_block": {
    "session_id": "rcs-20260323-165022-45faf4",
    "status": 409,
    "code": "role_creation_delete_creating_blocked"
  }
}
```

## 关键文件

- `src/workflow_app/server/services/role_creation_service_parts/session_commands.py`
- `src/workflow_app/server/api/training.py`
- `src/workflow_app/server/api/router.py`
- `src/workflow_app/server/bootstrap/web_server_runtime_parts/runtime_paths_and_config.py`
- `src/workflow_app/web_client/training_center_role_creation.js`
- `src/workflow_app/server/presentation/templates/index_training_center_role_creation.css`

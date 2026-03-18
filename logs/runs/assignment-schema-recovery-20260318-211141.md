# Run Log

- topic: assignment schema recovery
- recorded_at: 2026-03-18T21:11:41+08:00
- preference_ref: state/user-preferences.md
- workspace: `D:\code\AI\J-Agents\workflow`
- issue: prod runtime 访问 assignment execution settings 时抛出 `sqlite3.OperationalError: no such table: chat_sessions`
- root_cause: `ensure_tables()` 在完成建表与补列后又无条件删除 `chat_sessions/conversation_messages/task_runs/...`，与启动期 `migrate_legacy_local_work_records()` 叠加后把 runtime DB 留在半初始化状态
- changed_file: `src/workflow_app/server/infra/db/migrations.py`
- changed_file: `.running/prod/src/workflow_app/server/infra/db/migrations.py`
- verification: `.test/20260318-210448-796/report.md`
- verification: `http://127.0.0.1:8090/healthz`
- verification: `http://127.0.0.1:8090/api/training/agents`
- verification: `http://127.0.0.1:8090/api/agents`

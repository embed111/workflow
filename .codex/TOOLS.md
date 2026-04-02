# 工作区工具

## 优先本地命令
- `.\run_workflow.bat`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/launch_workflow.ps1 -OpenBrowser`
- `python scripts/workflow_web_server.py --host 127.0.0.1 --port 8090`
- `python scripts/workflow_entry_cli.py --mode status`
- `python scripts/workflow_entry_cli.py --mode backfill`
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`

## 记忆与技能约定
- `.codex/*` 用于存放 agent 记忆和工作区内部说明。
- `.codex/skills/` 是现有文档与代码约定的本地技能入口。
- `state/*` 继续表示产品运行态；`logs/*` 继续表示审计与执行证据。

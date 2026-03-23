# Test 发布与创建角色回归 2026-03-23

- environment: `test`
- version: `20260323-142105`
- url: `http://127.0.0.1:8092`
- deploy_report: `.running/control/logs/test/deploy-20260323-142105.json`
- test_gate_evidence: `.running/control/reports/test-gate-20260323-142105.json`

## 处理过程

1. 首次发布后发现 `test` 运行时沿用了失效的 `D:\code\AI\J-Agents`，导致 `/api/training/role-creation/sessions` 返回 `agent_search_root_not_set`。
2. 用 `-AgentSearchRoot C:\work\J-Agents` 重新发布 `test`，修正环境漂移。
3. 回归时发现 `start role creation` 仍失败，错误为 `role_creation_memory_script_missing`。
4. 定位到 `src/workflow_app/server/services/role_creation_service_parts/workspace_and_projection.py` 把 `cfg.root` 误当成源码根；在 Web 运行时它实际是 `runtime_root`。
5. 修复后重新发布并重启 `test`，再做真实创建角色链路验证。

## 修复点

- `src/workflow_app/server/services/role_creation_service_parts/workspace_and_projection.py`
  - 新增 `_role_creation_asset_root(cfg)`，优先从 `WORKFLOW_RUNTIME_DEPLOY_ROOT` / `WORKFLOW_RUNTIME_SOURCE_ROOT` 解析模板资产根。
  - 角色工作区初始化改为从部署副本读取 `.codex/MEMORY.md` 与 `scripts/manage_codex_memory.py`。
  - `workspace_init_ref` 证据仍落到 `runtime_root/logs/runs/`，避免混用运行态与模板资产路径。

## 发布后验证

- `healthz`: `ok=true`
- 角色创建会话：`rcs-20260323-144556-651094`
- 对话来源：
  - `dialogue_agent_name = Analyst`
  - `dialogue_agent_workspace = C:/work/J-Agents/Analyst`
  - `dialogue_provider = codex`
  - `trace_ref = logs/runs/role-creation-analyst-rcs-20260323-144556-651094-20260323-144556-54aaf4`
- `开始创建`：
  - `session.status = creating`
  - `assignment_ticket_id = asg-20260323-144632-e016a4`
  - `workspace_init_status = completed`
  - `workspace_init_ref = logs/runs/role-creation-workspace-init-20260323-144630-9d92d2.md`
  - `scheduler_state = running`
- 显式委派：
  - `task_refs` 从 `4 -> 5`
  - 当前回合成功新增真实任务中心任务

## 备注

- 通过当前终端环境直接后台起守护进程不稳定，最终用 `cmd /c start "" powershell ... start_workflow_env.ps1 -Environment test` 拉起 `test` 常驻实例。

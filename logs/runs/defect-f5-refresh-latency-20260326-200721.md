# 缺陷页 F5 刷新慢排查 20260326-200721

- topic: F5 首次刷新慢定位与修复
- started_at: 2026-03-26T19:49:00+08:00
- finished_at: 2026-03-26T20:07:21+08:00
- workspace: `C:\work\J-Agents\workflow`

## 结论
- 静态资源不是主因：`/`、`/static/workflow-web.css`、`/static/workflow-web-client.js` 在线上 `8090` 分别约 `119.7ms / 88.1ms / 125.4ms`。
- 首屏慢的主因是启动阶段串行等待 `/api/agents`，而线上旧实现该接口首轮约 `7.5s ~ 8.1s`。
- `/api/agents` 慢的主因是 agent 发现使用 `agents_root.rglob("AGENTS.md")` 全递归扫描，`agent_search_root=C:\work\J-Agents` 时会把 `workflow/.running`、`.test`、`.tmp` 等隐藏运行目录也遍历进去；这些目录最终虽会被过滤，但遍历成本已产生。

## 证据
- 线上旧实现测量：
  - `/api/agents` 首次 `8155.7ms`
  - `/api/chat/sessions` `120.7ms`
  - `/api/dashboard` `225.0ms`
  - `/api/runtime-upgrade/status` `52.1ms`
- 扫描代价对比（同一根目录 `C:\work\J-Agents`）：
  - `Path.rglob("AGENTS.md")` 约 `4332.6ms`，命中 `162` 个 `AGENTS.md`
  - 剪枝隐藏目录后的 `os.walk` 约 `123.5ms`，命中 `10` 个可见 `AGENTS.md`
- 修复后临时实例 `8098` 测量：
  - `/api/agents` 第 1 次 `106.4ms`
  - `/api/agents` 第 2 次 `24.9ms`
  - `/api/agents` 第 3 次 `56.1ms`

## 修复
- 文件：`src/workflow_app/server/services/agent_discovery_service.py`
- 动作：新增 `_iter_agent_manifest_paths()`，把 agent 发现从 `rglob` 改为 `os.walk(topdown=True)`。
- 规则：遍历阶段直接剪掉以 `.` 开头的目录，避免深入 `.running`、`.test`、`.tmp`、`.git` 等隐藏运行树；返回结果仍保持按路径排序，业务过滤口径不变。

## 验证
- `python -m py_compile src/workflow_app/server/services/agent_discovery_service.py`
- 临时实例测量日志：
  - `C:\work\J-Agents\workflow\.test\runtime\f5-refresh-probe.stdout.log`
  - `C:\work\J-Agents\workflow\.test\runtime\f5-refresh-probe.stderr.log`
- 新候选已推送到 `test`：
  - `C:\work\J-Agents\workflow\.running\control\logs\test\deploy-20260326-200621.json`
  - `C:\work\J-Agents\workflow\.running\control\reports\test-gate-20260326-200621.json`

## 当前状态
- `test` 候选版本：`20260326-200621`
- `prod` 未升级，仍需用户手动放行

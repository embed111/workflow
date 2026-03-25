# Role Creation Browser Acceptance Codex Isolation

- generated_at: `2026-03-25T10:44:07+08:00`
- scope: `创建角色浏览器验收 + 当前会话不中断收口`
- result: `passed`
- runtime_root: `C:/work/J-Agents/workflow/.test/runtime/role-creation-browser-acceptance`
- base_url: `http://127.0.0.1:8193`
- acceptance_summary: `C:/work/J-Agents/workflow/.test/evidence/role-creation-browser-acceptance/summary.md`
- acceptance_summary_json: `C:/work/J-Agents/workflow/.test/evidence/role-creation-browser-acceptance/summary.json`

## Key Fixes

- 为 `role_creation` analyst bridge 增加 `WORKFLOW_ROLE_CREATION_CODEX_BIN` 覆盖入口，验收显式指向本地 stub。
- 为 `run_acceptance_role_creation_browser.py` 注入本地 `codex.cmd` stub，并通过 `/api/assignments/settings/execution` 显式把 assignment 执行链路也切到 stub。
- 将阻塞式前台验收改为后台执行 + 轮询排查，避免当前和用户的会话在长时间验收时直接中断。
- 修复 high-load 验收编排：减少额外任务数量到 probe 所需最小集合，并放宽 HTTP 超时。
- 修复 `capture_probe()` 重试逻辑参数缺失。
- 修复 assignment 产物 JSON 写入在 Windows 下的并发竞争：改为唯一临时文件名 + `replace` 重试。

## Evidence

- 验收总结果：`.test/evidence/role-creation-browser-acceptance/summary.json` 中 `ok=true`
- 关键截图：
  - `C:/work/J-Agents/workflow/.test/evidence/role-creation-browser-acceptance/screenshots/rc_profile_tab.png`
  - `C:/work/J-Agents/workflow/.test/evidence/role-creation-browser-acceptance/screenshots/rc_archive_entry.png`
  - `C:/work/J-Agents/workflow/.test/evidence/role-creation-browser-acceptance/screenshots/rc_high_load.png`
- 探针结果：
  - `C:/work/J-Agents/workflow/.test/evidence/role-creation-browser-acceptance/screenshots/rc_profile_tab.probe.json`
  - `C:/work/J-Agents/workflow/.test/evidence/role-creation-browser-acceptance/screenshots/rc_high_load.probe.json`
- stub 隔离证据：
  - `C:/work/J-Agents/workflow/.test/evidence/role-creation-browser-acceptance/summary.json`
  - `C:/work/J-Agents/workflow/.test/runtime/role-creation-browser-acceptance/logs/runs`

## Decision

- 当前用户所说的“验收时会直接中断当前会话”已通过后台执行方式规避，同时验收链路内的真实 Codex 调用已被 stub 隔离。
- 本轮完成开发态真实浏览器验收，后续如需环境发布，按既定边界仅考虑 `test`，`prod` 仍保持用户手动升级。

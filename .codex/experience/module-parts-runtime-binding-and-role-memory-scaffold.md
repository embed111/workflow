# module parts runtime binding and role memory scaffold

## 适用范围
- `workflow_app.server.services.*` 这类通过 `exec_local_parts()` 组装的服务模块
- 角色工作区初始化、记忆库脚手架、离线 acceptance probe
- 想直接调用 `_initialize_*` 之类私有 helper 的场景

## 现象
- 离线验收里直接 `import role_creation_service as rc`，再调用 `rc._initialize_role_workspace(...)`，会在 `path_in_scope(...)`、`now_local()` 之类位置炸成 `NoneType is not callable`
- 现场看起来像“角色记忆脚手架坏了”，其实是服务模块运行时符号没有绑定

## 根因
- 这类拆片服务模块会先把 `path_in_scope`、`now_local`、`relative_to_root`、`safe_token` 等符号声明成占位
- 正常 Web runtime 启动时，会通过 `bind_runtime_symbols(...)` 把真实实现灌进去
- 如果 probe 绕过 runtime，直接裸调内部 helper，这些符号还是 `None`

## 处理规则
- 优先验证公开入口，不优先验证私有 helper
- 如果必须直调拆片服务里的私有 helper，先显式执行一次 `service_module.bind_runtime_symbols(runtime_module.__dict__)`
- 与角色记忆链相关的离线 runtime 至少要准备：
  - `scripts/manage_codex_memory.py`
  - `.codex/MEMORY.md` 或内建 fallback
  - `.codex/experience/index.md`
  - `.codex/memory/全局总览 + 月度总览 + 当日日记`

## 这次固化下来的做法
- 角色创建脚手架内建 fallback `MEMORY.md`
- 角色创建脚手架默认生成 `AGENTS.md -> Memory Governance`
- 角色创建脚手架默认补 `.codex/experience/index.md`
- 运行时 assignment memory bootstrap 也补经验索引和记忆骨架，避免老工作区因占位文件再次起不来
- 旧角色工作区统一用 `scripts/repair_role_workspace_memory.py` 做一次性修复

## 避坑提醒
- 不要把“helper 直调失败”误判成“生产逻辑失败”
- 验收里如果断言的是公开契约，优先走 API 或 runtime 绑定后的模块入口
- 若角色工作区里只剩 `# Memory Spec` 这类占位，说明不是正常记忆链，必须补 `repair-rollups`

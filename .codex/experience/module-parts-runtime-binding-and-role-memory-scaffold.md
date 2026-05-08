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
- 如果拆片模块需要兼容 acceptance 里的 monkeypatch，不要把 runtime 符号只拷贝成一次性的静态快照；更稳的默认是保留对上游符号表的 live 引用，否则像 `resolve_artifact_root_path`、`_assignment_runtime_status` 这类被 probe 临时替换的函数不会透传到新模块里
- 做 `schedule_*_runtime.py` 这类 runtime helper 抽离时，也不要在新模块里继续直接抓 `schedule_status_runtime` 的静态 alias；更稳的默认是优先经由 `_runtime_symbol(...)` 再回退到本地实现，否则像 `verify_schedule_live_result_summary.py` 这类依赖 monkeypatch 的回归会先在新模块里失效
- 与角色记忆链相关的离线 runtime 至少要准备：
  - `scripts/manage_codex_memory.py`
  - `.codex/MEMORY.md` 或内建 fallback
  - `.codex/experience/index.md`
  - `.codex/memory/全局总览 + 月度总览 + 当日日记`
- 做 `V5-R3` 这类角色专业能力前置合同时，不要去 developer workspace（`.repository/<developer_id>`）里找 `state/role-assets/`；更稳的默认是直接从 assigned agent 的运行态工作区读取 `state/role-assets/METHODS_INDEX.md + methods/*`，再把角色专属检查单和评分 rubric 注入 execution prompt。离线 probe 也应自建临时 agent workspace + role-assets，而不是假定 developer workspace 壳里天然就有这些文件。
- 做 `V5-R3` 这类角色质量评分回写时，也不要直接改 assignment 顶层 JSON 交付 contract；更稳的默认是继续保持既有五字段 JSON，把 `## 角色质量评分回写` 小节追加到 `artifact_markdown`，再由服务端解析回 `result.json / status-detail`。这样可以在不打破既有交付壳的前提下，把 rubric 结果稳定投影进运行真相。

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
- 像 `dashboard.py` 这类只读 API 或离线 acceptance，如果只是想读 `audit.jsonl / nodes/*.json` 做信号投影，不要直接 import `assignment_service_parts.task_artifact_store_core` 这类依赖 runtime 绑定的拆片模块；更稳的默认是直接读文件，或经由已经完成绑定的 `ws` 入口读取

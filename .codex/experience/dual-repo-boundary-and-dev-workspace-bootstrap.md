# 双仓边界与开发工作区 bootstrap 经验

## 适用范围
- `workflow / workflow_code` 双仓边界固定
- 开发工作区 bootstrap / refresh
- 普通执行链路的受保护根收口

## 稳定经验
- 双仓第一批不要把 `code_root` 就绪状态并到现有 `agent_search_root_ready` 总门禁里，否则会把当前 `8090` 既有会话/创建角色链路一起锁死。应单独暴露 `code_root_ready/code_root_error`，只对开发工作区 bootstrap 与代码仓相关动作 fail-closed。
- 路径契约应统一从 `workspace_root` 派生，固定：
  - `pm_root = <workspace_root>/workflow`
  - `code_root = <workspace_root>/workflow_code`
  - `development_workspace_root = <pm_root>/.repository`
- `../workflow_code` 只承载正式代码，不承载 `.codex`、`AGENTS.md`、运行态目录或审计留痕；这些内容继续留在 PM/控制工作区或运行态层。
- 一旦 `workflow_code` 与 `.repository/<developer_id>` 链路已经打通，PM 仓中原先残留的 `src/`、`scripts/`、`run_workflow.bat` 应立即删除，并在 PM 仓 `.gitignore` 中显式忽略；否则同一套实现会长期出现双副本漂移。
- 受保护根至少包含 `pm_root` 与 `code_root`。普通 chat/task 执行链路即便仍以 `agent_search_root` 作为大范围发现根，也要把这两个路径视为只读并显式拒绝写入。
- `../workflow_code` 如果缺失、不是目录、不是 Git 仓，必须直接 fail-closed，并返回明确错误码；不要偷偷回退到 `workflow` 当前仓继续承担正式代码仓职责。
- 若 `../workflow_code` 曾经误用 `workflow` 整仓历史初始化，后续即使已收成 code-only 文件树，Git 历史仍会混入 PM/运行态脏语义；这时应在确认文件树正确后直接重建 `workflow_code/.git`，让代码根仓从干净 root commit 重新开始。
- Windows 下把非 bare 本地仓当 remote 时，默认不要推当前被检出的基线分支；改为每个开发主体使用独立开发分支，例如 `dev/<developer_id>`，再向该分支推送。
- 开发工作区 refresh 前先检查工作区是否干净；存在未提交改动时，宁可阻塞，也不要自动 `checkout/reset` 覆盖。

## 已踩过的坑
- 坑 1：runtime-config 还指向旧的 `C:/work/J-Agents`，会让系统先报 `workspace_root_missing_workflow_subdir`，掩盖真正的 `workflow_code` 缺失问题。
  - 避免方式：先把 runtime-config 校到当前实际 workspace root，再看 `code_root` 的独立就绪状态。
- 坑 2：如果没有显式记录 `development_workspace_root`，开发工作区容易重新散回主仓附近，或者又混回任务产物根，和运行态目录混在一起。
  - 避免方式：把 `development_workspace_root` 固定到 `pm_root/.repository` 并加入 PM 仓 `.gitignore`；运行态仍单独留在 `artifact_root` 派生目录。
- 坑 3：本地开发分支没有 remote 时，refresh 若强制重建分支会吞掉已有本地提交。
  - 避免方式：本地分支已存在时只允许 `ff-only` 合基线；一旦发生分歧直接阻塞并提示手工处理或先推远端。
- 坑 4：如果 `workflow` 与 `workflow_code` 同时保留一份 `src/` / `scripts/`，之后有人在 PM 仓顺手改代码，很容易造成“代码根仓没变、治理仓偷偷漂移”的假状态。
  - 避免方式：code-only 根仓就位后，直接删掉 PM 仓重复代码副本，并把这些路径列入 PM 仓忽略名单。

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
- 一旦 `workflow_code` 与 `.repository/<developer_id>` 链路已经打通，PM 仓中原先残留的 `src/`、`scripts/` 应立即删除，并在 PM 仓 `.gitignore` 中显式忽略；否则同一套实现会长期出现双副本漂移。
- PM 仓顶层允许保留一个极薄的 `run_workflow.bat` 便捷入口，但它只能代理到默认开发工作区/PM 顶层部署副本，不能重新承载源码或和代码仓形成第二份实现。
- 开发工作区触发部署时，`dev/test/prod` 的 `.running/.runtime/.output` 真相源应统一回到 PM 顶层，而不是在 `.repository/<developer_id>` 下再长出一套平行运行态。
- 当开发工作区刚改成“部署回 PM 顶层”后，`test/prod` 可能还残留旧环境的 runtime-config；首次重发时要显式带上当前真实 `-AgentSearchRoot/-ArtifactRoot`，把旧盘符和旧产物根冲掉，再恢复到默认命令口径。
- 受保护根至少包含 `pm_root` 与 `code_root`。普通 chat/task 执行链路即便仍以 `agent_search_root` 作为大范围发现根，也要把这两个路径视为只读并显式拒绝写入。
- `../workflow_code` 如果缺失、不是目录、不是 Git 仓，必须直接 fail-closed，并返回明确错误码；不要偷偷回退到 `workflow` 当前仓继续承担正式代码仓职责。
- 若 `../workflow_code` 曾经误用 `workflow` 整仓历史初始化，后续即使已收成 code-only 文件树，Git 历史仍会混入 PM/运行态脏语义；这时应在确认文件树正确后直接重建 `workflow_code/.git`，让代码根仓从干净 root commit 重新开始。
- Windows 下把非 bare 本地仓当 remote 时，默认不要推当前被检出的基线分支；改为每个开发主体使用独立开发分支，例如 `dev/<developer_id>`，再向该分支推送。
- 开发工作区 refresh 前先检查工作区是否干净；存在未提交改动时，宁可阻塞，也不要自动 `checkout/reset` 覆盖。
- 跑完会修改开发工作区 Git 元数据的 gate/bootstrap 脚本后，要立刻复核 `.repository/<developer_id>` 的 `remote.origin.url`；如果它被临时指到 gate fixture 或隔离 runtime 下的假 `workflow_code`，后续 `push` 会悄悄送错仓。
- 如果线上止损时不得不直接改 `.running/prod`，后续第一优先级不是继续叠加热修，而是立即把差异回放到 `.repository/<developer_id>`，再推回 `../workflow_code`；否则多人协作会退化成串行补丁接力。
- `manage_developer_workspace.py` 这类 bootstrap/状态脚本如果从 runtime root 反推 `workspace_root`，要显式传入真实工作区根；否则它会把 `.running/control/runtime` 误判成协作根，派生出错误的 `pm_root/code_root/.repository` 边界。
- `workflow_bugmate` 这类 bugfix mirror 如果长期复用，mirror 内很容易夹带旧缺陷残留改动；导出 patch 前必须先看当前 diff。若当前任务只改一两个文件，优先按目标文件生成 scoped patch，不要直接交付 mirror 对 source 的全量差异。

## 已踩过的坑
- 坑 1：runtime-config 还指向旧的 `C:/work/J-Agents`，会让系统先报 `workspace_root_missing_workflow_subdir`，掩盖真正的 `workflow_code` 缺失问题。
  - 避免方式：先把 runtime-config 校到当前实际 workspace root，再看 `code_root` 的独立就绪状态。
- 坑 2：如果没有显式记录 `development_workspace_root`，开发工作区容易重新散回主仓附近，或者又混回任务产物根，和运行态目录混在一起。
  - 避免方式：把 `development_workspace_root` 固定到 `pm_root/.repository` 并加入 PM 仓 `.gitignore`；运行态仍单独留在 `artifact_root` 派生目录。
- 坑 3：本地开发分支没有 remote 时，refresh 若强制重建分支会吞掉已有本地提交。
  - 避免方式：本地分支已存在时只允许 `ff-only` 合基线；一旦发生分歧直接阻塞并提示手工处理或先推远端。
- 坑 4：如果 `workflow` 与 `workflow_code` 同时保留一份 `src/` / `scripts/`，之后有人在 PM 仓顺手改代码，很容易造成“代码根仓没变、治理仓偷偷漂移”的假状态。
  - 避免方式：code-only 根仓就位后，直接删掉 PM 仓重复代码副本，并把这些路径列入 PM 仓忽略名单。
- 坑 5：如果把 PM 顶层 `run_workflow.bat` 做成第二份真实启动实现，而不是便捷代理，后续又会把 PM 壳仓误判成代码仓。
  - 避免方式：顶层 `run_workflow.bat` 只能代理，不允许自带 `src/`、`scripts/` 或复制代码实现。
- 坑 6：如果开发工作区脚本部署时把 `.running` 派生到 `.repository/<developer_id>` 下面，用户从 PM 顶层启动时看到的就不是同一套 `prod/test/dev`。
  - 避免方式：部署/启动脚本在识别到 `.repository/<developer_id>` 源根时，统一把运行根、控制根和默认产物根派生回 PM 顶层。
- 坑 7：运行根已经切回 PM 顶层，但 `test` 或 `prod` 的 runtime-config 还保留旧盘符时，release gate 会在旧路径上建目录并直接超时失败。
  - 避免方式：第一次切换后重发 `test/prod` 时，显式传入当前真实 `-AgentSearchRoot/-ArtifactRoot`，并确认 `.running/control/runtime/<env>/state/runtime-config.json` 已更新到当前工作区路径。
- 坑 8：`workflow_bugmate/scripts/export_bugfix_patch.ps1` 默认会把 mirror 相对 source 的全部差异一起导出；如果 mirror 里还躺着历史任务残留，当前 bug 的 patch 会被无关改动污染。
  - 避免方式：导出前先审 mirror diff；若发现非本轮文件，先 refresh mirror 或改用 `git diff --no-index` 对本轮目标文件单独切 scoped patch。
- 坑 9：把 PM 仓里的 `src/`、`scripts/` 当成“暂时还能用的代码副本”继续改，短期看似方便，长期会把代码根仓、运行副本和本地工作区三套真相源重新搅在一起。
  - 避免方式：只要 `../workflow_code` 和 `.repository/<developer_id>` 已就绪，就立即清掉 PM 仓里的 `src/`、`scripts/` 误放副本，并把后续代码修改全部收口到本地开发工作区。
- 坑 10：`workflow gate` 或隔离 bootstrap 现场可能把开发工作区的 `origin` 临时改写成 `.test/runtime/.../workflow_code` 这类 fixture 仓；如果跑完 gate 后直接 `git push origin ...`，提交会被送到错误的临时根仓，而且表面上还会显示成功。
  - 避免方式：凡是跑过会构造隔离代码根仓的 gate/bootstrap 后，正式推根仓前先执行 `git -C .repository/<developer_id> remote -v` 复核；若 remote 漂了，先显式 `git remote set-url origin <真实 workflow_code 路径>` 再 push。

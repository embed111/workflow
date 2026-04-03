# Repository Guidelines

## 运行开关（顶部手动切换）
1. `DIALOGUE_RETRO_SWITCH: ON`
   - `ON`: 每轮对话结束后允许自动执行“复盘增量记录”（偏好变化、需求假设、验证动作）。
   - `OFF`: 禁止自动更新复盘相关文件；仅在用户明确指令时更新：
     - `state/session-snapshot.md`
     - `state/user-preferences.md`
     - `logs/runs/*.md`

## 启动读取顺序
1. 顶层治理入口固定先读 `AGENTS.md`。
2. 每轮正式工作前先读 `.codex/experience/index.md`，并按其中“必读经验”顺序补充读取必读经验文件。
3. 默认会话按以下顺序继续读取：
   - `.codex/SOUL.md`
   - `.codex/USER.md`
   - `.codex/MEMORY.md`
   - `.codex/memory/全局记忆总览.md`
   - `.codex/memory/YYYY-MM/记忆总览.md`
   - `.codex/memory/YYYY-MM/YYYY-MM-DD.md`
4. 当日日记缺失时，先在对应 `YYYY-MM/` 目录创建当日日记，再进入正式工作。
5. 工作日切后的首轮工作，先检查“昨日记忆”是否已归档到对应 `.codex/memory/YYYY-MM/记忆总览.md`。
6. 工作月切后的首轮工作，先检查“上月记忆总览”是否已归档到 `.codex/memory/全局记忆总览.md`。

## 三层职责边界
- `.codex/`：agent 工作记忆、内部工作文档、本地技能入口（如 `.codex/skills/*/SKILL.md`）。
- `state/`：产品运行态、运行数据库、会话快照与复盘态。
- `logs/`：运行与审计留痕、执行记录、证据归档。
- 禁止把 `.codex/MEMORY.md`、`.codex/memory/**/*.md` 当成产品运行态、配置文件或审计日志使用。

## Project Structure & Module Organization
- `../workflow_code/`：唯一正式代码根仓（code-only），承载 `src/`、`scripts/` 与正式 Git 历史，不再承载便捷启动 wrapper。
- `.repository/<developer_id>/`：本地临时代码开发工作区；实际代码修改、验证、提交都在这里进行，并推送回 `../workflow_code`。
- `run_workflow.bat`：当前 PM 仓顶层便捷启动入口，只负责把用户带到当前默认开发工作区/当前 `prod` 部署副本，不属于正式代码真相源。
- `.codex/`：agent 工作记忆、内部工作文档、本地技能入口（如 `.codex/skills/*/SKILL.md`）。
- `docs/workflow/`：需求、门禁和证据矩阵文档，先读这里再改流程。
- `logs/`：运行与审计留痕。重点子目录：`events/`（JSONL 事件流）、`runs/`（执行记录）、`decisions/`（决策日志）、`summaries/`（汇总）。
- `state/`：运行态数据（如 `state/workflow.db`、`session-snapshot.md`、`change-log.md`）。
- `.running/` 与 `.runtime/`：运行态、副本与部署控制数据。
- `metrics/` 与 `incidents/`：性能基线和故障记录。
- `src/`、`scripts/` 不再属于当前 PM 仓；若这些路径在 `workflow` 中重新出现，应视为误放的代码副本而不是合法治理文件。

## Current Collaboration Workflow
- 当前 `workflow` 项目仍处于单人维护阶段，默认由当前 Codex 同时承担开发、测试、发布候选生成与部署协助；后续新增协作者时，再为其分配各自独立的 `.repository/<developer_id>/` 工作区。
- 当前默认开发主体固定为 `pm-main`；若无额外说明，代码同步、修改、验证、提交与推送都在 `.repository/pm-main/` 中完成。
- 每次进入代码工作前，先将 `../workflow_code` 的最新代码同步到对应开发工作区；若该工作区存在未提交改动，必须先保护现场，不得直接覆盖。
- 用户提到 `./run_workflow.bat` 时，默认指当前 PM 仓顶层的便捷入口；该入口默认代理到 `.repository/pm-main` 的启动脚本，并复用 PM 顶层统一的 `.running/dev|test|prod` 运行态。
- 当前默认协作顺序固定为：
  1. 同步 `../workflow_code` 最新代码；
  2. 在 `.repository/<developer_id>/` 中开发、验证并跑门禁；
  3. 将通过验证的代码推回 `../workflow_code`；
  4. 生成或刷新 `prod` 升级候选；
  5. 仅当用户明确要求“更新生产环境代码”或“部署生产环境”时，才执行正式环境升级或等效生产代码更新。

## Build, Test, and Development Commands
- `.\run_workflow.bat`：从当前 PM 仓顶层启动默认 `prod` 入口；内部代理到 `.repository/pm-main` 的启动脚本，并落到 PM 顶层 `.running/prod`。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .repository/<developer_id>/scripts/launch_workflow.ps1 -OpenBrowser`：从本地开发工作区启动当前代码版本。
- `python .repository/<developer_id>/scripts/workflow_web_server.py --host 127.0.0.1 --port 8090`：仅启动开发工作区中的 Web 服务。
- `python .repository/<developer_id>/scripts/workflow_entry_cli.py --mode status`：刷新并查看待分析/待训练状态。
- `python .repository/<developer_id>/scripts/workflow_entry_cli.py --mode backfill`：将 `logs/events/*.jsonl` 回填到 SQLite。
- `python .repository/<developer_id>/scripts/acceptance/run_acceptance_workflow_gate.py --root .repository/<developer_id> --host 127.0.0.1 --port 8098`：执行开发工作区门禁验收。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .repository/<developer_id>/scripts/deploy_workflow_env.ps1 -Environment test`：将已验证版本部署到 `test` 并生成或刷新 `prod` 候选。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .repository/<developer_id>/scripts/deploy_workflow_env.ps1 -Environment prod -AllowDirectProdDeploy`：仅在用户明确要求更新生产环境时使用。
- `git -C .repository/<developer_id> status --short --branch`：检查当前开发分支与工作区状态。

## Coding Style & Naming Conventions
- 以下代码规范适用于 `../workflow_code/` 与 `.repository/<developer_id>/` 中的代码，不再针对当前 PM 仓根目录落代码。
- Python 使用 4 空格缩进，优先类型标注与 `pathlib.Path`，函数名使用 `snake_case`。
- JavaScript 保持 ES 语法与 `camelCase` 变量命名；常量使用 `UPPER_SNAKE_CASE`。
- 新增脚本命名遵循 `scripts/<action>_<target>.py`，日志文件遵循 `logs/runs/<topic>-YYYYMMDD-HHMMSS.md`。

## Testing Guidelines
- 当前主测试入口是开发工作区中的门禁脚本（非 pytest 套件）。改动 API/流程时，优先补充 `run_acceptance_workflow_gate.py` 对应 case。
- 验收结果需落盘到 `logs/runs/`，并在必要时更新 `docs/workflow/验收证据矩阵-Phase0.md`。
- 最低回归建议：`healthz` 可用、会话创建成功、任务可中断并可重试、训练链路事件可查询。

## Default Release Rule
- 默认发布约束文件：`docs/workflow/governance/默认发布约束.md`。
- 只要存在实际代码改动，且已完成验证并跑完门禁通过，默认继续执行：
  - 先同步 `../workflow_code` 最新代码到对应开发工作区
  - 部署 `test`
  - 生成/刷新 `prod` 升级候选
  - 由用户手动升级 `prod`
- 本仓库中“推送到生产环境”默认解释为“生成/刷新 `prod` candidate”，不是自动升级正式环境。
- 未经用户明确要求，不得直接执行 `prod` 覆盖式部署或自动 apply 正式升级。
- 代码改动默认先在对应开发工作区根执行 `python scripts/quality/check_workspace_line_budget.py --root .`；若本轮触达文件命中行数重构门槛，优先做职责拆分/设计模式重构，再发布。

## Architecture & Workflow Notes
- 当前 PM 仓只保留治理、留痕与本地开发工作区壳；实际实现位于 `../workflow_code/` 或 `.repository/<developer_id>/`。
- 当前 PM 仓顶层 `run_workflow.bat` 只是便捷代理，不承载正式代码；真正实现仍来自 `.repository/<developer_id>/scripts/*` 与部署到 PM 顶层 `.running/*` 的副本。
- 典型链路仍是 `workflow_web_server.py` 接收请求 -> `task_agent_runner.py` 执行任务 -> 事件与消息写入 `state/workflow.db` 与 `logs/events/*.jsonl`，但相关实现文件位于代码根仓或开发工作区，不再位于当前 PM 仓根目录。
- 前端资源由后端直接托管，核心交互脚本位于 `../workflow_code/src/workflow_app/web_client/*.js` 或对应开发工作区副本，修改 UI 时需同步检查 API 字段兼容性。
- 训练相关状态通过队列与事件表回放，调试时优先对照 `logs/runs/` 报告与 `state/change-log.md`。

## Commit & Pull Request Guidelines
- 代码提交统一在 `.repository/<developer_id>` 对应 Git 分支完成；当前 PM 仓提交应以治理、文档、留痕与边界收口为主。
- 代码仓提交建议统一采用 Conventional Commits：`feat:`, `fix:`, `docs:`, `chore:`。
- 提交信息建议包含作用域，如：`fix(workflow): block $root traversal on write targets`。
- PR 至少包含：变更目的、影响范围、验证命令、关键日志路径；涉及 UI 时附页面截图。
- 单个 PR 建议聚焦单一主题（例如仅修复路径安全或仅调整训练队列 UI），避免把流程改造与文档重写混在一次提交中。

## Security & Configuration Tips
- 真实模型调用依赖环境变量：`WORKFLOW_AGENT_BASE_URL`、`WORKFLOW_AGENT_API_KEY`、`WORKFLOW_AGENT_MODEL`。
- 严禁提交密钥或包含敏感信息的 trace；提交前检查 `logs/` 与 `state/` 新增文件。
- 所有写入路径必须限制在 `agent_search_root` 内，保持 `$root` 越界拦截行为不回退。

## PM Continuous Maintenance
- 仅当 `DIALOGUE_RETRO_SWITCH: ON` 时，才自动写入每轮复盘增量；`OFF` 时只读不写，除非用户明确要求更新。
- `.codex/experience/` 用于沉淀可复用经验与踩坑规避；每轮开始先读 `index.md` 与其中 `required_reads` 标记的经验文件，每轮结束若出现可复用经验或新坑位，更新索引并补充经验卡。
- 用户偏好与需求假设统一维护在 `state/user-preferences.md`（单一事实源）。
- 每次更新执行快照（如 `state/session-snapshot.md`、`logs/runs/*.md`）时，不重复粘贴全文，只追加引用：`preference_ref: state/user-preferences.md` 与本次增量观察。
- `User Preferences` 只记录可观察偏好，例如：响应风格、交付粒度、容错策略、优先级倾向；避免记录无关隐私。
- `Need Hypotheses` 使用固定格式：`Observation -> Inference -> Validation Action -> Confidence(High/Med/Low)`。
- 需求揣测采用“行为心理线索 + JTBD”方法：从措辞、催促频率、验收关注点推断深层目标，再通过下一轮需求确认闭环。
- 禁止把推测当事实；任何心理层推断都要在后续对话中显式求证并允许用户否定。
- `.codex/MEMORY.md` 只维护记忆规范；禁止把具体轮次总结直接写进该文件。
- `.codex/memory/全局记忆总览.md` 只归档已闭月的月度总结；当前活动月份只保留索引，不复制当月当日增量。
- `.codex/memory/YYYY-MM/记忆总览.md` 只归档截至昨日的日级摘要；今日总结仅写入当日日记，待日切后再汇总。
- 每轮工作结束后，都要向 `.codex/memory/YYYY-MM/YYYY-MM-DD.md` 追加一条带时间戳的本轮总结。
- 若发生日切但月未切，先补齐“昨日 -> 月度总览”的归档检查，再继续工作。
- 若发生月切，先补齐“昨日 -> 对应月度总览”与“上月总览 -> 全局总览”的归档检查，再继续工作。

### Snapshot Addendum Template
```md
- preference_ref: state/user-preferences.md
- delta_observation: <本次新增观察>
- delta_validation: <下一轮验证动作>
```



4. 在正式发布成功后同步绑定角色详情来源。

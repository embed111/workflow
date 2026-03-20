# 执行提示词：workflow 工作区 OpenClaw 试点改造

## 当前工作区路径
1. 工作区根目录：`D:\code\AI\J-Agents\workflow`
2. 需求文档目录：`D:\code\AI\J-Agents\workflow\docs\openclaw\workspace-openclaw-governance`
3. 本轮所有新增、修改、验证都只能发生在上述 `workflow` 工作区根目录内。

请按照以下文件执行当前 `workflow` 工作区整改，不要扩散到其他目录：

1. `D:\code\AI\J-Agents\workflow\docs\openclaw\workspace-openclaw-governance\需求概述.md`
2. `D:\code\AI\J-Agents\workflow\docs\openclaw\workspace-openclaw-governance\需求详情-workflow工作区OpenClaw试点改造.md`

## 本轮目标
1. 为当前工作区新增 `.codex/` 能力层。
2. 补齐 OpenClaw 风格记忆层：
   - `.codex/SOUL.md`
   - `.codex/USER.md`
   - `.codex/MEMORY.md`
   - `.codex/TOOLS.md`
   - `.codex/HEARTBEAT.md`
   - `.codex/memory/`
   - `.codex/skills/`
3. 更新 `AGENTS.md`，补齐 OpenClaw 风格读取顺序。
4. 明确 `.codex/*`、`state/*`、`logs/*` 的职责边界。
5. 保证现有 `workflow` 运行链路不受损。

## 必做事项
1. 在当前工作区创建缺失的 `.codex/` 目录与核心文档。
2. 更新 `AGENTS.md`，加入：
   - `.codex/SOUL.md`
   - `.codex/USER.md`
   - 近两天 `.codex/memory/YYYY-MM-DD.md`
   - 主会话额外读取 `.codex/MEMORY.md`
3. 校验当前代码与文档里所有 `.codex/skills/` 的正式入口口径与真实目录一致。
4. 做最小运行回归，证明本轮改造未破坏启动或关键链路。

## 禁止事项
1. 不要重构 `src/`、`scripts/`、`docs/workflow/` 的业务结构。
2. 不要把 `.codex/MEMORY.md` 当成产品运行态或配置文件。
3. 不要修改其他工作区。

## 交付物
1. 改造后的目录清单。
2. `AGENTS.md` 更新说明。
3. 启动读取验证证据。
4. 每日记忆写入验证证据。
5. 最小运行回归结果。

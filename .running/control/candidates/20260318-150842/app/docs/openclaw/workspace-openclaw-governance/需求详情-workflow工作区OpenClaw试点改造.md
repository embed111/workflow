# 需求详情：workflow 工作区 OpenClaw 试点改造

## 1. 主题目标与价值说明
为 `workflow` 增加 OpenClaw 风格 `.codex/` 能力层，补齐身份、用户、长期记忆、每日记忆和技能入口层，同时不破坏现有产品运行结构。

## 2. 用户画像与使用场景
1. 用户画像：`workflow` agent、owner、执行维护者。
2. 使用场景：
   - 主会话恢复长期记忆；
   - 非主会话仅恢复安全上下文；
   - 保持 `state/` 和 `logs/` 的产品运行态职责不变。

## 3. 用户旅程或关键流程
1. 新增 `.codex/` 和核心文档。
2. 更新 `AGENTS.md`，补齐读取顺序。
3. 校验 `.codex/skills/` 与现有文档/代码口径一致。
4. 做最小运行回归。

## 4. 功能需求清单
### FR-WFO-01 新增 `.codex/` 能力层
1. 新增：
   - `.codex/SOUL.md`
   - `.codex/USER.md`
   - `.codex/MEMORY.md`
   - `.codex/TOOLS.md`
   - `.codex/HEARTBEAT.md`
   - `.codex/memory/`
   - `.codex/skills/`

### FR-WFO-02 更新读取顺序
1. `AGENTS.md` 默认读取顺序至少应包含：
   - `.codex/SOUL.md`
   - `.codex/USER.md`
   - `.codex/memory/YYYY-MM-DD.md`（今天）
   - `.codex/memory/YYYY-MM-DD.md`（昨天）
2. 主会话额外读取 `.codex/MEMORY.md`。

### FR-WFO-03 三层职责边界
1. `.codex/*`：agent 工作记忆与内部文档。
2. `state/*`：产品运行态与复盘态。
3. `logs/*`：运行与审计留痕。

### FR-WFO-04 保持运行链路不回退
1. 不破坏 `run_workflow.bat`、`scripts/launch_workflow.ps1`、`src/`、`docs/workflow/`。

## 5. 非功能需求
1. 最小扰动。
2. 目录命名与总方案一致。
3. 兼容现有 `.codex/skills/` 口径。

## 6. 验收标准
1. Given 已完成改造
2. When 检查 `../workflow/.codex/`
3. Then 核心文档与 `memory/skills/` 已存在
4. And `AGENTS.md` 已具备 OpenClaw 风格读取顺序
5. And 最小运行回归通过

## 7. 边界条件与异常处理
1. 若当前无本地技能实现，`.codex/skills/` 仍应存在。
2. 若某运行链路误读 `.codex/MEMORY.md`，需在实现层显式隔离。

## 8. 依赖项与开放问题
1. 依赖执行方更新 `AGENTS.md` 并新增 `.codex/`。
2. 开放问题：`.codex/skills/` 是否需要最小说明文件；本轮不强制。

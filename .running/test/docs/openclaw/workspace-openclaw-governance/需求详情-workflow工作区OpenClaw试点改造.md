# 需求详情：workflow 工作区 OpenClaw 试点改造

## 1. 主题目标与价值说明
为 `workflow` 增加 OpenClaw 风格 `.codex/` 能力层，补齐身份、用户、记忆规范、全局记忆总览、月度记忆总览、每日记忆和技能入口层，同时不破坏现有产品运行结构。

## 2. 用户画像与使用场景
1. 用户画像：`workflow` agent、owner、执行维护者。
2. 使用场景：
   - 每轮工作前恢复记忆规范、全局总览、月度总览和当日日记；
   - 每轮工作后把本轮总结追加到当日日记；
   - 日切时把昨日摘要归档到月度总览；
   - 月切时把上月总览归档到全局总览；
   - 保持 `state/` 和 `logs/` 的产品运行态职责不变。

## 3. 用户旅程或关键流程
1. 新增 `.codex/` 和核心文档。
2. 将 memory 结构改为“规范文件 + 全局总览 + 月度总览 + 每日日记”。
3. 更新 `AGENTS.md`，补齐读取顺序与归档规则。
4. 校验 `.codex/skills/` 与现有文档/代码口径一致。
5. 做最小运行回归与 memory 校验。

## 4. 功能需求清单
### FR-WFO-01 新增 `.codex/` 能力层
1. 新增：
   - `.codex/SOUL.md`
   - `.codex/USER.md`
   - `.codex/MEMORY.md`
   - `.codex/TOOLS.md`
   - `.codex/HEARTBEAT.md`
   - `.codex/memory/全局记忆总览.md`
   - `.codex/memory/YYYY-MM/记忆总览.md`
   - `.codex/memory/YYYY-MM/YYYY-MM-DD.md`
   - `.codex/skills/`

### FR-WFO-02 更新读取顺序
1. `AGENTS.md` 默认读取顺序至少应包含：
   - `.codex/SOUL.md`
   - `.codex/USER.md`
   - `.codex/MEMORY.md`
   - `.codex/memory/全局记忆总览.md`
   - `.codex/memory/YYYY-MM/记忆总览.md`
   - `.codex/memory/YYYY-MM/YYYY-MM-DD.md`（今天）

### FR-WFO-03 记忆写入与归档
1. 每轮工作结束后，必须向当日日记追加一条带时间戳的轮次总结。
2. 日切后的首轮工作，必须先检查昨日摘要是否已归档到对应月份的 `记忆总览.md`。
3. 月切后的首轮工作，必须先检查上月 `记忆总览.md` 是否已归档到 `全局记忆总览.md`。
4. 当天总结不写入当月 `记忆总览.md`；待日切后再归档。

### FR-WFO-04 三层职责边界
1. `.codex/*`：agent 工作记忆与内部文档。
2. `state/*`：产品运行态与复盘态。
3. `logs/*`：运行与审计留痕。

### FR-WFO-05 保持运行链路不回退
1. 不破坏 `run_workflow.bat`、`scripts/launch_workflow.ps1`、`src/`、`docs/workflow/`。

## 5. 非功能需求
1. 最小扰动。
2. 目录命名与总方案一致。
3. 兼容现有 `.codex/skills/` 口径。
4. Memory 归档规则必须可校验，不能只靠口头约定。

## 6. 验收标准
1. Given 已完成改造
2. When 检查 `../workflow/.codex/`
3. Then 核心文档与 `memory/skills/` 已存在，且 `memory/` 采用“全局总览 + 月度总览 + 每日日记”结构
4. And `AGENTS.md` 已具备新的读取顺序与日切/月切归档规则
5. And 当日日记已支持带时间戳的轮次总结写入
6. And memory 校验与最小运行回归通过

## 7. 边界条件与异常处理
1. 若当前无本地技能实现，`.codex/skills/` 仍应存在。
2. 若某运行链路误读 `.codex/MEMORY.md`，需在实现层显式隔离。
3. 若当日日记尚未创建，应在开始工作前先创建对应 `YYYY-MM/YYYY-MM-DD.md`。

## 8. 依赖项与开放问题
1. 依赖执行方更新 `AGENTS.md` 并新增 `.codex/`。
2. 开放问题：`.codex/skills/` 是否需要最小说明文件；本轮不强制。

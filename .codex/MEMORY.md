# 工作区记忆规范

## 目的
- 本文件是当前工作区的顶层记忆规范。
- 具体轮次总结不要写在这里，只写入每日日记文件。
- 把 `.codex/` 视为 agent 记忆和内部指导，不得当成产品运行态。

## 必读顺序
1. `AGENTS.md`
2. `.codex/experience/index.md`
3. 读取 `.codex/experience/index.md` 中“必读经验”列出的经验文件
4. `.codex/SOUL.md`
5. `.codex/USER.md`
6. `.codex/MEMORY.md`
7. `.codex/memory/全局记忆总览.md`
8. `.codex/memory/YYYY-MM/记忆总览.md`
9. `.codex/memory/YYYY-MM/YYYY-MM-DD.md`

## 目录模型
- 经验索引：`.codex/experience/index.md`
- 经验卡：`.codex/experience/*.md`
- 全局总览：`.codex/memory/全局记忆总览.md`
- 月度总览：`.codex/memory/YYYY-MM/记忆总览.md`
- 每日日记：`.codex/memory/YYYY-MM/YYYY-MM-DD.md`

## 写入规则
- 经验卡只记录可复用模式、踩坑与规避规则；不要写成逐轮流水账。
- 出现新的稳定经验时，更新对应 `.codex/experience/*.md`，并同步维护 `index.md`。
- 每轮工作结束后，都要向当日日记追加一条带时间戳的总结。
- 每日日记条目优先使用结构化回忆格式：`主题`、`背景`、`动作`、`结论`、`验证`、`产物`、`下一步`。
- 当日总结只保留在当日日记中，直到次日开始。
- 当月总览只归档截至昨日的日级摘要。
- 全局总览只归档已闭月的月度总结。

## 每日条目字段说明
- `主题`：本轮主要在做什么。
- `背景`：本轮为什么发生，包括触发原因或发现的缺口。
- `动作`：本轮改了什么、创建了什么、迁移了什么、检查了什么。
- `结论`：会影响后续工作的规则或结论。
- `验证`：执行过的命令、检查项和观察结果。
- `产物`：本轮触达的关键文件或目录。
- `下一步`：后续待跟进工作、延后检查或归档条件。
- 条目保持简洁，但要完整到让后续读者不用重新打开大量无关文件也能复原本轮工作。

## 归档检查
- 日切检查：新一天首轮工作前，确认昨日日记已汇总到对应月度总览。
- 月切检查：新一月首轮工作前，确认上月总览已汇总到全局总览。
- 如果发现必须的总览条目缺失，先补归档，再继续正常工作。

## 验证命令
- `python scripts/manage_codex_memory.py status --root .`
- `python scripts/manage_codex_memory.py verify-rollups --root .`
- `python scripts/manage_codex_memory.py append --root . --summary "<round summary>"`
- `python scripts/manage_codex_memory.py append --root . --topic "<topic>" --context "<context>" --actions "<action1|action2>" --decisions "<decision1|decision2>" --validation "<check1|check2>"`

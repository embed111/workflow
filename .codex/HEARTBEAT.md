# 工作区心跳

## 启动读取顺序
1. `AGENTS.md`
2. `.codex/experience/index.md`
3. 读取 `.codex/experience/index.md` 中“必读经验”列出的经验文件
4. `.codex/SOUL.md`
5. `.codex/USER.md`
6. `.codex/MEMORY.md`
7. `.codex/memory/全局记忆总览.md`
8. `.codex/memory/YYYY-MM/记忆总览.md`
9. `.codex/memory/YYYY-MM/YYYY-MM-DD.md`

## 记忆周期
- 每轮总结都写入 `.codex/memory/YYYY-MM/YYYY-MM-DD.md`，并带上时间戳和结构化回忆字段。
- 当日总结在日切前只保留在当日日记中。
- 日切后的首轮工作，把昨日日记归档到 `.codex/memory/YYYY-MM/记忆总览.md`。
- 月切后的首轮工作，把已闭月总览归档到 `.codex/memory/全局记忆总览.md`。

## 核验要求
- `python scripts/manage_codex_memory.py status --root .`
- `python scripts/manage_codex_memory.py verify-rollups --root .`
- 不要把产品运行态数据写入 `.codex/`。
- 读取、写入和回归验证的证据都保留在当前工作区。

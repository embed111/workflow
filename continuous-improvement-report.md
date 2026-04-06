# 本轮持续迭代报告

- 生成时间：`2026-04-06T21:41:20.0145542+08:00`
- 当前 active 版本：`V1`
- 本轮聚焦任务包：`V1-P0 / V1-P1`

## 本轮结论
- 当前最高优先未完成问题仍是 `V1-P0 / V1-P1`，不是已经预挂到任务中心里的 `V1-P5`。这轮应该继续修“schedule trigger 非终态恢复 + 多处真相源分叉”，不能跳版。
- `prod` 的真实监听仍在 `127.0.0.1:8090`。`envs/prod.json` 已写 `8090`，但 `instances/prod.json` 仍残留 `8098`，当前运行真相源已经分叉。
- `[持续迭代] workflow` 的 `sti-20260406-1636431e -> node-sti-20260406-1636431e` 已被系统按“运行句柄缺失或 workflow 已重启”收口为 `failed`。
- `2026-04-06 20:43` 的 smoke trigger `sti-20260406-6b3e899a` 和 `2026-04-06 20:53` 的保底唤醒 trigger `sti-20260406-4e3ff2f4` 都已经命中并建出节点，但现场仍暴露出“trigger 已 hit / node 已建出 / detail 仍 queued / worker 线程可能丢失”的恢复缺口。

## 本轮交付
- 我延续了 `pm-main` 工作区里尚未提交的 `schedule_service.py` 修复方向：让 worker 周期扫描最近的 `trigger_hit/queued/running/dispatch_failed` 非终态 trigger，并重挂后台处理线程。
- 我把 `verify_schedule_trigger_recovery_worker.py` 补强为三类现场断言：
  - 无 assignment refs 的 `dispatch_failed` 必须恢复。
  - 有 refs 但未终态的 `queued` 必须恢复。
  - 有 refs 且已终态的 trigger 必须跳过，不得重启。
- 我把 `docs/workflow/governance/PM版本推进计划.md` 同步到当前现网事实：`prod=20260406-184906`、`candidate=20260406-193047`，并明确本轮仍以 `V1-P0 / V1-P1` 为先。
- 我把“worker 需要周期恢复最近非终态 trigger，而不是只靠 scan/detail 人工补偿”的经验补进了 `.codex/experience/schedule-trigger-closure.md`。

## 验证证据
- 端口与版本真相：
  - `D:/code/AI/J-Agents/workflow/.running/control/envs/prod.json`
  - `D:/code/AI/J-Agents/workflow/.running/control/instances/prod.json`
  - `D:/code/AI/J-Agents/workflow/.running/control/prod-last-action.json`
  - `Get-NetTCPConnection -LocalPort 8090,8098 -State Listen`：当前只有 `8090` 在监听
- 运行态与计划真相：
  - `GET http://127.0.0.1:8090/api/status`
  - `GET http://127.0.0.1:8090/api/dashboard`
  - `GET http://127.0.0.1:8090/api/schedules/sch-20260405-56eee156`
  - `GET http://127.0.0.1:8090/api/schedules/sch-20260405-67a89536`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/nodes/node-sti-20260406-1636431e.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/nodes/node-sti-20260406-6b3e899a.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/nodes/node-sti-20260406-4e3ff2f4.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260406-202952-bcb996/run.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260406-213012-966326/run.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260406-213042-9be6d3/run.json`
- 本轮验证：
  - `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260406-213956-701/report.md`
  - `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260406-214004-563/report.md`

## 下一轮入口
- 当前任务中心仍保留可执行入口，没有断链：
  - `node-20260406-213016-899b6a`：`V1-P5 升级 drain 模式与闭环接力收口`
  - `node-sti-20260406-6b3e899a`：`生产 smoke 基线 20260406-2043 / 2026-04-06 20:43:00`
  - `node-sti-20260406-4e3ff2f4`：`pm持续唤醒 - workflow 主线巡检 / 2026-04-06 20:53:00`
- 本轮没有再额外挂新的未来 schedule；当前不断链依赖上述 `ready` 入口继续承接。
- 推荐下一步：
  - 先把 `schedule_service.py` 这组 recovery patch 推进到发布链。
  - 再继续收口 `envs/prod.json / instances/prod.json / dashboard / workboard / schedule detail / node.json / run.json` 的真相一致性。

## 记忆与经验
- `memory_ref: .codex/memory/2026-04/2026-04-06.md`
- `experience_ref: .codex/experience/schedule-trigger-closure.md`

## 当前警告
- `dashboard` / `workboard` / `schedule detail` / `node.json` / `run.json` 目前仍未完全对齐，不能只看单一接口判断是否真的在跑。
- `node-sti-20260406-6b3e899a` 当前已经出现同一节点对应多条 `running` run 记录的现场，后续还要继续收口重复 dispatch 或 stale run 的判断。
- 本轮只跑了命中改动面的定向验证和行数门禁，没有补跑完整 `workflow gate`。

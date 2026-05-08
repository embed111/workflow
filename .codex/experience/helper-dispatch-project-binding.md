# helper 派发与 project 绑定经验

## 适用范围
- `workflow(pm)` 在全局主图里给 helper 手工/受支持 API 派发节点
- `workflow` 平台主线与其他运营项目并存，且某 helper 同时出现在多个 project 里
- 运营项目 PM 需要给本项目 writer/reviewer/member 角色真实派发任务的初始化与排障

## 稳定经验
- 运营项目 PM 初始化不能只给角色画像、记忆骨架和业务方法卡。如果期望它能给 `novel_master_writer`、`novel_quality_reviewer` 这类成员派活，必须把平台任务派发 runbook/API usage card 注入到该 PM 工作区，至少写清：base URL 或本地服务入口、稳定 `ticket_id`/项目任务图来源、`project_id`、`POST /api/assignments/{ticket_id}/nodes` 的最小字段、`POST /api/assignments/{ticket_id}/dispatch-next`、`status-detail`/`audit.jsonl`/`run.json` 回读证据、PowerShell UTF-8 body 注意事项，以及客户端超时后的文件真相复核规则。否则项目 PM 只能产出“可交接载荷”，并会诚实报告当前工作区没有可用 dispatch/API；这应归类为系统派发链缺口，不应误判为经营止损、题材失败或 writer 能力失败。
- 对 `workflow` 平台主线的 helper 节点，不要继续给 `workflow_devmate` 这类兼任其他 project controller 的角色使用 `project_binding_mode=auto`。更稳的默认是显式写 `project_id=workflow`；否则 live 现场会优先把节点绑到该 helper 的 controller project，这轮真实命中的是 `project-comics-smoke`。
- `POST /api/assignments/{ticket_id}/nodes` 当前只接受空值或 `project_binding_mode=auto`；不要为了表达“手工指定项目”传 `project_binding_mode=manual`。平台主线 helper 节点的稳定写法是只传显式 `project_id=workflow`，并省略 `project_binding_mode`。若误传 `manual`，API 会返回 `project_binding_mode_invalid` 或客户端看到 400。
- 手工调用 `create_node` 时不要把 `project_binding_mode=none` 或“省略 `project_id`”当成中性选择。平台主线 helper 节点如果漏传 `project_id=workflow`，live 会落成 `project_id="" / project_ref=""` 的空绑定节点；若节点已经进入 `running/live_execution`，本轮只记录 warning 和后续约束，不为了补字段重复创建同义任务。
- 即使节点已经显式落到某个 project，也不要让“所有分给 controller 角色的节点”都自动续挂 controller cadence。更稳的默认是：只有 dedicated project-controller 节点才允许续挂，至少满足 `expected_artifact=project-controller-iteration-report.md`、`node_name` 带 `[project-controller]`，或 `source_schedule_id` 命中该 controller 自己的 self-iteration schedule 之一；否则普通 helper 实现节点会污染 `next_handoff_interval_effective_after_run`，把错误的上一轮结果灌回 controller loop。
- 当 `dispatch-next` 的客户端调用超时或卡住时，不要直接把它记成“没有派发成功”。更稳的默认是先读 `C:/work/J-Agents/.output/tasks/<ticket>/nodes/<node>.json` 和 `runs/<run>/run.json`，确认节点/运行批次有没有已经起跑，再决定是否补派，避免重复建节点或误判卡死。
- 如果 `dispatch-next` 超时后只留下 `run.json status=starting / provider_pid=0`，且 `status-detail.execution_chain.latest_run.execution_truth=starting_stalled`，不要重复创建同义节点。先用受支持的 `rerun`/恢复入口重置同一节点，再回读 `status-detail`；现场可能出现 `rerun` 客户端也超时但同一 run 随后转成 `live_execution` 的情况，最终以 `provider_pid` 和 `execution_truth` 为准。
- 如果 helper 节点失败发生在接单读链/系统 skill 路径/工作区读链阶段，而不是目标代码实现或验收结论阶段，不要把它归类为代码修复失败，也不要直接创建同义 replacement 节点。先保留原节点的上游、artifact contract 和 project 绑定，执行 `repair-ghost-running`、同节点 `rerun`/`override-status ready`/`dispatch-next` 等受支持恢复动作；若客户端超时，继续回读 `status-detail`、`run.json`、`events.log`，直到确认同一节点是 `live_execution`、`ready` 还是 terminal blocked。
- 如果超时派发已经生成 `run.json/events.log` 且 provider 进程真实启动，不要再把这条运行批次当普通 ghost 去修。先核对 `provider_pid` 是否存活、`events.log` 是否已有 `provider_start` 或后续 item 事件，再让 node/run 状态回到同一个事实面；否则容易把活跃 helper 误标成 `cancelled/failed`，随后制造新的 ghost-running 假象。
- 当 live `create_node` 或 `delete_node` 的客户端调用超时，尤其是同一时间还有另一条 `workflow` 主线在跑时，不要直接重试同义 helper 切片。更稳的默认是先核 `audit.jsonl / node.json` 是否已经出现等价节点；如果并发运行已经先创建了同义 `ready/running` 节点，只删除后到的重复节点，保留先进入执行链的那条。
- `status-detail` 查询一个尚未存在、已拼错或创建失败的 `node_id` 时，可能返回默认选中节点，而不是直接报“该节点不存在”。回读时必须确认 `selected_node.node_id == requested_node_id`；若不相等，继续用 `/api/assignments/{ticket_id}/graph` 按 `node_id` 过滤或读节点文件，不能把默认选中的主线节点误当成刚创建的 helper 节点。

## 最小检查清单
1. 项目 PM 工作区是否有可执行派发 runbook/API usage card，而不只是业务 brief 模板
2. 平台主线 helper 节点是否显式写了非空 `project_id=workflow`，且省略 `project_binding_mode` 或仅在需要 auto 绑定时使用 `auto`
3. 若客户端调用超时，先核 `node.json / run.json / events.log / audit.jsonl`，不要先重发 create/dispatch/delete
4. helper 节点一旦已经起跑，只把 project 误绑定记成 warning 和后续约束，不在同轮里盲目重复造第二条同义任务
5. 若并发运行已经先建出同义 helper 节点，只保留先进入执行链的那条，后建重复节点立即删掉
6. `status-detail` 回读时先确认 `selected_node.node_id`，避免把默认选中节点误判成目标 helper 节点
7. helper 接单/读链失败优先恢复同一节点；只有确认原节点无法恢复且需要改变任务合同，才创建新节点并在 history 写明替代原因

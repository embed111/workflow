# V8-R3 flat surface phase2 测试设计评审

- version: `V8`
- requirement_id: `V8-R3`
- reviewed_at: `2026-04-23T01:14:55+08:00`
- owner: `workflow(pm)`

## 1. 测试目标
- 证明 current slice 已经把 `project context -> node contract -> execution` 的读取顺序前置到 assignment detail。
- 证明当 `selected_node.project_id` 找不到对应 `project_bootstrap_summary` 时，会正确 degrade 到 node-only contract，而不是伪造 project ownership 文案。
- 证明这轮不去误改 quiet default 与无关的 `project-ops` / workboard work surface；后续 `canonical header / workboard trim` 单独留给 `V9-R3`。

## 2. 用例分层
- focused regression：
  - `node scripts/acceptance/verify_assignment_detail_contract_grouping.js`
  - 断言 `项目上下文`、`节点合同` 与 `执行链路` 的渲染顺序，以及 node-only degrade。
- gate readback：
  - `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260422-172847.md`
  - 证明 current slice 已经进入正式 `workflow gate`，不再只是一次性交付件。
- UCD / quiet default 既有证据复用：
  - `v8-r3-flat-worksurface-phase2-brief.md`
  - 这轮不再重复造第二条 `project-ops` quiet probe；当前只要求“不破坏既有 quiet default”。

## 3. 关键断言
- assignment detail 在 `执行链路` 之前先出现 `项目上下文` 与 `节点合同`。
- `项目上下文` 从 `dashboard.project_bootstrap_summary.items[*]` 读出 `controller / members / goal`，不是再去拼一套新字段。
- node-only degrade 成立时，只保留 `节点合同`，不生成伪 project strip。
- 这轮不新增 `project-ops canonical header` 与 `workboard trim` 的断言；它们已经正式后移到 `V9-R3`。

## 4. 不覆盖项
- 不在 `V8-R3` 这轮里补 `project-ops canonical header / workboard trim` 的视觉或交互验收。
- 不把 `运营项目创建入口 / 项目产出图表达` 混进当前 current slice 的 focused regression。
- 不重跑一整套新的 browser 验收去证明当前 slice；当前 gate + focused regression 足够回答这轮的最小合同。

## 5. 评审结论
- `pass`
- 当前测试设计足以支撑 `V8-R3` current slice 从“实现 artifact 已有”推进到“focused regression + demo 准入已补齐”；后续 phase3 surface 改造转由 `V9-R3` 继续承接。

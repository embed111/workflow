# V8-R3 phase2 current slice demo

- version: `V8`
- requirement_id: `V8-R3`
- demo_at: `2026-04-23T01:14:55+08:00`
- owner: `workflow(pm)`

## 1. Demo 结论
- `V8-R3` 当前 slice 已经不再停在 brief：
  - assignment detail 会把 `项目上下文` 与 `节点合同` 前置到 `执行链路` 之前
  - quiet default 没有因为 project-role contract 到位而被误改
- 我这轮同步把 scope decision 收口了：
  - 当前 slice 继续留在 `V8`
  - `project-ops canonical header / workboard trim` 正式后移到 `V9-R3`

## 2. 现场证据
- brief：
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/artifacts/node-20260422-090428-7e4018/output/v8-r3-flat-worksurface-phase2-brief.md`
- implementation artifact：
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/artifacts/node-20260422-141404-2557cb/output/v8-r3-phase2-detail-strip-impl.md`
- focused regression：
  - `scripts/acceptance/verify_assignment_detail_contract_grouping.js`
- gate：
  - `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260422-172847.md`

## 3. 当前 slice 读面
- assignment detail 在展开 `执行链路` 前，先回答：
  - 这条节点属于哪个 project
  - project 的 controller / members / goal 是什么
  - 节点本身的 `return_contract / forbidden_anti_patterns / expected_artifact` 是什么
- 当前 slice 不再承担：
  - `project-ops` canonical header 重排
  - workboard `project-entry` 边界再裁剪
  - 项目创建入口或项目产出图表达

## 4. Demo 准入结论
- `demo_passed`
- `V8-R3` 不再因为“phase2 下一 slice 还没决定”继续占 `V8` blocker；后续 `project-ops canonical header / workboard trim` 已明确移交给 `V9-R3`。

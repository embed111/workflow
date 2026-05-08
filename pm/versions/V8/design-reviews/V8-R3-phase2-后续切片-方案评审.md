# V8-R3 phase2 后续切片方案评审

- version: `V8`
- requirement_id: `V8-R3`
- reviewed_at: `2026-04-23T01:14:55+08:00`
- owner: `workflow(pm)`
- collaborators: `workflow_ucdmate / workflow_devmate / workflow_testmate`

## 1. 背景
- `workflow_ucdmate` 已在 `2026-04-22` 交付 `v8-r3-flat-worksurface-phase2-brief.md`，把 phase2 明确拆成：
  - shared contract grouping primitive
  - `project-ops` canonical header
  - `task-center` workboard trim + role-facing detail strip
- 同日 `workflow_ucdmate` 又交付了 `v8-r3-phase2-detail-strip-impl.md`，把最小实现批次真正落到了 assignment detail 的 `项目上下文 / 节点合同` 读面，并配套补上 `verify_assignment_detail_contract_grouping.js` focused regression。
- 当前真正悬而未决的，不再是“还有没有下一刀可做”，而是：`project-ops canonical header / workboard trim` 这条后续 slice 继续留在 `V8`，还是正式后移到 `V9-R3`。

## 2. 方案判断
- 我这轮做的不是再起一条新实现，而是先把 `V8-R3` 的边界钉死：
  - `V8` 只保留已经落地的 current slice：
    - assignment detail 的 contract-first read-face
    - quiet default 不被 project-role fields 误改
    - focused regression 与 gate 证据
  - `project-ops canonical header / workboard trim` 正式后移到 `V9-R3`
- 后移理由：
  - 这两刀已经不只是 `V8` 当前 slice 的“收尾 polish”，而是会直接碰到 `project-ops` 作为 canonical work surface 的信息架构重排。
  - `V9-R3` 本来就承接“扁平化工作面三期 implementation、项目创建入口与项目产出图表达回归”；把这两刀放进 `V9-R3`，范围更一致，也避免把 `V8` 在切版前继续加胖。
  - `V8-R3` 当前 slice 的目标是把 `project contract -> node contract -> execution` 这条阅读顺序立住；这部分已经有正式实现和 focused regression，不必再等 phase3 才算当前刀完成。

## 3. 否决方案
- 否决：把 `project-ops canonical header / workboard trim` 继续留在 `V8`
  - 会让 `V8-R3` 从“当前 slice 收口”再次膨胀回“继续追一整段 project surface 重排”，和当前 active 版本的切版节奏冲突。
- 否决：不做正式后移，只在 history 里口头写“下一版再说”
  - 这会让 `V8-R3` 继续保持假 blocker，也会让 `V9-R3` 的承接关系只存在于我的脑子里。

## 4. 风险与护栏
- 风险：把后续 slice 移走后，团队误以为 `V8-R3` 已经把 `project-ops` 整体做完。
- 护栏：
  - 在 `V8` 文档里显式写清：current slice 已收口，但 `project-ops canonical header / workboard trim` 已后移到 `V9-R3`。
  - 在 `V9-R3` 的版本计划里同步登记这条继承关系。
- 风险：若 current slice 的 read-face regression 之后回退，当前后移判断会失效。
- 护栏：
  - 只要 `verify_assignment_detail_contract_grouping.js` 或 `workflow gate` 这条 focused regression 回红，我就把 `V8-R3` 重新拉回 active blocker，而不是继续按“已后移”自我安慰。

## 5. 验证口径
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/artifacts/node-20260422-090428-7e4018/output/v8-r3-flat-worksurface-phase2-brief.md`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/artifacts/node-20260422-141404-2557cb/output/v8-r3-phase2-detail-strip-impl.md`
- `scripts/acceptance/verify_assignment_detail_contract_grouping.js`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260422-172847.md`

## 6. 评审结论
- `go`
- `V8-R3` 当前 slice 继续留在 `V8` 并按 focused regression 收口；`project-ops canonical header / workboard trim` 正式后移到 `V9-R3`，不再作为 `V8` 的 scope decision blocker。

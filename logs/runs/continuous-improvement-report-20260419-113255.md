# continuous-improvement-report-20260419-113255

- topic: `V5-R4` 第二项目最小启动能力 dry-run 首次进入真实 helper 路由
- result: 我先用 `git -C .repository/pm-main update-index --refresh` 收掉 `pm-main` 的 3 个 stat 假脏，再把 `workflow_devmate` 的 `V5-R4 bootstrap dry run` 节点 `node-20260419-113025-d5b947` 种进全局主图，并补了 `pm/versions/V5/dry-run/2026-04/2026-04-19-v5-r4-second-project-bootstrap.md`
- version_transition_decision: `stay(V4)`
- live_ref: `/api/status`、`/api/assignments/asg-20260327-223335-b79f27/graph`
- memory_ref: `.codex/memory/2026-04/2026-04-19.md`
- preference_ref: `state/user-preferences.md`
- delta_observation: `launch_summary` 里的 dirty 快照不一定是 live 真相；当前现场里 `git status` 虽报 3 个 tracked dirty，但 `git diff` 为空、`hash-object` 与 index blob 一致，最终通过 `git update-index --refresh` 收成 clean。
- delta_validation: 下次再遇到 “status 脏但 diff 空” 时，先核 `hash-object + ls-files --stage`，再决定是否进入发布边界冻结模式；如果是同类假脏，就先 refresh index 再重算 `root_sync_state`。

# continuous-improvement-report 2026-04-22 02:59:36+08:00

- ticket: `asg-20260327-223335-b79f27`
- node: `node-sti-20260422-307e707d`
- version_transition_decision: `stay(V7)`
- lane: `测试探测`
- lifecycle_stage: `基于基线测试`
- root_sync_snapshot: `pm-main/workflow_devmate/workflow_testmate/workflow_qualitymate/workflow_bugmate/workflow_ucdmate = clean_synced@165f8e3`
- release_snapshot: `prod=current=20260422-020751 / candidate=20260422-020751 / candidate_is_newer=false / drain_active=false / running_task_count=2`
- summary:
  - 我先确认 `prod` 已经是 `20260422-020751`，所以这轮不再复述“等升级”，而是直接把 `V7-R2` 的 version-matched compare regression 和 `V7-R5` 的 prod lifecycle readback 送进 live。
  - 我用受支持 API 做了最小 lifecycle prod 读回：`DELETE /api/projects/workflow -> 409`，临时项目 `project-lifecycle-live-20260422-024130` 能创建、能删除，删除后项目列表只剩 `workflow`。
  - `workflow_testmate node-20260422-023504-r2cmp / arun-20260422-024047-0bbf79` 已经成功冻结 compare blocker，结论是 `blocked_verified`，下一批只需要 rebind 一条 baseline=`20260422-020751` 的 `api_catalog_live_regression` 新证据；`workflow_qualitymate node-20260422-023913-r5life / arun-20260422-024212-c912ee` 仍在继续采集 lifecycle 结构化证据。
- next:
  - 先切 code-side `api_catalog_live_regression` freshness rebind，再用 compare focused rerun 回读
  - 同时继续消费 `arun-20260422-024212-c912ee` 的 lifecycle readback，确认 active-task guard 和结构化证据是否齐了
  - 若 lifecycle helper 长时间不收敛，再按 supported rerun/恢复动作收口
- preference_ref: `state/user-preferences.md`
- delta_observation: compare 这条已经从“等 live regression 结果”进一步缩成“只差一条 version-matched 新证据绑定”；真正还在跑的是 lifecycle 结构化 readback。
- delta_validation: 下一轮优先消费 `arun-20260422-024212-c912ee`，同时切 `api_catalog_live_regression` evidence rebind 并 focused rerun compare。

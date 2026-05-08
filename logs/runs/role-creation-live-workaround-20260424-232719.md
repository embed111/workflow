# 创建 AI 小说角色现场记录 2026-04-24 23:27

- topic: 使用当前工作区的创建角色能力创建 `AI小说项目PM / AI小说审核官 / AI小说家` 三个角色，并在 `start` 链路卡住时做最小 workaround 交付。
- environment: `prod current=20260424-174453`
- session_ids:
  - `rcs-20260424-225336-a528b4` -> `novel_project_pm`
  - `rcs-20260424-225337-8780bf` -> `novel_quality_reviewer`
  - `rcs-20260424-225337-215641` -> `novel_master_writer`

## 结果
- 角色草稿分析成功：
  - 三个会话都已完成 analyst 分析。
  - `missing_fields=[]`
  - `start_gate.can_start=true`
  - 已自动生成能力模块、知识沉淀和首批任务建议。
- 正式 `start` 链路异常：
  - 对 `/api/training/role-creation/sessions/<session_id>/start` 的 live 调用长时间不返回。
  - 首次调用中 `novel_project_pm` 已落半程工作区初始化证据，但 `role_creation_sessions` 仍停在 `draft / workspace_init / pending`。
  - 其余两个角色在 API 层同样未完成状态推进。
- workaround 已交付：
  - 使用聚合后的 `training_center_runtime` 组件完成工作区初始化。
  - 补写 `agent_registry`，让三个角色进入 `released / trainable / idle`。
  - 刷新 `state/role-assets/` 骨架，并补首批 `ROLE_SPECIALTY.md + methods/*.md`。

## 交付角色
- `novel_project_pm`
  - workspace: `D:/code/AI/J-Agents/novel_project_pm`
  - specialty: `state/role-assets/ROLE_SPECIALTY.md`
  - methods:
    - `state/role-assets/methods/profitability-gate.md`
    - `state/role-assets/methods/serialization-operations-rhythm.md`
- `novel_quality_reviewer`
  - workspace: `D:/code/AI/J-Agents/novel_quality_reviewer`
  - specialty: `state/role-assets/ROLE_SPECIALTY.md`
  - methods:
    - `state/role-assets/methods/chapter-quality-gate.md`
    - `state/role-assets/methods/character-consistency-audit.md`
- `novel_master_writer`
  - workspace: `D:/code/AI/J-Agents/novel_master_writer`
  - specialty: `state/role-assets/ROLE_SPECIALTY.md`
  - methods:
    - `state/role-assets/methods/hook-first-opening.md`
    - `state/role-assets/methods/serial-pacing-outline.md`

## 验证
- 角色工作区存在：
  - `D:/code/AI/J-Agents/novel_project_pm`
  - `D:/code/AI/J-Agents/novel_quality_reviewer`
  - `D:/code/AI/J-Agents/novel_master_writer`
- `agent_registry` 已存在三条记录：
  - `novel_project_pm`
  - `novel_quality_reviewer`
  - `novel_master_writer`
- 三条记录均为：
  - `runtime_status=idle`
  - `lifecycle_state=released`
  - `training_gate_state=trainable`

## bug 结论
- bug_name: `role_creation_start_hangs_after_workspace_init`
- symptom:
  - 创建角色分析通过后，`start` 调用长时间不返回。
  - 至少一条会话已经写出 `role-creation-workspace-init` 证据，但 session 状态未推进到 `creating`。
- current_scope:
  - 影响通过产品正式 `start` 链把角色自动映射到任务中心主图。
  - 不影响角色定义分析本身。
  - 可通过受支持组件做工作区初始化和角色资产补齐作为临时 workaround。
- suspected_boundary:
  - 更像卡在“工作区初始化完成之后 -> 任务中心全局主图映射/ starter nodes 创建”这一段，而不是 analyst 对话或 role spec 生成。

## 后续安排
- scheduled_version: `V12`
- scheduling_note:
  - 后续把这条问题作为 `创建角色 start 链稳定性` 缺口纳入 `V12` 版本 history 继续收口。

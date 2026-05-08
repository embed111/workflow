# V5-R4 Second Project Bootstrap Dry Run

- created_at: `2026-04-19T11:32:55+08:00`
- version: `V5`
- requirement_id: `V5-R4`
- source_ticket_id: `asg-20260327-223335-b79f27`
- helper_node_id: `node-20260419-113025-d5b947`
- helper_agent_id: `workflow_devmate`
- helper_status: `succeeded`
- helper_run_id: `arun-20260419-115744-edff55`
- helper_completed_at: `2026-04-19T12:13:44+08:00`
- workflow_followup_commit: `18ca696`
- test_candidate_version: `20260419-134702`
- expected_artifact: `v5-r4-second-project-bootstrap-dry-run.md`

## 1. Goal
- Turn `V5-R4` from plan-level activation wording into the first executable dry-run slice for “second project minimum bootstrap”.
- Keep the slice small enough to unblock the next implementation batch without waiting for the full project-board or template-market vision.

## 2. Minimal Project Object Contract
```json
{
  "project_id": "project-<slug>",
  "project_name": "<name>",
  "project_type": "<type>",
  "controller_role_id": "<role_id>",
  "member_role_ids": [
    "<role_id>"
  ],
  "project_goal": "<goal>",
  "project_board_ref": "projects/<project_id>/board",
  "runtime_policy_ref": "projects/<project_id>/runtime-policy"
}
```

## 3. Runtime Policy Contract
```json
{
  "default_handoff_interval_minutes": 20,
  "next_handoff_interval_minutes": 20,
  "next_handoff_interval_override_source": "default",
  "next_handoff_interval_effective_after_run": "<run_id or next mainline ref>"
}
```

## 4. Workflow vs Project Boundary
- `workflow` remains the long-running platform and baseline project.
- The second project is a separate operational entity; its `controller_role_id`, `member_role_ids`, `project_goal`, and `runtime_policy_ref` must not be folded back into the base `workflow` single-project wording.
- Project-specific next-handoff overrides must stay scoped to the target project and must not mutate the base `workflow` default interval.

## 5. First Implementation Batch
1. Define the durable truth source for the project object and runtime policy.
2. Add the smallest create/read contract for the second project object.
3. Expose a minimal project entry that can distinguish `workflow` from the second project and show `controller_role_id` plus the next-handoff interval.
4. Add the first probe that can assert the object fields and runtime-policy fields without waiting for the full project board.

## 6. Current Live Route
- I already created the first helper slice in the global graph:
  - `ticket_id=asg-20260327-223335-b79f27`
  - `node_id=node-20260419-113025-d5b947`
  - `node_name=V5-R4 bootstrap dry run`
  - `assigned_agent_id=workflow_devmate`
  - `delivery_receiver_agent_id=workflow`
- The helper node has already reached `succeeded`, and the dry-run brief is no longer just a queued plan note.

## 7. Exit Signal For This Dry Run
- The helper artifact returned with a concrete implementation brief.
- The project object fields and runtime-policy fields are stable enough to become an implementation probe or minimal code batch.
- The “next handoff interval” UI contract is concrete enough to stop being a vague future note.

## 8. Follow-up Implementation Batch
- `workflow(pm)` has already consumed this dry run into `.repository/pm-main@18ca696 / ../workflow_code@18ca696`.
- The current implementation batch now includes:
  - `src/workflow_app/server/services/project_registry_service.py`
  - `src/workflow_app/server/api/projects.py`
  - `dashboard.project_bootstrap_summary`
  - workboard rail `项目入口`
  - project-scoped `next-handoff-interval` writeback
  - `verify_project_bootstrap_summary.py`
  - `verify_assignment_workboard_project_entry.js`
- The current release boundary is `test / prod candidate=20260419-134702`; the remaining gap is no longer “whether we have a dry run”, but “when project runtime policy will be consumed by the real 7x24 scheduler path”.

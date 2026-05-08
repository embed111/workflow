# V13-R7 fallback expiry ledger

- version: `V13`
- requirement: `V13-R7`
- status: `active-ledger-tightened-after-quality-scout`
- created_at: `2026-04-29T16:25:00+08:00`
- owner: `workflow(pm)`
- review_source: `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/artifacts/node-20260429-v13r7-reviewmate-expiry-review-recovery-152533/output/v13-r7-fallback-expiry-review.md`
- review_verdict: `request_changes`
- quality_scout_source: `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/artifacts/node-20260429-v13r7-qualitymate-ledger-scout-1625/output/v13-r7-fallback-expiry-ledger-scout.md`
- quality_scout_verdict: `request_changes_to_ledger / tiny_cleanup_only / live_fallback_deletion_blocked`
- rollback_anchor: `prod=20260429-133742 / source=da4c969c5c67ac5d0f1d45d8cf7f9d2353bcd84b / test-gate=.running/control/reports/test-gate-20260429-133742.json`

## 1. Ledger Rule

`V13-R7` is now a controlled ledger track, not a broad deletion track.

Deletion can start only when each row has:
- `owner`
- `live_usage`
- `expiry_condition`
- `required_probe`
- `rollback_anchor`
- `review_gate`
- `test_gate`
- `sequence_rule`

Any candidate without these fields remains `blocked` or `defer`. Live fallback deletion is blocked until `agent_discovery_service.discover_agents` is at least split, reviewed, and tested, or PM records a production stop-loss exception.

## 2. Immediate Candidates

| candidate_id | surface | scope | status | owner | live_usage | expiry_condition | required_probe | rollback_anchor | sequence_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `R7-C1` | API catalog dead registry metadata for `projects.runtime-policy.pause/resume` | Registry/discovery metadata only; no endpoint or handler deletion | `conditional_tiny_cleanup_candidate` | `workflow_devmate` | Prod API catalog reports `dead_registry_count=2`, but quality scout confirmed `api/projects.py` still has pause/resume handlers and `verify_project_runtime_policy_live_regression.py` still references them | preflight must first decide whether `dead_registry_count=2` is a real dead registry or a catalog/discovery false positive; if route is live, update/waive metadata rather than delete coverage; post-fix `dead_registry_count=0` without unexpected route-count loss | read-only source route check; `verify_api_catalog_cleanup_hooks.py`; API catalog readback; Interface Center module UI/live regression; `verify_project_runtime_policy_live_regression.py` when route stays live; `git diff --check`; line budget | revert cleanup commit and redeploy last green candidate `20260429-133742` | may run before `discover_agents` only as tiny metadata/discovery correction; must not be bundled with endpoint/handler deletion |
| `R7-C2` | Deprecated dev launcher `scripts/dev/start_workflow_web.ps1` plus README mapping | Dev tooling only; no prod/test deploy or launch behavior change | `tiny_cleanup_candidate` | `workflow_devmate` | File is a deprecation wrapper to `launch_workflow.ps1`; review found only README reference | `rg "start_workflow_web.ps1"` shows no consumers except docs, README mapping updated, PowerShell parse still passes | repository-wide `rg`; PowerShell parse check; README contract check; `git diff --check`; no test/prod deploy delta | revert cleanup commit and redeploy last green candidate `20260429-133742` | may run before `discover_agents` only if it stays non-runtime tooling |

## 3. Blocked Or Deferred Candidates

| candidate_id | surface | status | reason | unblock_condition | sequence_rule |
| --- | --- | --- | --- | --- | --- |
| `R7-B1` | `api/legacy.py`, `legacy_route_handlers.py`, `legacy_task_*_handlers.py` catch-all API surface | `blocked` | API catalog still reports `legacy_count=56` and incomplete live contract samples | per-route owner map, replacement route or explicit 404/410 decision, API catalog closure, workflow gate, live API regression | after `agent_discovery_service.discover_agents` |
| `R7-B2` | Runtime upgrade / assignment running-gate fallbacks | `blocked` | these surfaces currently protect workboard fallback, node-file fallback, running gate exclusion, and ghost-running overview | truth-owner replacement proof, running-gate probes, ghost-running repair acceptance, release-boundary TC-REL-003, prod readback | after `agent_discovery_service.discover_agents`, unless production stop-loss |
| `R7-B3` | `/api/config/show-test-data` 410 contract and legacy localStorage cleanup | `defer` | browser/API probes still assert the 410 compatibility contract and legacy key cleanup | telemetry/client proof, updated TD acceptance, full test-data toggle regression | after `agent_discovery_service.discover_agents` |
| `R7-B4` | `policy_fallback_service.build_agent_policy_payload_via_codex` | `defer` | `discover_agents` calls this fallback during cache miss or invalidation; not isolated trash | split `discover_agents` into scan/cache/policy phases, then re-review policy fallback as domain service or removable branch | `discover_agents` first |
| `R7-B5` | Work-record and assignment workspace legacy migrations | `blocked` | data-bearing historical compatibility and startup/runtime migration paths remain active | read-only inventory, migration-lock acceptance, startup smoke, rollback plan | after `agent_discovery_service.discover_agents` |
| `R7-B6` | Workflow gate fallback probes and acceptance fallback helpers | `defer` | current gate still relies on fallback probes to catch runtime failure modes | replace each fallback probe with canonical-contract coverage and prove gate still catches same failures | after `agent_discovery_service.discover_agents`, except pure probe refactors |
| `R7-B7` | Training registry structured-field fallback and release-review fallback UI payloads | `defer` | historical role releases may still lack bound public reports | inventory release profiles, prove report binding coverage, keep source transparency, run Training Center regressions | after `agent_discovery_service.discover_agents` |
| `R7-B8` | `assignment_service_parts` directory sprawl | `blocked_as_r7_deletion` | module sprawl is architecture debt, not expiry deletion | separate quality slice with owner map and facade plan | separate R5/R14 quality slice |

## 4. Blocked/Deferred Field Addendum

The quality scout found `R7-B1` through `R7-B8` were not complete deletion ledger rows. Until each item receives an owner, live-usage inventory, explicit probe, rollback anchor, review gate, and test gate, each remains non-actionable for deletion.

| candidate_id | owner | live_usage | expiry_condition | required_probe | rollback_anchor | review_gate | test_gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `R7-B1` | `unassigned_until_route_owner_map` | API catalog `legacy_count=56`; live samples still include chat/AB/training/assignment/schedule surfaces | per-route owner map and replacement/404/410 decision complete | per-route API regression, catalog closure, workflow gate, focused live API readback | per-route revert commit + last green candidate `20260429-133742` | required before any route-level removal | required before any route-level removal |
| `R7-B2` | `workflow_devmate / workflow_reviewmate` | runtime-upgrade, running gate, workboard fallback, node-file fallback, ghost overview | truth-owner replacement proof exists and current prod readback stays ghost-free | running-gate fallback probes, ghost-running repair acceptance, TC-REL-003, prod readback | revert truth-owner replacement commit + last green candidate `20260429-133742` | required | required |
| `R7-B3` | `workflow_testmate` | user-visible 410 test-data toggle contract and browser localStorage cleanup | accepted compatibility change replaces 410/localStorage probes | full test-data toggle browser/API regression | revert compatibility change + last green candidate `20260429-133742` | required | required |
| `R7-B4` | `workflow_devmate` | `discover_agents` still calls policy fallback on cache miss/invalidation | `discover_agents` split proves scan/cache/policy phases and re-review classifies fallback | discover-agents behavior probe + policy fallback focused probe | revert split/deletion commit + last green candidate `20260429-133742` | required | required |
| `R7-B5` | `workflow_devmate / workflow_testmate` | historical work-record and assignment workspace migration paths may still be data-bearing | read-only inventory proves legacy roots/tables empty or archived | migration-lock acceptance, startup smoke, rollback rehearsal | restore migration path commit + last green candidate `20260429-133742` | required | required |
| `R7-B6` | `workflow_testmate` | workflow gate still relies on fallback probes for runtime failure modes | canonical-contract probes replace each fallback probe without coverage loss | workflow gate registry probe + targeted fallback replacement regression | revert probe replacement commit | required | required |
| `R7-B7` | `workflow_devmate / workflow_testmate` | historical role releases may lack public reports | release profile inventory proves binding coverage or keeps source transparency | Training Center release/profile regressions | revert compatibility deletion + last green candidate `20260429-133742` | required | required |
| `R7-B8` | `workflow_devmate` | architecture debt; not expiry deletion | separate facade/owner-map quality slice accepted | line budget, module owner-map, facade probe | revert quality slice commit | separate review | separate test |

## 5. Next Execution Order

1. Keep `version_transition_decision=stay`.
2. Consume `workflow_qualitymate` scout before creating a devmate implementation node.
3. Dispatch `workflow_devmate` only for one of:
   - `R7-C2` deprecated dev launcher cleanup, or
   - `R7-C1` API catalog metadata/discovery preflight and correction, or
   - `V13-R5` first debt split: `agent_discovery_service.discover_agents`.
4. Do not combine tiny cleanup with live fallback deletion.
5. Do not approve broad legacy/fallback deletion until `workflow_reviewmate` changes the verdict from `request_changes` to `approve` for a concrete batch.

## 6. Current Gate Decision

- `live_fallback_deletion`: `blocked`
- `tiny_metadata_tooling_cleanup`: `allowed_after_owner_probe_binding`
- `R7-C1`: `conditional_only_after_live_route_preflight`
- `R7-C2`: `safe_tiny_cleanup_candidate`
- `agent_discovery_first_debt`: `must_schedule_before_live_expiry_batch`
- `V14_activation`: `not_ready`

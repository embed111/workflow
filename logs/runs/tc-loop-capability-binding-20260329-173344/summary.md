# Training Loop Capability Binding Evidence (20260329-173344)

- base_url: http://127.0.0.1:18110
- queue_round1: tq-20260329-173347-fb87fe
- queue_round2: tq-20260329-173347-909a00
- server_stdout: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/server_stdout.log
- server_stderr: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/server_stderr.log

## API
- 01_create_plan.json: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/api/01_create_plan.json
- 02_execute_round1.json: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/api/02_execute_round1.json
- 03_loop_round1.json: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/api/03_loop_round1.json
- 04_status_detail_round1.json: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/api/04_status_detail_round1.json
- 05_capability_example_round1.json: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/api/05_capability_example_round1.json
- 06_enter_next_round.json: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/api/06_enter_next_round.json
- 07_execute_round2.json: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/api/07_execute_round2.json
- 08_loop_round2.json: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/api/08_loop_round2.json
- 09_status_detail_round2.json: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/api/09_status_detail_round2.json
- 10_capability_example_round2_blocked.json: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/api/10_capability_example_round2_blocked.json
- 11_behavior_evidence.json: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/api/11_behavior_evidence.json

## DOM Probes
- dom_assertions.json: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/probes/dom_assertions.json
- round1_default.dom.html: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/probes/round1_default.dom.html
- round2_baseline.dom.html: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/probes/round2_baseline.dom.html
- round2_default.dom.html: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/probes/round2_default.dom.html

## Screenshots
- 角色中心训练优化首屏: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/screenshots/01_training_optimization_first_screen_round1.png
  url: http://127.0.0.1:18110/?tc_loop_mode=status&tc_loop_task=tq-20260329-173347-fb87fe&tc_loop_node=tq-20260329-173347-fb87fe&tc_loop_search=tc-loop-capability-binding+20260329-173344
- 中部聊天壳能力列表: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/screenshots/02_chat_shell_capability_list_round1.png
  url: http://127.0.0.1:18110/?tc_loop_mode=status&tc_loop_task=tq-20260329-173347-fb87fe&tc_loop_node=tq-20260329-173347-fb87fe&tc_loop_search=tc-loop-capability-binding+20260329-173344
- 能力项效果与评分同屏: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/screenshots/03_effect_and_score_round1.png
  url: http://127.0.0.1:18110/?tc_loop_mode=status&tc_loop_task=tq-20260329-173347-fb87fe&tc_loop_node=tq-20260329-173347-fb87fe&tc_loop_search=tc-loop-capability-binding+20260329-173344
- Gate-B Gate-C 绑定到能力项: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/screenshots/04_gate_binding_round2_blocked.png
  url: http://127.0.0.1:18110/?tc_loop_mode=status&tc_loop_task=tq-20260329-173347-909a00&tc_loop_node=tq-20260329-173347-909a00&tc_loop_search=tc-loop-capability-binding+20260329-173344
- 右侧默认任务与能力演进: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/screenshots/05_right_tasks_evolution_default_round2.png
  url: http://127.0.0.1:18110/?tc_loop_mode=status&tc_loop_task=tq-20260329-173347-909a00&tc_loop_node=tq-20260329-173347-909a00&tc_loop_search=tc-loop-capability-binding+20260329-173344
- 右侧当前能力基线: D:/code/AI/J-Agents/workflow/logs/runs/tc-loop-capability-binding-20260329-173344/screenshots/06_right_baseline_round2.png
  url: http://127.0.0.1:18110/?tc_loop_mode=status&tc_loop_task=tq-20260329-173347-909a00&tc_loop_node=tq-20260329-173347-909a00&tc_loop_search=tc-loop-capability-binding+20260329-173344&tc_loop_tab=baseline

## Key Findings
- Round1 capability object renders with effect evidence, score, Gate-B and Gate-C; historical result is `not_affected`.
- Round2 capability object contains `gate_status.gate_c=blocked`; `tasks_evolution.auto_publish.status=blocked`.
- Default right tab stays on `任务 / 能力演进`; `当前能力基线` can be switched independently.

  // Training center actions, release operations, and probe flows.

  function trainingCenterPlanPayload() {
    return {
      target_agent_id: trainingCenterSelectedTargetAgent(),
      capability_goal: safe($('tcPlanGoalInput') ? $('tcPlanGoalInput').value : '').trim(),
      training_tasks: parseTrainingTasksInput(),
      acceptance_criteria: safe($('tcPlanAcceptanceInput') ? $('tcPlanAcceptanceInput').value : '').trim(),
      priority: safe($('tcPlanPrioritySelect') ? $('tcPlanPrioritySelect').value : '').trim(),
      execution_engine: 'workflow_native',
      operator: 'web-user',
      created_by: 'web-user',
    };
  }

  async function enqueueTrainingCenterPlan(source) {
    const mode = safe(source).toLowerCase() === 'auto_analysis' ? 'auto_analysis' : 'manual';
    const payload = trainingCenterPlanPayload();
    const endpoint = mode === 'manual' ? '/api/training/plans/manual' : '/api/training/plans/auto';
    const data = await postJSON(endpoint, payload);
    setTrainingCenterError('');
    setTrainingCenterRunResult(data);
    await refreshTrainingCenterQueue();
    await refreshTrainingCenterAgents();
    return data;
  }

  async function submitTrainingCenterPlanFromLoop(action) {
    const mode = safe(action).toLowerCase() === 'start' ? 'start' : 'draft';
    const created = await enqueueTrainingCenterPlan('manual');
    const queueTaskId = safe(created && created.queue_task_id).trim();
    if (!queueTaskId) {
      renderTrainingLoop();
      return created;
    }
    state.tcLoopSelectedQueueTaskId = queueTaskId;
    state.tcLoopSelectedNodeId = queueTaskId;
    state.tcLoopMode = 'status';
    state.tcLoopStatusTab = 'overview';
    if (mode === 'start') {
      await executeTrainingCenterQueueTask(queueTaskId);
    }
    await refreshTrainingLoopServerData(queueTaskId, { force: true });
    renderTrainingCenterQueue();
    renderTrainingLoop();
    return created;
  }

  async function renameTrainingCenterQueueTask(queueTaskId, nextTitle) {
    const qid = safe(queueTaskId).trim();
    if (!qid) throw new Error('请先选择训练任务');
    const title = safe(nextTitle).trim();
    if (!title) throw new Error('任务名称不能为空');
    const data = await postJSON('/api/training/queue/' + encodeURIComponent(qid) + '/rename', {
      capability_goal: title,
      operator: 'web-user',
    });
    setTrainingCenterError('');
    setTrainingCenterRunResult(data);
    await refreshTrainingCenterQueue();
  }

  async function removeTrainingCenterQueueTask(queueTaskId) {
    const data = await postJSON('/api/training/queue/' + encodeURIComponent(queueTaskId) + '/remove', {
      operator: 'web-user',
      reason: 'manual_remove_from_ui',
    });
    setTrainingCenterError('');
    setTrainingCenterRunResult(data);
    await refreshTrainingCenterQueue(false);
    await refreshTrainingCenterAgents();
  }

  async function executeTrainingCenterQueueTask(queueTaskId) {
    const data = await postJSON('/api/training/queue/' + encodeURIComponent(queueTaskId) + '/execute', {
      operator: 'web-user',
    });
    setTrainingCenterError('');
    setTrainingCenterRunResult(data);
    if (safe(data.run_id)) {
      const run = await getJSON('/api/training/runs/' + encodeURIComponent(safe(data.run_id)));
      setTrainingCenterRunResult(run);
    }
    await refreshTrainingCenterQueue(false);
    await refreshTrainingCenterAgents();
    if (safe(state.tcLoopSelectedQueueTaskId).trim() === safe(queueTaskId).trim()) {
      await refreshTrainingLoopServerData(queueTaskId, { force: true });
    }
  }

  async function dispatchNextTrainingCenterQueue() {
    const data = await postJSON('/api/training/queue/dispatch-next', {
      operator: 'web-user',
    });
    setTrainingCenterError('');
    setTrainingCenterRunResult(data);
    await refreshTrainingCenterQueue(false);
    await refreshTrainingCenterAgents();
  }

  function selectedTrainingCenterAgentId() {
    const fromState = safe(state.tcSelectedAgentId).trim();
    if (fromState) return fromState;
    return safe(trainingCenterSelectedTargetAgent()).trim();
  }

  async function switchTrainingCenterAgentVersion() {
    const agentId = selectedTrainingCenterAgentId();
    if (!agentId) throw new Error('请先选择角色');
    const versionLabel = safe($('tcSwitchVersionSelect') ? $('tcSwitchVersionSelect').value : '').trim();
    if (!versionLabel) throw new Error('请选择已发布版本');
    const currentVersion = currentTrainingCenterDisplayedVersion(state.tcSelectedAgentDetail || {});
    if (versionLabel === currentVersion) {
      return null;
    }
    const data = await postJSON('/api/training/agents/' + encodeURIComponent(agentId) + '/switch', {
      version_label: versionLabel,
      operator: 'web-user',
    });
    setTrainingCenterDetailError('');
    setTrainingCenterAgentActionResult(data);
    setTrainingCenterRunResult(data);
    await refreshTrainingCenterAgents();
    await refreshTrainingCenterQueue(false);
  }

  async function cloneTrainingCenterAgentFromCurrent() {
    const agentId = selectedTrainingCenterAgentId();
    if (!agentId) throw new Error('请先选择角色');
    const newAgentName = safe($('tcCloneAgentNameInput') ? $('tcCloneAgentNameInput').value : '').trim();
    if (!newAgentName) throw new Error('克隆角色名称必填');
    const data = await postJSON('/api/training/agents/' + encodeURIComponent(agentId) + '/clone', {
      new_agent_name: newAgentName,
      operator: 'web-user',
    });
    state.tcSelectedAgentId = safe(data.agent_id || '').trim();
    state.tcSelectedAgentName = safe(data.agent_name || '').trim();
    setTrainingCenterDetailError('');
    setTrainingCenterAgentActionResult(data);
    setTrainingCenterRunResult(data);
    await refreshTrainingCenterAgents();
    await refreshTrainingCenterQueue(false);
  }

  async function setTrainingCenterAgentAvatar() {
    const agentId = selectedTrainingCenterAgentId();
    if (!agentId) throw new Error('请先选择角色');
    const fileInput = $('tcAvatarFileInput');
    const file = fileInput && fileInput.files && fileInput.files[0] ? fileInput.files[0] : null;
    if (!file) throw new Error('请选择本地头像文件');
    const name = safe(file.name).trim();
    const ext = name.includes('.') ? safe(name.split('.').pop()).toLowerCase() : '';
    if (!['png', 'jpg', 'jpeg', 'webp'].includes(ext)) {
      throw new Error('头像格式仅支持 png/jpg/webp');
    }
    const size = Number(file.size) || 0;
    if (size <= 0) {
      throw new Error('头像文件内容为空');
    }
    if (size > 2 * 1024 * 1024) {
      throw new Error('头像文件超过 2MB 限制');
    }
    const dataUrl = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(safe(reader.result));
      reader.onerror = () => reject(new Error('头像文件读取失败'));
      reader.readAsDataURL(file);
    });
    const rawUrl = safe(dataUrl).trim();
    const splitIndex = rawUrl.indexOf(',');
    if (splitIndex <= 0) {
      throw new Error('头像文件读取失败');
    }
    const meta = rawUrl.slice(0, splitIndex);
    const payloadBase64 = rawUrl.slice(splitIndex + 1);
    const contentType = meta.replace(/^data:/i, '').replace(/;base64$/i, '').trim();
    try {
      const data = await postJSON('/api/training/agents/' + encodeURIComponent(agentId) + '/avatar', {
        upload_name: name,
        upload_content_type: contentType || safe(file.type),
        upload_base64: payloadBase64,
        operator: 'web-user',
      });
      if (fileInput) {
        fileInput.value = '';
      }
      setTrainingCenterDetailError('');
      setTrainingCenterAgentActionResult(data);
      setTrainingCenterRunResult(data);
      await refreshTrainingCenterAgents();
    } catch (err) {
      renderTrainingCenterAvatarPreview(state.tcSelectedAgentDetail || {});
      throw err;
    }
  }

  async function discardTrainingCenterPreRelease() {
    const agentId = selectedTrainingCenterAgentId();
    if (!agentId) throw new Error('请先选择角色');
    if (!hasTrainingCenterPublishedRelease(state.tcSelectedAgentDetail || {})) {
      throw new Error('没有首个发布版本，不能舍弃修改');
    }
    const data = await postJSON(
      '/api/training/agents/' + encodeURIComponent(agentId) + '/pre-release/discard',
      {
        operator: 'web-user',
      }
    );
    setTrainingCenterDetailError('');
    setTrainingCenterAgentActionResult(data);
    setTrainingCenterRunResult(data);
    await refreshTrainingCenterAgents();
    await refreshTrainingCenterQueue(false);
  }

  async function enterTrainingCenterReleaseReview() {
    const agentId = selectedTrainingCenterAgentId();
    if (!agentId) throw new Error('请先选择角色');
    startTrainingCenterReleaseReviewProgress(agentId, 'enter');
    try {
      const data = await postJSON(
        '/api/training/agents/' + encodeURIComponent(agentId) + '/release-review/enter',
        {
          operator: 'web-user',
        }
      );
      if (!state.tcReleaseReviewByAgent || typeof state.tcReleaseReviewByAgent !== 'object') {
        state.tcReleaseReviewByAgent = {};
      }
      state.tcReleaseReviewByAgent[agentId] = normalizeTrainingCenterReleaseReviewPayload(agentId, data);
      finishTrainingCenterReleaseReviewProgress(agentId);
      setTrainingCenterDetailError('');
      setTrainingCenterAgentActionResult(data);
      setTrainingCenterRunResult(data);
      renderTrainingCenterReleaseReview(agentId);
      await refreshTrainingCenterAgents();
    } catch (err) {
      failTrainingCenterReleaseReviewProgress(agentId, err);
      throw err;
    }
  }

  async function discardTrainingCenterReleaseReview() {
    const agentId = selectedTrainingCenterAgentId();
    if (!agentId) throw new Error('请先选择角色');
    const reason = safe($('tcEvalSummaryInput') ? $('tcEvalSummaryInput').value : '').trim();
    const data = await postJSON(
      '/api/training/agents/' + encodeURIComponent(agentId) + '/release-review/discard',
      {
        operator: 'web-user',
        reason: reason,
      }
    );
    if (!state.tcReleaseReviewByAgent || typeof state.tcReleaseReviewByAgent !== 'object') {
      state.tcReleaseReviewByAgent = {};
    }
    state.tcReleaseReviewByAgent[agentId] = normalizeTrainingCenterReleaseReviewPayload(agentId, data);
    setTrainingCenterDetailError('');
    setTrainingCenterAgentActionResult(data);
    setTrainingCenterRunResult(data);
    renderTrainingCenterReleaseReview(agentId);
    await refreshTrainingCenterAgents();
  }

  async function submitTrainingCenterManualEvaluation() {
    const agentId = selectedTrainingCenterAgentId();
    if (!agentId) throw new Error('请先选择角色');
    const decision = safe($('tcEvalDecisionSelect') ? $('tcEvalDecisionSelect').value : '').trim();
    const reviewer = safe($('tcEvalReviewerInput') ? $('tcEvalReviewerInput').value : '').trim();
    const summary = safe($('tcEvalSummaryInput') ? $('tcEvalSummaryInput').value : '').trim();
    if (decision === 'reject_discard_pre_release' && !hasTrainingCenterPublishedRelease(state.tcSelectedAgentDetail || {})) {
      throw new Error('没有首个发布版本，不能舍弃修改');
    }
    const data = await postJSON(
      '/api/training/agents/' + encodeURIComponent(agentId) + '/release-review/manual',
      {
        decision: decision,
        reviewer: reviewer,
        review_comment: summary,
        operator: 'web-user',
      }
    );
    if (!state.tcReleaseReviewByAgent || typeof state.tcReleaseReviewByAgent !== 'object') {
      state.tcReleaseReviewByAgent = {};
    }
    state.tcReleaseReviewByAgent[agentId] = normalizeTrainingCenterReleaseReviewPayload(agentId, data);
    setTrainingCenterDetailError('');
    setTrainingCenterAgentActionResult(data);
    setTrainingCenterRunResult(data);
    renderTrainingCenterReleaseReview(agentId);
    await refreshTrainingCenterAgents();
  }

  async function confirmTrainingCenterReleaseReview() {
    const agentId = selectedTrainingCenterAgentId();
    if (!agentId) throw new Error('请先选择角色');
    startTrainingCenterReleaseReviewProgress(agentId, 'confirm');
    try {
      const data = await postJSON(
        '/api/training/agents/' + encodeURIComponent(agentId) + '/release-review/confirm',
        {
          operator: 'web-user',
        }
      );
      if (!state.tcReleaseReviewByAgent || typeof state.tcReleaseReviewByAgent !== 'object') {
        state.tcReleaseReviewByAgent = {};
      }
      state.tcReleaseReviewByAgent[agentId] = normalizeTrainingCenterReleaseReviewPayload(agentId, data);
      finishTrainingCenterReleaseReviewProgress(agentId);
      setTrainingCenterDetailError('');
      setTrainingCenterAgentActionResult(data);
      setTrainingCenterRunResult(data);
      renderTrainingCenterReleaseReview(agentId);
      await refreshTrainingCenterAgents();
    } catch (err) {
      failTrainingCenterReleaseReviewProgress(agentId, err);
      throw err;
    }
  }

  async function runTrainingCenterProbe() {
    const output = {
      ts: new Date().toISOString(),
      case: trainingCenterProbeCase(),
      pass: false,
      error: '',
      error_code: '',
      module: '',
      agent_count: 0,
      selected_agent_id: '',
      selected_agent_name: '',
      release_count: 0,
      release_versions: [],
      release_has_commit_ref: false,
      lifecycle_state: '',
      training_gate_state: '',
      queue_count: 0,
      queue_removed_count: 0,
      queue_sources: [],
      clone_agent_id: '',
      risk_tip: '',
      run_status: '',
      api_result: {},
      review_state: '',
      review_decision: '',
      review_reviewer: '',
      review_can_review: false,
      review_can_confirm: false,
      review_error: '',
      publish_status: '',
      publish_error: '',
      fallback_status: '',
      release_review_card_mode: '',
      release_review_visible_grid_count: 0,
      release_report_ref_count: 0,
      release_report_button_count: 0,
      release_report_button_versions: [],
      release_report_unavailable_count: 0,
      release_report_unavailable_versions: [],
      release_report_dialog_open: false,
      release_report_dialog_title: '',
      release_report_dialog_version: '',
      release_report_dialog_text: '',
      release_review_current_pills: [],
      report_first_person_summary: '',
      report_change_summary: '',
      report_has_inventory: false,
      report_has_delta: false,
      analysis_chain_paths: {},
      execution_log_phases: [],
      role_profile_source: '',
      role_profile_source_release_id: '',
      role_profile_first_person_summary: '',
      active_role_profile_ref: '',
    };
    const errorPayload = (err) => ({
      ok: false,
      error: safe(err && err.message ? err.message : err),
      code: safe(err && err.code),
      status: Number(err && err.status) || 0,
      data: err && err.data ? err.data : {},
    });
    try {
      switchTab('training-center');
      setTrainingCenterModule('agents');
      await refreshTrainingCenterAgents();
      await refreshTrainingCenterQueue();
      const rows = Array.isArray(state.tcAgents) ? state.tcAgents : [];
      output.agent_count = rows.length;
      const probeCase = output.case;
      const requestedAgent = safe(queryParam('tc_probe_agent')).trim().toLowerCase();
      let selected = await selectTrainingCenterProbeAgent({ nonGitFirst: probeCase === 'ac_uo_04' });
      if (!selected) {
        selected = findTrainingCenterProbeAgent({});
      }
      const pickAgentBy = async (matcher) => {
        const list = Array.isArray(state.tcAgents) ? state.tcAgents : [];
        for (const row of list) {
          const aid = safe(row && row.agent_id).trim();
          if (!aid) continue;
          state.tcSelectedAgentId = aid;
          state.tcSelectedAgentName = safe(row.agent_name || '');
          state.tcSelectedAgentDetail = row;
          syncTrainingCenterPlanAgentOptions();
          updateTrainingCenterSelectedMeta();
          renderTrainingCenterAgentList();
          await refreshTrainingCenterSelectedAgentContext(aid);
          const detail = state.tcSelectedAgentDetail || {};
          const releases = Array.isArray(state.tcReleasesByAgent[aid]) ? state.tcReleasesByAgent[aid] : [];
          if (matcher(detail, releases)) {
            return row;
          }
        }
        return null;
      };

      if (requestedAgent) {
        const explicit = await pickAgentBy((detail) => {
          const agentId = safe(detail && detail.agent_id).trim().toLowerCase();
          const agentName = safe(detail && detail.agent_name).trim().toLowerCase();
          return requestedAgent === agentId || requestedAgent === agentName;
        });
        if (explicit) selected = explicit;
      }
      if (probeCase.startsWith('ac_ar_') && !requestedAgent) {
        const preferred = await pickAgentBy((detail, releases) => {
          return !!detail.git_available && releases.length >= 2;
        });
        if (preferred) selected = preferred;
      }
      const selectedId = safe(selected && selected.agent_id).trim();
      const selectedName = safe(selected && selected.agent_name).trim();
      output.selected_agent_id = selectedId;
      output.selected_agent_name = selectedName;

      if (probeCase === 'ac_uo_01') {
        setTrainingCenterModule('agents');
      } else if (probeCase === 'ac_uo_02' || probeCase === 'ac_uo_03' || probeCase === 'ac_uo_04') {
        setTrainingCenterModule('agents');
      } else if (probeCase === 'ac_uo_05_before') {
        setTrainingCenterModule('ops');
        fillTrainingCenterProbePlan(selectedId, 'before', 'P1');
      } else if (probeCase === 'ac_uo_05_after') {
        setTrainingCenterModule('ops');
        fillTrainingCenterProbePlan(selectedId, 'after', 'P1');
        output.api_result = await postJSON('/api/training/plans/manual', trainingCenterPlanPayload());
        await refreshTrainingCenterQueue();
      } else if (probeCase === 'ac_uo_06') {
        setTrainingCenterModule('ops');
        fillTrainingCenterProbePlan(selectedId, 'priority-missing', '');
        try {
          await postJSON('/api/training/plans/manual', trainingCenterPlanPayload());
        } catch (err) {
          setTrainingCenterError(err.message || String(err));
        }
      } else if (probeCase === 'ac_uo_07') {
        setTrainingCenterModule('ops');
        fillTrainingCenterProbePlan(selectedId, 'dispatch-p2', 'P2');
        await postJSON('/api/training/plans/manual', trainingCenterPlanPayload());
        fillTrainingCenterProbePlan(selectedId, 'dispatch-p0', 'P0');
        await postJSON('/api/training/plans/manual', trainingCenterPlanPayload());
        fillTrainingCenterProbePlan(selectedId, 'dispatch-p1', 'P1');
        await postJSON('/api/training/plans/manual', trainingCenterPlanPayload());
        await refreshTrainingCenterQueue();
      } else if (probeCase === 'ac_uo_08') {
        setTrainingCenterModule('ops');
        fillTrainingCenterProbePlan(selectedId, 'similarity', 'P2');
        if ($('tcPlanGoalInput')) $('tcPlanGoalInput').value = 'similarity-case';
        if ($('tcPlanTasksInput')) $('tcPlanTasksInput').value = 'normalize output\nstabilize retry';
        if ($('tcPlanAcceptanceInput')) $('tcPlanAcceptanceInput').value = 'shape stable';
        await postJSON('/api/training/plans/manual', trainingCenterPlanPayload());
        await postJSON('/api/training/plans/manual', trainingCenterPlanPayload());
        await refreshTrainingCenterQueue();
      } else if (probeCase === 'ac_uo_09_before') {
        setTrainingCenterModule('ops');
        fillTrainingCenterProbePlan(selectedId, 'remove-before', 'P1');
        await postJSON('/api/training/plans/manual', trainingCenterPlanPayload());
        await refreshTrainingCenterQueue();
      } else if (probeCase === 'ac_uo_09_after') {
        setTrainingCenterModule('ops');
        fillTrainingCenterProbePlan(selectedId, 'remove-after', 'P1');
        await postJSON('/api/training/plans/manual', trainingCenterPlanPayload());
        await refreshTrainingCenterQueue();
        const toRemove = (state.tcQueue || []).find((row) => safe(row.status).toLowerCase() === 'queued');
        if (toRemove && safe(toRemove.queue_task_id).trim()) {
          output.api_result = await postJSON(
            '/api/training/queue/' + encodeURIComponent(safe(toRemove.queue_task_id)) + '/remove',
            { operator: 'probe-user', reason: 'tc_probe_remove' }
          );
        }
        // Probe for AC-UO-09 needs to validate removed item state from queue payload.
        await refreshTrainingCenterQueue(true);
      } else if (probeCase === 'ac_uo_10') {
        setTrainingCenterModule('ops');
        fillTrainingCenterProbePlan(selectedId, 'manual-source', 'P2');
        await postJSON('/api/training/plans/manual', trainingCenterPlanPayload());
        fillTrainingCenterProbePlan(selectedId, 'auto-source', 'P2');
        await postJSON('/api/training/plans/auto', trainingCenterPlanPayload());
        await refreshTrainingCenterQueue();
      } else if (probeCase === 'ac_uo_11') {
        setTrainingCenterModule('ops');
        fillTrainingCenterProbePlan(selectedId, 'execute', 'P2');
        const created = await postJSON('/api/training/plans/manual', trainingCenterPlanPayload());
        const queueTaskId = safe(created && created.queue_task_id).trim();
        if (queueTaskId) {
          output.api_result = await postJSON('/api/training/queue/' + encodeURIComponent(queueTaskId) + '/execute', {
            operator: 'probe-user',
          });
        }
        await refreshTrainingCenterQueue();
      } else if (probeCase === 'ac_ar_01') {
        setTrainingCenterModule('agents');
      } else if (probeCase === 'ac_ar_02') {
        setTrainingCenterModule('agents');
      } else if (probeCase === 'ac_ar_03') {
        setTrainingCenterModule('agents');
        try {
          output.api_result = await postJSON('/api/training/agents/' + encodeURIComponent(selectedId) + '/switch', {
            version_label: 'deadbeef-not-release',
            operator: 'probe-user',
          });
        } catch (err) {
          output.api_result = errorPayload(err);
          output.error_code = safe(err && err.code);
        }
      } else if (probeCase === 'ac_ar_04') {
        setTrainingCenterModule('ops');
        const releases = Array.isArray(state.tcReleasesByAgent[selectedId]) ? state.tcReleasesByAgent[selectedId] : [];
        const latest = safe((releases[0] || {}).version_label).trim();
        const older = safe((releases[1] || {}).version_label).trim();
        if (older && latest && older !== latest) {
          await postJSON('/api/training/agents/' + encodeURIComponent(selectedId) + '/switch', {
            version_label: older,
            operator: 'probe-user',
          });
        }
        await refreshTrainingCenterAgents();
        await refreshTrainingCenterSelectedAgentContext(selectedId);
        fillTrainingCenterProbePlan(selectedId, 'ar04-frozen-enqueue', 'P1');
        try {
          output.api_result = await postJSON('/api/training/plans/manual', trainingCenterPlanPayload());
        } catch (err) {
          output.api_result = errorPayload(err);
          output.error_code = safe(err && err.code);
        }
      } else if (probeCase === 'ac_ar_05') {
        setTrainingCenterModule('ops');
        const releases = Array.isArray(state.tcReleasesByAgent[selectedId]) ? state.tcReleasesByAgent[selectedId] : [];
        const latest = safe((releases[0] || {}).version_label).trim();
        if (latest) {
          await postJSON('/api/training/agents/' + encodeURIComponent(selectedId) + '/switch', {
            version_label: latest,
            operator: 'probe-user',
          });
        }
        await refreshTrainingCenterAgents();
        await refreshTrainingCenterSelectedAgentContext(selectedId);
        fillTrainingCenterProbePlan(selectedId, 'ar05-unfreeze-enqueue', 'P1');
        output.api_result = await postJSON('/api/training/plans/manual', trainingCenterPlanPayload());
        await refreshTrainingCenterQueue();
      } else if (probeCase === 'ac_ar_06') {
        setTrainingCenterModule('ops');
        const releases = Array.isArray(state.tcReleasesByAgent[selectedId]) ? state.tcReleasesByAgent[selectedId] : [];
        const latest = safe((releases[0] || {}).version_label).trim();
        const older = safe((releases[1] || {}).version_label).trim();
        if (older && latest && older !== latest) {
          await postJSON('/api/training/agents/' + encodeURIComponent(selectedId) + '/switch', {
            version_label: older,
            operator: 'probe-user',
          });
        }
        const cloneName = safe(selectedId || 'probe-agent')
          .replace(/[^0-9A-Za-z._:-]/g, '')
          .slice(0, 72) + '-clone-' + String(Date.now()).slice(-5);
        const cloneResp = await postJSON('/api/training/agents/' + encodeURIComponent(selectedId) + '/clone', {
          new_agent_name: cloneName,
          operator: 'probe-user',
        });
        output.clone_agent_id = safe(cloneResp.agent_id || '').trim();
        await refreshTrainingCenterAgents();
        state.tcSelectedAgentId = output.clone_agent_id;
        await refreshTrainingCenterSelectedAgentContext(output.clone_agent_id);
        fillTrainingCenterProbePlan(output.clone_agent_id, 'ar06-clone-enqueue', 'P1');
        output.api_result = await postJSON('/api/training/plans/manual', trainingCenterPlanPayload());
        await refreshTrainingCenterQueue();
      } else if (probeCase === 'ac_ar_07') {
        setTrainingCenterModule('ops');
        const trainable = await pickAgentBy((detail) => safe(detail.training_gate_state).toLowerCase() !== 'frozen_switched');
        const trainableId = safe((trainable || {}).agent_id || state.tcSelectedAgentId).trim();
        fillTrainingCenterProbePlan(trainableId, 'ar07-train', 'P1');
        const created = await postJSON('/api/training/plans/manual', trainingCenterPlanPayload());
        const queueTaskId = safe(created.queue_task_id).trim();
        if (queueTaskId) {
          output.api_result = await postJSON('/api/training/queue/' + encodeURIComponent(queueTaskId) + '/execute', {
            operator: 'probe-user',
          });
        }
        await refreshTrainingCenterAgents();
        await refreshTrainingCenterSelectedAgentContext(trainableId);
        await refreshTrainingCenterQueue();
      } else if (probeCase === 'ac_ar_08') {
        setTrainingCenterModule('agents');
        let preRelease = await pickAgentBy((detail) => safe(detail.lifecycle_state).toLowerCase() === 'pre_release');
        if (!preRelease) {
          const trainable = await pickAgentBy((detail) => safe(detail.training_gate_state).toLowerCase() !== 'frozen_switched');
          const aid = safe((trainable || {}).agent_id || state.tcSelectedAgentId).trim();
          setTrainingCenterModule('ops');
          fillTrainingCenterProbePlan(aid, 'ar08-train-to-pre', 'P1');
          const created = await postJSON('/api/training/plans/manual', trainingCenterPlanPayload());
          const queueTaskId = safe(created.queue_task_id).trim();
          if (queueTaskId) {
            await postJSON('/api/training/queue/' + encodeURIComponent(queueTaskId) + '/execute', {
              operator: 'probe-user',
            });
          }
          await refreshTrainingCenterAgents();
          preRelease = await pickAgentBy((detail) => safe(detail.lifecycle_state).toLowerCase() === 'pre_release');
        }
        const discardAgentId = safe((preRelease || {}).agent_id || state.tcSelectedAgentId).trim();
        output.api_result = await postJSON(
          '/api/training/agents/' + encodeURIComponent(discardAgentId) + '/pre-release/discard',
          { operator: 'probe-user' }
        );
        await refreshTrainingCenterAgents();
        await refreshTrainingCenterSelectedAgentContext(discardAgentId);
      } else if (probeCase === 'ac_ar_09') {
        setTrainingCenterModule('agents');
        let preRelease = await pickAgentBy((detail) => safe(detail.lifecycle_state).toLowerCase() === 'pre_release');
        if (!preRelease) {
          const trainable = await pickAgentBy((detail) => safe(detail.training_gate_state).toLowerCase() !== 'frozen_switched');
          const aid = safe((trainable || {}).agent_id || state.tcSelectedAgentId).trim();
          setTrainingCenterModule('ops');
          fillTrainingCenterProbePlan(aid, 'ar09-train-to-pre', 'P1');
          const created = await postJSON('/api/training/plans/manual', trainingCenterPlanPayload());
          const queueTaskId = safe(created.queue_task_id).trim();
          if (queueTaskId) {
            await postJSON('/api/training/queue/' + encodeURIComponent(queueTaskId) + '/execute', {
              operator: 'probe-user',
            });
          }
          await refreshTrainingCenterAgents();
          preRelease = await pickAgentBy((detail) => safe(detail.lifecycle_state).toLowerCase() === 'pre_release');
        }
        const evalAgentId = safe((preRelease || {}).agent_id || state.tcSelectedAgentId).trim();
        output.api_result = await postJSON(
          '/api/training/agents/' + encodeURIComponent(evalAgentId) + '/release-evaluations/manual',
          {
            decision: 'approve',
            reviewer: 'probe-reviewer',
            summary: 'manual evaluation approve in probe',
            operator: 'probe-user',
          }
        );
        await refreshTrainingCenterAgents();
        await refreshTrainingCenterSelectedAgentContext(evalAgentId);
      } else if (probeCase === 'ac_ar_10') {
        setTrainingCenterModule('agents');
      } else if (
        probeCase === 'ac_ar_rr_09' ||
        probeCase === 'ac_ar_rr_10' ||
        probeCase === 'ac_ar_rr_11' ||
        probeCase === 'ac_ar_rr_12' ||
        probeCase === 'ac_ar_rr_13' ||
        probeCase === 'ac_ar_rr_14' ||
        probeCase === 'ac_ar_rr_15' ||
        probeCase === 'ac_ar_rr_16'
      ) {
        setTrainingCenterModule('agents');
        if (selectedId) {
          await refreshTrainingCenterSelectedAgentContext(selectedId);
        }
      } else {
        setTrainingCenterModule('ops');
        await refreshTrainingCenterQueue();
      }

      const selectedDetail = state.tcSelectedAgentDetail || {};
      const roleProfile = trainingCenterRoleProfile(selectedDetail);
      const currentReview = currentTrainingCenterReleaseReview(safe(state.tcSelectedAgentId).trim());
      const releases = state.tcReleasesByAgent[safe(state.tcSelectedAgentId)] || [];
      const queueItems = Array.isArray(state.tcQueue) ? state.tcQueue : [];
      output.module = safe(state.tcModule);
      output.selected_agent_id = safe(state.tcSelectedAgentId);
      output.selected_agent_name = safe(state.tcSelectedAgentName || selectedName);
      output.release_count = releases.length;
      output.release_versions = releases.map((row) => safe(row.version_label)).filter(Boolean);
      output.release_has_commit_ref = releases.some((row) => Object.prototype.hasOwnProperty.call(row || {}, 'commit_ref'));
      output.queue_count = queueItems.length;
      output.queue_removed_count = queueItems.filter((row) => safe(row.status).toLowerCase() === 'removed').length;
      output.queue_sources = Array.from(
        new Set(queueItems.map((row) => safe(row.source).toLowerCase()).filter(Boolean))
      );
      output.risk_tip = safe((output.api_result && output.api_result.risk_tip) || ($('tcOpsRisk') ? $('tcOpsRisk').textContent : ''));
      output.run_status = safe((output.api_result && output.api_result.status) || '');
      output.git_available = !!selectedDetail.git_available;
      output.status_tags = Array.isArray(selectedDetail.status_tags) ? selectedDetail.status_tags : [];
      output.lifecycle_state = safe(selectedDetail.lifecycle_state || '').toLowerCase();
      output.training_gate_state = safe(selectedDetail.training_gate_state || '').toLowerCase();
      output.review_state = safe(currentReview.release_review_state || '').toLowerCase();
      output.review_decision = safe(currentReview.review_decision || '').trim();
      output.review_reviewer = safe(currentReview.reviewer || '').trim();
      output.review_can_enter = !!currentReview.can_enter;
      output.review_can_discard = !!currentReview.can_discard;
      output.review_can_review = !!currentReview.can_review;
      output.review_can_confirm = !!currentReview.can_confirm;
      output.review_error = safe(currentReview.report_error || '').trim();
      output.review_report_error_code = safe(currentReview.report_error_code || '').trim().toLowerCase();
      output.review_report_missing_fields = Array.isArray(currentReview.report_missing_fields) ? currentReview.report_missing_fields : [];
      output.review_required_report_fields = Array.isArray(currentReview.required_report_fields) ? currentReview.required_report_fields : [];
      output.publish_status = safe(currentReview.publish_status || '').toLowerCase();
      output.publish_error = safe(currentReview.publish_error || '').trim();
      output.fallback_status = safe(currentReview.fallback && currentReview.fallback.status).toLowerCase();
      const releaseReviewCard = $('tcReleaseReviewCard');
      output.release_review_card_mode = safe(releaseReviewCard && releaseReviewCard.dataset && releaseReviewCard.dataset.reviewMode).trim().toLowerCase();
      output.release_review_visible_grid_count = Array.from(document.querySelectorAll('#tcReleaseReviewCard .tc-release-review-grid'))
        .filter((node) => !!node && !node.hidden)
        .length;
      const releaseReportButtons = Array.from(document.querySelectorAll('#tcReleaseList button'))
        .filter((node) => safe(node && node.textContent).trim() === '查看发布报告');
      const releaseReportUnavailableNodes = Array.from(document.querySelectorAll('#tcReleaseList .tc-item-sub'))
        .filter((node) => /未绑定可展示的发布报告文件/.test(safe(node && node.textContent).trim()));
      output.release_report_ref_count = releases.filter((row) => !!safe((row && (row.release_source_ref || row.capability_snapshot_ref)) || '').trim()).length;
      output.release_report_button_count = releaseReportButtons.length;
      output.release_report_button_versions = releaseReportButtons
        .map((node) => safe(node && node.dataset && node.dataset.releaseVersion).trim())
        .filter(Boolean);
      output.release_report_unavailable_count = releaseReportUnavailableNodes.length;
      output.release_report_unavailable_versions = releaseReportUnavailableNodes
        .map((node) => safe(node && node.dataset && node.dataset.releaseVersion).trim())
        .filter(Boolean);
      output.release_review_current_pills = Array.from(document.querySelectorAll('#tcReleaseReviewSubstage .tc-release-review-pill.current'))
        .map((node) => safe(node && node.textContent).trim())
        .filter(Boolean);
      output.report_previous_release_version = safe(currentReview.report && currentReview.report.previous_release_version).trim();
      output.report_first_person_summary = safe(currentReview.report && currentReview.report.first_person_summary).trim();
      output.report_change_summary = safe(currentReview.report && currentReview.report.change_summary).trim();
      output.report_release_recommendation = safe(currentReview.report && currentReview.report.release_recommendation).trim().toLowerCase();
      output.report_has_inventory =
        !!(currentReview.report && Array.isArray(currentReview.report.full_capability_inventory) && currentReview.report.full_capability_inventory.length);
      output.report_has_delta =
        !!(currentReview.report && Array.isArray(currentReview.report.capability_delta) && currentReview.report.capability_delta.length);
      output.report_has_knowledge_scope = !!safe(currentReview.report && currentReview.report.knowledge_scope).trim();
      output.report_agent_skill_count =
        currentReview.report && Array.isArray(currentReview.report.agent_skills) ? currentReview.report.agent_skills.length : 0;
      output.report_applicable_scenario_count =
        currentReview.report && Array.isArray(currentReview.report.applicable_scenarios) ? currentReview.report.applicable_scenarios.length : 0;
      output.report_warning_count =
        currentReview.report && Array.isArray(currentReview.report.warnings) ? currentReview.report.warnings.length : 0;
      output.report_has_failure_skeleton =
        !!safe(currentReview.report && currentReview.report.target_version).trim() &&
        !!safe(currentReview.report && currentReview.report.current_workspace_ref).trim() &&
        !!safe(currentReview.report && currentReview.report.change_summary).trim() &&
        !!safe(currentReview.report && currentReview.report.release_recommendation).trim() &&
        !!safe(currentReview.report && currentReview.report.next_action_suggestion).trim();
      output.analysis_chain_paths = {
        prompt_path: safe(currentReview.analysis_chain && currentReview.analysis_chain.prompt_path).trim(),
        stdout_path: safe(currentReview.analysis_chain && currentReview.analysis_chain.stdout_path).trim(),
        stderr_path: safe(currentReview.analysis_chain && currentReview.analysis_chain.stderr_path).trim(),
        report_path: safe(currentReview.analysis_chain && currentReview.analysis_chain.report_path).trim(),
        public_profile_markdown_path: safe(currentReview.public_profile_markdown_path).trim(),
        capability_snapshot_json_path: safe(currentReview.capability_snapshot_json_path).trim(),
      };
      output.execution_log_phases = Array.from(
        new Set(
          (Array.isArray(currentReview.execution_logs) ? currentReview.execution_logs : [])
            .map((row) => safe(row && row.phase).trim().toLowerCase())
            .filter(Boolean)
        )
      );
      output.role_profile_source = safe(roleProfile.profile_source).trim();
      output.role_profile_source_release_id = safe(roleProfile.source_release_id).trim();
      output.role_profile_first_person_summary = safe(roleProfile.first_person_summary).trim();
      output.active_role_profile_ref = safe(selectedDetail.active_role_profile_ref || '').trim();
      if ((probeCase === 'ac_ar_rr_12' || probeCase === 'ac_ar_rr_19') && output.release_report_button_count >= 1) {
        const requestedReleaseVersion = safe(queryParam('tc_probe_release_version')).trim();
        const releaseReportBtn = Array.from(document.querySelectorAll('#tcReleaseList button'))
          .find((node) => {
            if (safe(node && node.textContent).trim() !== '查看发布报告') return false;
            if (!requestedReleaseVersion) return true;
            return safe(node && node.dataset && node.dataset.releaseVersion).trim() === requestedReleaseVersion;
          });
        if (releaseReportBtn) {
          releaseReportBtn.click();
          await new Promise((resolve) => window.setTimeout(resolve, 250));
          const reportDialog = $('tcPublishedReleaseReportDialog');
          output.release_report_dialog_open = !!(reportDialog && reportDialog.open);
          const reportTitleNode = reportDialog ? reportDialog.querySelector('.tc-report-dialog-title') : null;
          const reportBodyNode = reportDialog ? reportDialog.querySelector('.tc-report-dialog-body') : null;
          output.release_report_dialog_title = safe(reportTitleNode && reportTitleNode.textContent).trim();
          output.release_report_dialog_version = safe(reportDialog && reportDialog.dataset && reportDialog.dataset.releaseVersion).trim();
          output.release_report_dialog_text = safe(reportBodyNode && reportBodyNode.textContent).trim().slice(0, 1600);
          if (probeCase !== 'ac_ar_rr_19' && reportDialog && reportDialog.open && typeof reportDialog.close === 'function') {
            reportDialog.close();
          }
        }
      }
      if (!output.error_code) {
        output.error_code = safe((output.api_result && output.api_result.code) || '').toLowerCase();
      }

      output.pass =
        output.agent_count >= 0 &&
        (probeCase === 'ac_uo_01'
          ? output.agent_count >= 1
          : probeCase === 'ac_uo_02' || probeCase === 'ac_uo_03'
            ? output.release_count >= 1
            : probeCase === 'ac_uo_04'
              ? output.status_tags.includes('git_unavailable')
              : probeCase === 'ac_uo_06'
                ? !!safe($('tcOpsErr').textContent)
              : probeCase === 'ac_uo_09_after'
                  ? output.queue_removed_count >= 1
                  : probeCase === 'ac_uo_10'
                    ? output.queue_sources.includes('manual') && output.queue_sources.includes('auto_analysis')
                    : probeCase === 'ac_ar_01'
                      ? output.agent_count >= 1
                      : probeCase === 'ac_ar_02'
                        ? output.release_count >= 1 && !output.release_has_commit_ref
                        : probeCase === 'ac_ar_03'
                          ? output.error_code === 'version_not_released'
                          : probeCase === 'ac_ar_04'
                            ? output.error_code === 'training_frozen_after_switch' || output.training_gate_state === 'frozen_switched'
                            : probeCase === 'ac_ar_05'
                              ? safe(output.api_result && output.api_result.queue_task_id) && output.training_gate_state !== 'frozen_switched'
                              : probeCase === 'ac_ar_06'
                                ? safe(output.clone_agent_id) && safe(output.api_result && output.api_result.queue_task_id)
                                : probeCase === 'ac_ar_07'
                                  ? safe(output.api_result && output.api_result.status).toLowerCase() === 'done' && output.lifecycle_state === 'pre_release'
                                  : probeCase === 'ac_ar_08'
                                    ? !!(output.api_result && output.api_result.discarded) && output.lifecycle_state === 'released'
                                    : probeCase === 'ac_ar_09'
                                      ? !!safe(output.api_result && output.api_result.evaluation_id) && safe(output.api_result && output.api_result.decision) === 'approve'
                                      : probeCase === 'ac_ar_10'
                                        ? true
                                        : probeCase === 'ac_ar_rr_09'
                                          ? output.review_state === 'report_generating'
                                            : probeCase === 'ac_ar_rr_10'
                                              ? output.review_state === 'report_ready' &&
                                                output.report_has_inventory &&
                                                output.report_has_delta &&
                                                output.report_has_knowledge_scope &&
                                                output.report_agent_skill_count >= 1 &&
                                                output.report_applicable_scenario_count >= 1 &&
                                                !!safe(output.analysis_chain_paths.prompt_path) &&
                                                !!safe(output.analysis_chain_paths.stdout_path) &&
                                                !!safe(output.analysis_chain_paths.stderr_path) &&
                                                !!safe(output.analysis_chain_paths.report_path) &&
                                                /^我/.test(output.report_first_person_summary)
                                            : probeCase === 'ac_ar_rr_11'
                                              ? output.review_state === 'review_approved' &&
                                                output.review_decision === 'approve_publish' &&
                                                !!output.review_reviewer
                                            : probeCase === 'ac_ar_rr_12'
                                                ? output.publish_status === 'success' &&
                                                  output.release_review_card_mode === 'inactive' &&
                                                  output.release_review_visible_grid_count === 0 &&
                                                  output.role_profile_source === 'latest_release_report' &&
                                                  !!output.active_role_profile_ref &&
                                                  output.release_report_ref_count >= 1 &&
                                                  output.release_report_button_count >= 1 &&
                                                  output.release_report_dialog_open &&
                                                  /发布报告/.test(output.release_report_dialog_title) &&
                                                  output.release_review_current_pills.length === 0 &&
                                                  /^我/.test(output.role_profile_first_person_summary)
                                                : probeCase === 'ac_ar_rr_19'
                                                  ? output.publish_status === 'success' &&
                                                    output.release_report_button_count >= 1 &&
                                                    output.release_report_dialog_open &&
                                                    /发布报告/.test(output.release_report_dialog_title) &&
                                                    (!safe(queryParam('tc_probe_release_version')).trim() ||
                                                      output.release_report_button_versions.includes(safe(queryParam('tc_probe_release_version')).trim())) &&
                                                    (!safe(queryParam('tc_probe_release_version')).trim() ||
                                                      output.release_report_dialog_version === safe(queryParam('tc_probe_release_version')).trim()) &&
                                                    (!safe(queryParam('tc_probe_release_version')).trim() ||
                                                      output.release_report_dialog_text.includes(safe(queryParam('tc_probe_release_version')).trim()))
                                                : probeCase === 'ac_ar_rr_20'
                                                  ? output.release_report_unavailable_count >= 1 &&
                                                    !output.release_report_dialog_open &&
                                                    (!safe(queryParam('tc_probe_release_version')).trim() ||
                                                      output.release_report_unavailable_versions.includes(safe(queryParam('tc_probe_release_version')).trim())) &&
                                                    (!safe(queryParam('tc_probe_release_version')).trim() ||
                                                      !output.release_report_button_versions.includes(safe(queryParam('tc_probe_release_version')).trim()))
                                                : probeCase === 'ac_ar_rr_13'
                                                  ? output.execution_log_phases.includes('prepare') &&
                                                    output.execution_log_phases.includes('git_execute') &&
                                                    output.execution_log_phases.includes('release_note') &&
                                                    output.execution_log_phases.includes('verify')
                                                  : probeCase === 'ac_ar_rr_14'
                                                    ? output.review_state === 'publish_failed' &&
                                                      !!output.fallback_status &&
                                                      output.execution_log_phases.includes('fallback_trigger') &&
                                                      output.execution_log_phases.includes('fallback_result')
                                                  : probeCase === 'ac_ar_rr_15'
                                                    ? output.review_state === 'report_failed' &&
                                                      !!output.review_error &&
                                                      !!output.review_report_error_code &&
                                                      output.report_has_failure_skeleton &&
                                                      !output.review_can_confirm
                                                    : probeCase === 'ac_ar_rr_16'
                                                      ? output.review_state === 'review_discarded' &&
                                                        output.review_can_enter &&
                                                        !output.review_can_confirm
                                         : true);
    } catch (err) {
      output.error = safe(err && err.message ? err.message : err);
      output.error_code = safe(err && err.code ? err.code : output.error_code);
    }
    const node = ensureTrainingCenterProbeOutputNode();
    node.textContent = JSON.stringify(output);
    node.setAttribute('data-pass', output.pass ? '1' : '0');
  }

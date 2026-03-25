  // Training center role creation workbench.

  function roleCreationEscapeHtml(value) {
    return safe(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function roleCreationSessionStatusText(value) {
    const key = safe(value).trim().toLowerCase();
    if (key === 'creating') return '创建中';
    if (key === 'completed') return '已完成';
    return '草稿';
  }

  function roleCreationStatusTone(value) {
    const key = safe(value).trim().toLowerCase();
    if (key === 'running' || key === 'creating' || key === 'current') return 'active';
    if (key === 'succeeded' || key === 'completed') return 'done';
    if (key === 'failed') return 'danger';
    if (key === 'archived') return 'archive';
    return 'pending';
  }

  function roleCreationStageStateText(value) {
    const key = safe(value).trim().toLowerCase();
    if (key === 'completed') return '已完成';
    if (key === 'current') return '当前阶段';
    return '待进入';
  }

  function roleCreationCurrentDetail() {
    return state.tcRoleCreationDetail && typeof state.tcRoleCreationDetail === 'object'
      ? state.tcRoleCreationDetail
      : {};
  }

  function roleCreationCurrentSession() {
    const detail = roleCreationCurrentDetail();
    return detail.session && typeof detail.session === 'object' ? detail.session : {};
  }

  function roleCreationCurrentProfile() {
    const detail = roleCreationCurrentDetail();
    return detail.profile && typeof detail.profile === 'object' ? detail.profile : {};
  }

  function roleCreationCurrentStages() {
    const detail = roleCreationCurrentDetail();
    return Array.isArray(detail.stages) ? detail.stages : [];
  }

  function roleCreationCurrentMessages() {
    const detail = roleCreationCurrentDetail();
    return Array.isArray(detail.messages) ? detail.messages : [];
  }

  function roleCreationOptimisticMessages(sessionId) {
    const key = safe(sessionId).trim();
    if (!key) return [];
    const store = state.tcRoleCreationOptimisticMessages && typeof state.tcRoleCreationOptimisticMessages === 'object'
      ? state.tcRoleCreationOptimisticMessages
      : {};
    return Array.isArray(store[key]) ? store[key] : [];
  }

  function roleCreationReplaceOptimisticMessages(sessionId, messages) {
    const key = safe(sessionId).trim();
    if (!key) return;
    const store = state.tcRoleCreationOptimisticMessages && typeof state.tcRoleCreationOptimisticMessages === 'object'
      ? Object.assign({}, state.tcRoleCreationOptimisticMessages)
      : {};
    const rows = Array.isArray(messages) ? messages.slice() : [];
    if (rows.length) {
      store[key] = rows;
    } else {
      delete store[key];
    }
    state.tcRoleCreationOptimisticMessages = store;
  }

  function roleCreationPushOptimisticMessage(sessionId, message) {
    const key = safe(sessionId).trim();
    if (!key || !message || typeof message !== 'object') return;
    const rows = roleCreationOptimisticMessages(key).slice();
    rows.push(Object.assign({}, message));
    roleCreationReplaceOptimisticMessages(key, rows);
  }

  function roleCreationDropOptimisticMessage(sessionId, clientMessageId) {
    const key = safe(sessionId).trim();
    const clientId = safe(clientMessageId).trim();
    if (!key || !clientId) return;
    const rows = roleCreationOptimisticMessages(key)
      .filter((item) => safe(item && item.client_message_id).trim() !== clientId);
    roleCreationReplaceOptimisticMessages(key, rows);
  }

  function roleCreationPruneOptimisticMessages(sessionId, serverMessages) {
    const key = safe(sessionId).trim();
    if (!key) return;
    const seen = new Set(
      (Array.isArray(serverMessages) ? serverMessages : [])
        .map((item) => safe(item && (item.client_message_id || (item.meta && item.meta.client_message_id))).trim())
        .filter((item) => !!item)
    );
    if (!seen.size) return;
    const rows = roleCreationOptimisticMessages(key)
      .filter((item) => !seen.has(safe(item && item.client_message_id).trim()));
    roleCreationReplaceOptimisticMessages(key, rows);
  }

  function roleCreationSessionProcessingInfo(sessionSummary) {
    const summary = sessionSummary && typeof sessionSummary === 'object' ? sessionSummary : {};
    const sessionId = safe(summary.session_id).trim();
    const optimisticCount = roleCreationOptimisticMessages(sessionId).length;
    const serverUnhandled = Math.max(0, Number(summary.unhandled_user_message_count || 0));
    const totalUnhandled = serverUnhandled + optimisticCount;
    let status = safe(summary.message_processing_status).trim().toLowerCase();
    if (optimisticCount > 0 && (!status || status === 'idle')) {
      status = 'pending';
    }
    if (!status) {
      status = totalUnhandled > 0 ? 'pending' : 'idle';
    }
    if (status === 'running' && totalUnhandled <= 0) {
      status = 'idle';
    } else if (status === 'pending' && totalUnhandled <= 0) {
      status = 'idle';
    } else if (status === 'idle' && totalUnhandled > 0) {
      status = 'pending';
    }
    let text = safe(summary.message_processing_status_text).trim();
    if (!text) {
      if (status === 'running') text = '分析中';
      else if (status === 'pending') text = '待分析';
      else if (status === 'failed') text = '分析失败';
      else text = '空闲';
    }
    return {
      status: status,
      text: text,
      active: status === 'pending' || status === 'running',
      failed: status === 'failed',
      unhandledCount: totalUnhandled,
      error: safe(summary.message_processing_error).trim(),
    };
  }

  function roleCreationCurrentProcessingInfo() {
    return roleCreationSessionProcessingInfo(roleCreationCurrentSession());
  }

  function roleCreationDisplayMessages() {
    const session = roleCreationCurrentSession();
    const serverRows = roleCreationCurrentMessages().slice();
    const optimisticRows = roleCreationOptimisticMessages(session.session_id);
    const merged = serverRows.slice();
    optimisticRows.forEach((item) => {
      merged.push(Object.assign({}, item));
    });
    merged.sort((a, b) => {
      const at = safe(a && a.created_at).trim();
      const bt = safe(b && b.created_at).trim();
      if (at !== bt) return at.localeCompare(bt);
      return safe(a && (a.message_id || a.client_message_id)).localeCompare(safe(b && (b.message_id || b.client_message_id)));
    });
    const processing = roleCreationCurrentProcessingInfo();
    if (safe(session.session_id).trim() && processing.active) {
      merged.push({
        message_id: 'local-processing-placeholder',
        role: 'assistant',
        content: processing.status === 'pending' ? '已收到，正在合并本轮消息…' : '分析中…',
        attachments: [],
        message_type: 'chat',
        created_at: new Date().toISOString(),
        processing_placeholder: true,
      });
    }
    return merged;
  }

  function roleCreationShouldPoll() {
    const sessionId = safe(state.tcRoleCreationSelectedSessionId).trim();
    if (!sessionId) return false;
    return roleCreationCurrentProcessingInfo().active || roleCreationOptimisticMessages(sessionId).length > 0;
  }

  function stopRoleCreationPoller() {
    if (state.tcRoleCreationPoller) {
      clearInterval(state.tcRoleCreationPoller);
      state.tcRoleCreationPoller = 0;
    }
  }

  function startRoleCreationPoller() {
    if (state.tcRoleCreationPoller) return;
    state.tcRoleCreationPoller = window.setInterval(() => {
      if (state.tcRoleCreationPollBusy) return;
      const sessionId = safe(state.tcRoleCreationSelectedSessionId).trim();
      if (!sessionId) {
        stopRoleCreationPoller();
        return;
      }
      state.tcRoleCreationPollBusy = true;
      refreshRoleCreationSessionDetail(sessionId, { skipRender: true, background: true })
        .catch((err) => {
          setRoleCreationError(err.message || String(err));
        })
        .finally(() => {
          state.tcRoleCreationPollBusy = false;
          if (!roleCreationShouldPoll()) {
            stopRoleCreationPoller();
          }
        });
    }, 900);
  }

  function syncRoleCreationPoller() {
    if (roleCreationShouldPoll()) {
      startRoleCreationPoller();
    } else {
      stopRoleCreationPoller();
    }
  }

  function roleCreationCurrentCreatedAgent() {
    const detail = roleCreationCurrentDetail();
    return detail.created_agent && typeof detail.created_agent === 'object' ? detail.created_agent : {};
  }

  function roleCreationCurrentDialogueAgent() {
    const detail = roleCreationCurrentDetail();
    return detail.dialogue_agent && typeof detail.dialogue_agent === 'object' ? detail.dialogue_agent : {};
  }

  function setRoleCreationError(text) {
    state.tcRoleCreationError = safe(text);
    const node = $('rcError');
    if (node) node.textContent = state.tcRoleCreationError;
  }

  function normalizeRoleCreationDetailTab(value) {
    return safe(value).trim().toLowerCase() === 'profile' ? 'profile' : 'evolution';
  }

  function setRoleCreationDetailTab(tabName) {
    const next = normalizeRoleCreationDetailTab(tabName);
    state.tcRoleCreationDetailTab = next;
    const evolutionBtn = $('rcDetailTabEvolution');
    const profileBtn = $('rcDetailTabProfile');
    const evolutionPane = $('rcDetailPaneEvolution');
    const profilePane = $('rcDetailPaneProfile');
    if (evolutionBtn) evolutionBtn.classList.toggle('active', next === 'evolution');
    if (profileBtn) profileBtn.classList.toggle('active', next === 'profile');
    if (evolutionPane) evolutionPane.classList.toggle('active', next === 'evolution');
    if (profilePane) profilePane.classList.toggle('active', next === 'profile');
  }

  function roleCreationUnresolvedTaskCount(detail) {
    const payload = detail && typeof detail === 'object' ? detail : roleCreationCurrentDetail();
    const stages = Array.isArray(payload.stages) ? payload.stages : [];
    let total = 0;
    stages.forEach((stage) => {
      const activeTasks = Array.isArray(stage && stage.active_tasks) ? stage.active_tasks : [];
      activeTasks.forEach((task) => {
        if (safe(task && task.status).trim().toLowerCase() !== 'succeeded') {
          total += 1;
        }
      });
    });
    return total;
  }

  function roleCreationCanComplete(detail) {
    const payload = detail && typeof detail === 'object' ? detail : roleCreationCurrentDetail();
    const session = payload.session && typeof payload.session === 'object' ? payload.session : {};
    return safe(session.status).trim().toLowerCase() === 'creating' && roleCreationUnresolvedTaskCount(payload) === 0;
  }

  function syncRoleCreationSessionSummary(sessionSummary) {
    const summary = sessionSummary && typeof sessionSummary === 'object' ? sessionSummary : {};
    const sessionId = safe(summary.session_id).trim();
    if (!sessionId) return;
    const rows = Array.isArray(state.tcRoleCreationSessions) ? state.tcRoleCreationSessions.slice() : [];
    const nextRows = [];
    let replaced = false;
    rows.forEach((row) => {
      if (safe(row && row.session_id).trim() !== sessionId) {
        nextRows.push(row);
        return;
      }
      nextRows.push(Object.assign({}, row || {}, summary));
      replaced = true;
    });
    if (!replaced) {
      nextRows.unshift(Object.assign({}, summary));
    }
    nextRows.sort((a, b) => safe(b && b.updated_at).localeCompare(safe(a && a.updated_at)));
    state.tcRoleCreationSessions = nextRows;
    state.tcRoleCreationTotal = nextRows.length;
  }

  function applyRoleCreationDetailPayload(payload, options) {
    const data = payload && typeof payload === 'object' ? payload : {};
    const session = data.session && typeof data.session === 'object' ? data.session : {};
    const sessionId = safe(session.session_id).trim();
    if (!sessionId) return null;
    roleCreationPruneOptimisticMessages(sessionId, data.messages);
    clearRoleCreationTaskPreview();
    state.tcRoleCreationDetail = data;
    state.tcRoleCreationSelectedSessionId = sessionId;
    writeSavedRoleCreationSessionId(sessionId);
    syncRoleCreationSessionSummary(session);
    syncRoleCreationPoller();
    if (!(options && options.skipRender)) {
      renderRoleCreationWorkbench();
    }
    return data;
  }

  async function refreshRoleCreationSessionDetail(sessionId, options) {
    const key = safe(sessionId).trim();
    const opts = options && typeof options === 'object' ? options : {};
    const background = !!opts.background;
    if (!key) {
      state.tcRoleCreationDetail = null;
      state.tcRoleCreationSelectedSessionId = '';
      writeSavedRoleCreationSessionId('');
      syncRoleCreationPoller();
      renderRoleCreationWorkbench();
      return null;
    }
    if (!background) {
      state.tcRoleCreationLoading = true;
    }
    if (!opts.skipRender && !background) {
      renderRoleCreationWorkbench();
    }
    try {
      const data = await getJSON('/api/training/role-creation/sessions/' + encodeURIComponent(key));
      if (safe(state.tcRoleCreationSelectedSessionId).trim() && safe(state.tcRoleCreationSelectedSessionId).trim() !== key) {
        return data;
      }
      setRoleCreationError('');
      return applyRoleCreationDetailPayload(data, opts);
    } finally {
      if (!background) {
        state.tcRoleCreationLoading = false;
      }
      syncRoleCreationPoller();
      renderRoleCreationWorkbench();
    }
  }

  async function selectRoleCreationSession(sessionId, options) {
    const key = safe(sessionId).trim();
    if (!key) return null;
    state.tcRoleCreationSelectedSessionId = key;
    writeSavedRoleCreationSessionId(key);
    if (
      state.tcRoleCreationDetail &&
      safe(roleCreationCurrentSession().session_id).trim() === key &&
      !(options && options.force)
    ) {
      syncRoleCreationPoller();
      renderRoleCreationWorkbench();
      return state.tcRoleCreationDetail;
    }
    return refreshRoleCreationSessionDetail(key, options);
  }

  async function refreshRoleCreationSessions(options) {
    const opts = options && typeof options === 'object' ? options : {};
    if (!state.agentSearchRootReady) {
      state.tcRoleCreationSessions = [];
      state.tcRoleCreationTotal = 0;
      state.tcRoleCreationSelectedSessionId = '';
      state.tcRoleCreationDetail = null;
      writeSavedRoleCreationSessionId('');
      syncRoleCreationPoller();
      renderRoleCreationWorkbench();
      return { items: [], total: 0 };
    }
    state.tcRoleCreationLoading = true;
    if (!opts.skipRender) {
      renderRoleCreationWorkbench();
    }
    try {
      const data = await getJSON('/api/training/role-creation/sessions');
      state.tcRoleCreationSessions = Array.isArray(data.items) ? data.items : [];
      state.tcRoleCreationTotal = Number(data.total || state.tcRoleCreationSessions.length || 0);
      const current = safe(state.tcRoleCreationSelectedSessionId).trim();
      const cached = readSavedRoleCreationSessionId();
      const availableIds = new Set(
        state.tcRoleCreationSessions
          .map((item) => safe(item && item.session_id).trim())
          .filter((item) => !!item)
      );
      let next = current;
      if (!availableIds.has(next)) {
        next = availableIds.has(cached) ? cached : '';
      }
      if (!availableIds.has(next)) {
        next = state.tcRoleCreationSessions.length
          ? safe(state.tcRoleCreationSessions[0].session_id).trim()
          : '';
      }
      state.tcRoleCreationSelectedSessionId = next;
      if (!next) {
        state.tcRoleCreationDetail = null;
        writeSavedRoleCreationSessionId('');
        setRoleCreationError('');
        syncRoleCreationPoller();
        return data;
      }
      return await refreshRoleCreationSessionDetail(next, { skipRender: true });
    } finally {
      state.tcRoleCreationLoading = false;
      syncRoleCreationPoller();
      renderRoleCreationWorkbench();
    }
  }

  async function createRoleCreationSession() {
    const data = await postJSON('/api/training/role-creation/sessions', {
      operator: 'web-user',
    });
    setRoleCreationError('');
    applyRoleCreationDetailPayload(data);
    return data;
  }

  async function deleteRoleCreationSession(sessionId) {
    const key = safe(sessionId).trim();
    if (!key) return null;
    const rows = Array.isArray(state.tcRoleCreationSessions) ? state.tcRoleCreationSessions : [];
    const session = rows.find((item) => safe(item && item.session_id).trim() === key) || {};
    const status = safe(session && session.status).trim().toLowerCase();
    const processing = roleCreationSessionProcessingInfo(session);
    if (status === 'creating') {
      throw new Error('创建中的角色不能直接删除，请先完成当前创建流程');
    }
    if (processing.active) {
      throw new Error('当前对话仍在分析中，请等待处理完成后再删除');
    }
    const title = safe(session && session.session_title).trim() || '未命名角色草稿';
    const confirmed = window.confirm(
      status === 'completed'
        ? ('确认从创建角色列表中删除“' + title + '”吗？已创建的角色工作区和任务图不会被删除。')
        : ('确认删除草稿“' + title + '”吗？当前对话记录会一并删除。')
    );
    if (!confirmed) return null;
    const data = await deleteJSON(
      '/api/training/role-creation/sessions/' + encodeURIComponent(key),
      { operator: 'web-user' },
    );
    roleCreationReplaceOptimisticMessages(key, []);
    clearRoleCreationTaskPreview();
    setRoleCreationError('');
    await refreshRoleCreationSessions();
    return data;
  }

  function resetRoleCreationDraft() {
    state.tcRoleCreationDraftAttachments = [];
    if ($('rcInput')) $('rcInput').value = '';
    if ($('rcImageInput')) $('rcImageInput').value = '';
    renderRoleCreationDraftAttachments();
  }

  async function postRoleCreationMessage() {
    const sessionId = safe(state.tcRoleCreationSelectedSessionId).trim();
    if (!sessionId) {
      throw new Error('请先创建或选择一个角色草稿');
    }
    const content = safe($('rcInput') ? $('rcInput').value : '').trim();
    const attachments = Array.isArray(state.tcRoleCreationDraftAttachments) ? state.tcRoleCreationDraftAttachments.slice() : [];
    if (!content && !attachments.length) {
      throw new Error('请先输入内容，或添加一张图片');
    }
    const clientMessageId = 'rc-local-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8);
    roleCreationPushOptimisticMessage(sessionId, {
      message_id: clientMessageId,
      client_message_id: clientMessageId,
      session_id: sessionId,
      role: 'user',
      content: content,
      attachments: attachments,
      message_type: 'chat',
      created_at: new Date().toISOString(),
      processing_state: 'pending',
      processing_state_text: '待处理',
      local_only: true,
    });
    resetRoleCreationDraft();
    syncRoleCreationPoller();
    renderRoleCreationWorkbench();
    let data;
    try {
      data = await postJSON(
        '/api/training/role-creation/sessions/' + encodeURIComponent(sessionId) + '/messages',
        {
          content: content,
          attachments: attachments,
          operator: 'web-user',
          client_message_id: clientMessageId,
        },
      );
    } catch (err) {
      roleCreationDropOptimisticMessage(sessionId, clientMessageId);
      if ($('rcInput') && !safe($('rcInput').value).trim()) {
        $('rcInput').value = content;
      }
      state.tcRoleCreationDraftAttachments = attachments.slice();
      renderRoleCreationDraftAttachments();
      syncRoleCreationPoller();
      renderRoleCreationWorkbench();
      throw err;
    }
    setRoleCreationError('');
    try {
      await refreshRoleCreationSessionDetail(sessionId, { skipRender: true });
    } catch (_) {
      applyRoleCreationDetailPayload(data, { skipRender: true });
    }
    renderRoleCreationWorkbench();
    return data;
  }

  async function startRoleCreationSelectedSession() {
    const sessionId = safe(state.tcRoleCreationSelectedSessionId).trim();
    if (!sessionId) {
      throw new Error('请先选择角色草稿');
    }
    const data = await postJSON(
      '/api/training/role-creation/sessions/' + encodeURIComponent(sessionId) + '/start',
      { operator: 'web-user' },
    );
    setRoleCreationError('');
    applyRoleCreationDetailPayload(data);
    refreshTrainingCenterAgents().catch(() => {});
    return data;
  }

  async function updateRoleCreationStage(stageKey) {
    const sessionId = safe(state.tcRoleCreationSelectedSessionId).trim();
    const key = safe(stageKey).trim();
    if (!sessionId || !key) return null;
    const data = await postJSON(
      '/api/training/role-creation/sessions/' + encodeURIComponent(sessionId) + '/stage',
      {
        stage_key: key,
        operator: 'web-user',
      },
    );
    setRoleCreationError('');
    applyRoleCreationDetailPayload(data);
    return data;
  }

  async function archiveRoleCreationTask(nodeId) {
    const sessionId = safe(state.tcRoleCreationSelectedSessionId).trim();
    const taskId = safe(nodeId).trim();
    if (!sessionId || !taskId) return null;
    const reason = window.prompt('请输入废案收口原因', '方向调整，暂不继续');
    if (reason === null) return null;
    if (!safe(reason).trim()) {
      throw new Error('废案收口原因不能为空');
    }
    const data = await postJSON(
      '/api/training/role-creation/sessions/' + encodeURIComponent(sessionId) + '/tasks/' + encodeURIComponent(taskId) + '/archive',
      {
        close_reason: safe(reason).trim(),
        operator: 'web-user',
      },
    );
    clearRoleCreationTaskPreview();
    setRoleCreationError('');
    applyRoleCreationDetailPayload(data);
    return data;
  }

  async function completeRoleCreationSelectedSession() {
    const sessionId = safe(state.tcRoleCreationSelectedSessionId).trim();
    if (!sessionId) {
      throw new Error('请先选择角色草稿');
    }
    const ok = window.confirm('确认当前后台任务已全部完成，并把该角色创建收口为已完成吗？');
    if (!ok) return null;
    const data = await postJSON(
      '/api/training/role-creation/sessions/' + encodeURIComponent(sessionId) + '/complete',
      {
        confirmed: true,
        operator: 'web-user',
      },
    );
    setRoleCreationError('');
    applyRoleCreationDetailPayload(data);
    refreshTrainingCenterAgents().catch(() => {});
    return data;
  }

  function roleCreationAttachmentThumbHtml(item, removable) {
    const attachment = item && typeof item === 'object' ? item : {};
    const attachmentId = safe(attachment.attachment_id).trim();
    const fileName = safe(attachment.file_name || 'image').trim();
    const dataUrl = safe(attachment.data_url).trim();
    return (
      "<div class='rc-draft-file'>" +
        "<img class='rc-draft-file-thumb' src='" + roleCreationEscapeHtml(dataUrl) + "' alt='" + roleCreationEscapeHtml(fileName) + "'/>" +
        "<div class='rc-draft-file-meta'>" +
          "<div class='rc-draft-file-name'>" + roleCreationEscapeHtml(fileName || '图片') + '</div>' +
          "<div class='rc-draft-file-sub'>" + roleCreationEscapeHtml(safe(attachment.content_type).trim() || 'image') + '</div>' +
        '</div>' +
        (
          removable
            ? "<button class='rc-draft-file-remove alt' type='button' data-attachment-id='" + roleCreationEscapeHtml(attachmentId) + "'>移除</button>"
            : ''
        ) +
      '</div>'
    );
  }

  function roleCreationMessageAttachmentsHtml(attachments) {
    const rows = Array.isArray(attachments) ? attachments : [];
    if (!rows.length) return '';
    return (
      "<div class='rc-message-assets'>" +
      rows.map((item) => (
        "<div class='rc-message-asset'>" +
          "<img src='" + roleCreationEscapeHtml(safe(item && item.data_url).trim()) + "' alt='" + roleCreationEscapeHtml(safe(item && item.file_name).trim() || '图片') + "'/>" +
        '</div>'
      )).join('') +
      '</div>'
    );
  }

  function roleCreationMessageRoleClass(message) {
    const item = message && typeof message === 'object' ? message : {};
    const messageType = safe(item.message_type).trim().toLowerCase();
    const role = safe(item.role).trim().toLowerCase();
    if (messageType !== 'chat' || role === 'system') return 'system';
    if (role === 'user') return 'user';
    return 'assistant';
  }

  function roleCreationMessageSenderText(message) {
    const role = safe(message && message.role).trim().toLowerCase();
    if (role === 'user') return '用户';
    if (role === 'system') return '系统';
    const dialogueAgent = roleCreationCurrentDialogueAgent();
    return safe(dialogueAgent.agent_name).trim() || '分析师';
  }

  function roleCreationMessageProcessingState(message) {
    const item = message && typeof message === 'object' ? message : {};
    return safe(item.processing_state || (item.meta && item.meta.processing_state)).trim().toLowerCase();
  }

  function roleCreationMessageProcessingText(message) {
    const stateKey = roleCreationMessageProcessingState(message);
    if (stateKey === 'processing') return '处理中';
    if (stateKey === 'processed') return '已处理';
    if (stateKey === 'failed') return '处理失败';
    if (stateKey === 'pending') return '待处理';
    return '';
  }

  function renderRoleCreationMessages() {
    const box = $('rcMessages');
    if (!box) return;
    const session = roleCreationCurrentSession();
    const rows = roleCreationDisplayMessages();
    if (!safe(session.session_id).trim()) {
      box.innerHTML = "<div class='rc-empty'>还没有创建草稿。点击左侧“新建”后，直接用对话描述你要的角色即可。</div>";
      return;
    }
    if (!rows.length) {
      box.innerHTML = "<div class='rc-empty'>当前草稿还没有消息。</div>";
      return;
    }
    box.innerHTML = rows.map((message) => {
      const cls = roleCreationMessageRoleClass(message);
      const attachmentsHtml = roleCreationMessageAttachmentsHtml(message.attachments);
      const content = safe(message && message.content);
      const processingState = roleCreationMessageProcessingState(message);
      const processingText = roleCreationMessageProcessingText(message);
      const processingChip = cls === 'user' && processingText
        ? ("<span class='rc-message-processing " + roleCreationEscapeHtml(processingState || 'processed') + "'>" + roleCreationEscapeHtml(processingText) + '</span>')
        : '';
      const metaHtml = cls === 'system'
        ? ''
        : (
          "<div class='rc-message-meta'>" +
            "<span class='rc-message-sender'>" + roleCreationEscapeHtml(roleCreationMessageSenderText(message)) + '</span>' +
            processingChip +
            "<span>" + roleCreationEscapeHtml(formatDateTime(message.created_at)) + '</span>' +
          '</div>'
        );
      return (
        "<div class='message " + cls + (message && message.processing_placeholder ? ' pending' : '') + "'>" +
          (cls === 'system' ? '' : "<div class='message-role'>" + roleCreationEscapeHtml(roleCreationMessageSenderText(message).slice(0, 1)) + '</div>') +
          "<div class='message-body'>" +
            metaHtml +
            attachmentsHtml +
            (content ? "<div class='message-text'>" + roleCreationEscapeHtml(content) + '</div>' : '') +
          '</div>' +
        '</div>'
      );
    }).join('');
    box.scrollTop = box.scrollHeight;
  }

  function roleCreationSessionSubtitle(session) {
    const summary = session && typeof session === 'object' ? session : {};
    const processing = roleCreationSessionProcessingInfo(summary);
    if (processing.active) {
      return processing.unhandledCount > 0
        ? (processing.text + ' · 待处理 ' + String(processing.unhandledCount) + ' 条')
        : processing.text;
    }
    if (processing.failed && processing.unhandledCount > 0) {
      return '有 ' + String(processing.unhandledCount) + ' 条消息处理失败，继续发送会自动重试';
    }
    const preview = safe(summary.last_message_preview).trim();
    if (preview) return preview;
    const missing = Array.isArray(summary.missing_fields) ? summary.missing_fields.length : 0;
    if (safe(summary.status).trim().toLowerCase() === 'draft' && missing > 0) {
      return '还缺 ' + String(missing) + ' 项关键信息';
    }
    return '等待继续补充';
  }

  function renderRoleCreationSessionList() {
    const box = $('rcSessionList');
    if (!box) return;
    const rows = Array.isArray(state.tcRoleCreationSessions) ? state.tcRoleCreationSessions : [];
    if (!rows.length) {
      box.innerHTML = "<div class='rc-empty'>当前还没有创建草稿。</div>";
      return;
    }
    box.innerHTML = rows.map((session) => {
      const sessionId = safe(session && session.session_id).trim();
      const current = sessionId && sessionId === safe(state.tcRoleCreationSelectedSessionId).trim();
      const missing = Array.isArray(session && session.missing_fields) ? session.missing_fields.length : 0;
      const status = safe(session && session.status).trim().toLowerCase();
      const processing = roleCreationSessionProcessingInfo(session);
      const canDelete = (status === 'draft' || status === 'completed') && !processing.active;
      return (
        "<div class='rc-session-card" + (current ? ' active' : '') + "'>" +
          "<button class='rc-session-card-main' type='button' data-session-id='" + roleCreationEscapeHtml(sessionId) + "'>" +
            "<div class='rc-session-card-top'>" +
              "<div class='rc-session-card-title'>" + roleCreationEscapeHtml(safe(session && session.session_title).trim() || '未命名角色草稿') + '</div>' +
              "<div class='rc-session-card-statuses'>" +
                "<span class='rc-chip " + roleCreationStatusTone(session && session.status) + "'>" + roleCreationEscapeHtml(roleCreationSessionStatusText(session && session.status)) + '</span>' +
                (
                  processing.active || processing.failed
                    ? "<span class='rc-chip " + roleCreationStatusTone(processing.status) + "'>" + roleCreationEscapeHtml(processing.text) + '</span>'
                    : ''
                ) +
              '</div>' +
            '</div>' +
            "<div class='rc-session-card-sub'>" + roleCreationEscapeHtml(roleCreationSessionSubtitle(session)) + '</div>' +
            "<div class='rc-session-card-meta'>" +
              "<span>" + roleCreationEscapeHtml(formatDateTime(session && session.updated_at)) + '</span>' +
              (
                missing > 0 && status === 'draft'
                  ? "<span>缺失 " + roleCreationEscapeHtml(String(missing)) + ' 项</span>'
                  : ''
              ) +
            '</div>' +
          '</button>' +
          (
            canDelete
              ? "<div class='rc-session-card-actions'><button class='bad rc-session-card-delete' type='button' data-rc-delete-session='" + roleCreationEscapeHtml(sessionId) + "'>" + roleCreationEscapeHtml(status === 'completed' ? '删除记录' : '删除草稿') + '</button></div>'
              : ''
          ) +
        '</div>'
      );
    }).join('');
  }

  function renderRoleCreationDraftAttachments() {
    const box = $('rcDraftFiles');
    if (!box) return;
    const rows = Array.isArray(state.tcRoleCreationDraftAttachments) ? state.tcRoleCreationDraftAttachments : [];
    if (!rows.length) {
      box.innerHTML = '';
      return;
    }
    box.innerHTML = rows.map((item) => roleCreationAttachmentThumbHtml(item, true)).join('');
  }

  function renderRoleCreationMeta() {
    const session = roleCreationCurrentSession();
    const profile = roleCreationCurrentProfile();
    const createdAgent = roleCreationCurrentCreatedAgent();
    const dialogueAgent = roleCreationCurrentDialogueAgent();
    const processing = roleCreationCurrentProcessingInfo();
    const draftMeta = $('rcDraftMeta');
    const sessionTitle = $('rcSessionTitle');
    const sessionMeta = $('rcSessionMeta');
    const composerMeta = $('rcComposerMeta');
    const startBtn = $('rcStartSessionBtn');
    const completeBtn = $('rcCompleteSessionBtn');
    const input = $('rcInput');
    const sendBtn = $('rcSendBtn');
    const pickImageBtn = $('rcPickImageBtn');
    const collapsedCount = $('rcDraftCollapsedCount');
    const collapsedCurrent = $('rcDraftCollapsedCurrent');
    if (draftMeta) {
      draftMeta.textContent = state.agentSearchRootReady
        ? '新建后通过对话逐步收口角色画像'
        : '根路径未就绪，创建角色功能已锁定';
    }
    if (collapsedCount) {
      collapsedCount.textContent = String(Array.isArray(state.tcRoleCreationSessions) ? state.tcRoleCreationSessions.length : 0);
    }
    if (collapsedCurrent) {
      collapsedCurrent.hidden = !safe(state.tcRoleCreationSelectedSessionId).trim();
    }
    if (sessionTitle) {
      sessionTitle.textContent = safe(session.session_title).trim() || '创建角色';
    }
    if (sessionMeta) {
      if (!safe(session.session_id).trim()) {
        sessionMeta.textContent = '先创建草稿，再通过对话补齐角色目标、能力边界和场景';
      } else if (safe(session.status).trim().toLowerCase() === 'draft') {
        const missingLabels = Array.isArray(profile.missing_labels) ? profile.missing_labels : [];
        const draftSegments = [
          safe(dialogueAgent.agent_name).trim() ? '对话分析师：' + safe(dialogueAgent.agent_name).trim() : '',
          processing.active
            ? ('当前状态：' + processing.text + (processing.unhandledCount > 0 ? '（' + String(processing.unhandledCount) + ' 条待处理）' : ''))
            : '',
          missingLabels.length
            ? '当前草稿还缺：' + missingLabels.join('、')
            : '草稿信息已齐，可直接开始创建',
        ].filter((item) => !!item);
        sessionMeta.textContent = draftSegments.join(' · ');
      } else if (safe(session.status).trim().toLowerCase() === 'creating') {
        const segments = [
          safe(dialogueAgent.agent_name).trim() ? '对话分析师：' + safe(dialogueAgent.agent_name).trim() : '',
          processing.active
            ? ('当前状态：' + processing.text + (processing.unhandledCount > 0 ? '（' + String(processing.unhandledCount) + ' 条待处理）' : ''))
            : '',
          safe(session.current_stage_title).trim() ? '当前阶段：' + safe(session.current_stage_title).trim() : '',
          safe(session.assignment_ticket_id).trim() ? '任务图：' + safe(session.assignment_ticket_id).trim() : '',
          safe(createdAgent.agent_name).trim() ? '执行主体：' + safe(createdAgent.agent_name).trim() : '',
        ].filter((item) => !!item);
        sessionMeta.textContent = segments.join(' · ');
      } else {
        sessionMeta.textContent = safe(createdAgent.agent_name).trim()
          ? '已完成，角色工作区：' + safe(createdAgent.agent_name).trim()
          : '当前角色创建已完成';
      }
    }
    if (composerMeta) {
      const count = Array.isArray(state.tcRoleCreationDraftAttachments) ? state.tcRoleCreationDraftAttachments.length : 0;
      if (processing.active) {
        composerMeta.textContent = processing.unhandledCount > 0
          ? (processing.text + ' · 当前累计待处理 ' + String(processing.unhandledCount) + ' 条，可继续追加消息')
          : (processing.text + ' · 可继续追加消息');
      } else if (processing.failed && processing.unhandledCount > 0) {
        composerMeta.textContent = '上一轮处理失败，继续发送会自动重试未处理消息';
      } else {
        composerMeta.textContent = count > 0
          ? '当前消息已挂载 ' + String(count) + ' 张图片'
          : '同一条消息可同时发送图片和文字';
      }
    }
    const canStart = !!profile.can_start
      && safe(session.status).trim().toLowerCase() === 'draft'
      && state.agentSearchRootReady
      && !processing.active
      && processing.unhandledCount <= 0;
    const canComplete = roleCreationCanComplete(roleCreationCurrentDetail())
      && state.agentSearchRootReady
      && !processing.active
      && processing.unhandledCount <= 0;
    if (startBtn) startBtn.disabled = !canStart;
    if (completeBtn) completeBtn.disabled = !canComplete;
    const inputLocked = !safe(session.session_id).trim() || safe(session.status).trim().toLowerCase() === 'completed' || !state.agentSearchRootReady;
    if (input) input.disabled = inputLocked;
    if (sendBtn) sendBtn.disabled = inputLocked;
    if (pickImageBtn) pickImageBtn.disabled = inputLocked;
  }

  function roleCreationListHtml(value, emptyText) {
    const rows = Array.isArray(value)
      ? value
        .map((item) => {
          if (item && typeof item === 'object') {
            return safe(item.file_name || item.name || item.attachment_id).trim();
          }
          return safe(item).trim();
        })
        .filter((item) => !!item)
      : [];
    if (!rows.length) {
      return "<div class='rc-profile-empty'>" + roleCreationEscapeHtml(emptyText) + '</div>';
    }
    return "<ul class='rc-profile-list'>" + rows.map((item) => '<li>' + roleCreationEscapeHtml(item) + '</li>').join('') + '</ul>';
  }

  function renderRoleCreationProfile() {
    const box = $('rcProfileView');
    if (!box) return;
    const detail = roleCreationCurrentDetail();
    const session = detail.session && typeof detail.session === 'object' ? detail.session : {};
    const profile = roleCreationCurrentProfile();
    const createdAgent = roleCreationCurrentCreatedAgent();
    const dialogueAgent = roleCreationCurrentDialogueAgent();
    if (!safe(session.session_id).trim()) {
      box.innerHTML = "<div class='rc-empty'>先创建或选择一个草稿，角色画像会在这里持续收口。</div>";
      return;
    }
    const sections = [];
    const addText = (label, text, emptyText) => {
      sections.push(
        "<section class='rc-profile-card'>" +
          "<div class='rc-profile-k'>" + roleCreationEscapeHtml(label) + '</div>' +
          "<div class='rc-profile-v'>" + roleCreationEscapeHtml(safe(text).trim() || emptyText) + '</div>' +
        '</section>'
      );
    };
    const addList = (label, rows, emptyText) => {
      sections.push(
        "<section class='rc-profile-card'>" +
          "<div class='rc-profile-k'>" + roleCreationEscapeHtml(label) + '</div>' +
          "<div class='rc-profile-v'>" + roleCreationListHtml(rows, emptyText) + '</div>' +
        '</section>'
      );
    };
    addText('角色名称', profile.role_name || session.session_title || '未命名角色', '未命名角色');
    addText('角色目标', profile.role_goal, '继续通过对话补充目标和交付边界');
    addList('核心能力', profile.core_capabilities, '继续通过对话补充关键能力');
    addList('能力边界', profile.boundaries, '当前还没有明确能力边界');
    addList('适用场景', profile.applicable_scenarios, '当前还没有明确适用场景');
    addText('协作方式', profile.collaboration_style, '当前还没有明确协作方式');
    addList('示例资产', profile.example_assets, '当前还没有提交示例资产');
    addList('缺失信息', profile.missing_labels, '当前草稿已满足开工条件');
    addText('对话分析师', dialogueAgent.agent_name, '当前未解析到对话分析师');
    addText('对话工作区', dialogueAgent.workspace_path, '当前未解析到对话工作区');
    addText('对话 Provider', dialogueAgent.provider, 'codex');
    addText('工作区路径', createdAgent.workspace_path, safe(session.created_agent_workspace_path).trim() || '启动创建后会自动生成工作区');
    addText('运行态', createdAgent.runtime_status_text || '', safe(createdAgent.runtime_status).trim() || 'idle');
    box.innerHTML = sections.join('');
  }

  function roleCreationTaskCardHtml(task, stageKey) {
    const item = task && typeof task === 'object' ? task : {};
    const tone = roleCreationStatusTone(item.status);
    return (
      "<button class='rc-task-card' type='button' data-kind='task' data-stage-key='" + roleCreationEscapeHtml(stageKey) + "' data-node-id='" + roleCreationEscapeHtml(safe(item.node_id).trim()) + "'>" +
        "<div class='rc-task-card-head'>" +
          "<div class='rc-task-card-title'>" + roleCreationEscapeHtml(safe(item.task_name).trim() || '未命名任务') + '</div>' +
          "<span class='rc-chip " + tone + "'>" + roleCreationEscapeHtml(safe(item.status_text).trim() || safe(item.status).trim() || '待开始') + '</span>' +
        '</div>' +
        "<div class='rc-task-card-ref'>task_id: " + roleCreationEscapeHtml(safe(item.node_id).trim() || '-') + '</div>' +
        (
          safe(item.expected_artifact).trim()
            ? "<div class='rc-task-card-sub'>产物: " + roleCreationEscapeHtml(safe(item.expected_artifact).trim()) + '</div>'
            : ''
        ) +
      '</button>'
    );
  }

  function roleCreationArchivePocketHtml(stage) {
    const item = stage && typeof stage === 'object' ? stage : {};
    const count = Number(item.archive_count || 0);
    if (!count) return '';
    return (
      "<button class='archive-pocket' type='button' data-kind='archive' data-stage-key='" + roleCreationEscapeHtml(safe(item.stage_key).trim()) + "'>" +
        "<div class='task-title'>废案收纳</div>" +
        "<div class='task-ref'>已收口 " + roleCreationEscapeHtml(String(count)) + ' 个任务</div>' +
      '</button>'
    );
  }

  function roleCreationStageCardHtml(stage) {
    const item = stage && typeof stage === 'object' ? stage : {};
    const session = roleCreationCurrentSession();
    const sessionStatus = safe(session.status).trim().toLowerCase();
    const action = item.analyst_action && typeof item.analyst_action === 'object' ? item.analyst_action : {};
    const activeTasks = Array.isArray(item.active_tasks) ? item.active_tasks : [];
    const canSwitch = sessionStatus === 'creating' &&
      safe(item.stage_key).trim() !== 'workspace_init' &&
      safe(item.stage_key).trim() !== 'complete_creation' &&
      safe(item.stage_key).trim() !== safe(session.current_stage_key).trim();
    return (
      "<section class='process-row " + roleCreationEscapeHtml(safe(item.state).trim().toLowerCase()) + "'>" +
        "<div class='rc-stage-gutter'>" +
          "<span class='rc-stage-dot'></span>" +
          "<span class='rc-stage-line'></span>" +
        '</div>' +
        "<div class='rc-stage-main'>" +
          "<div class='rc-stage-head'>" +
            "<div class='rc-stage-title-wrap'>" +
              "<div class='rc-stage-title'>" + roleCreationEscapeHtml(safe(item.title).trim() || '未命名阶段') + '</div>' +
              "<div class='rc-stage-sub'>阶段 " + roleCreationEscapeHtml(String(item.stage_index || '')) + '</div>' +
            '</div>' +
            "<span class='rc-chip " + roleCreationStatusTone(item.state) + "'>" + roleCreationEscapeHtml(roleCreationStageStateText(item.state)) + '</span>' +
          '</div>' +
          "<div class='rc-analyst-card'>" +
            "<div class='rc-analyst-title'>" + roleCreationEscapeHtml(safe(action.title).trim() || '阶段动作') + '</div>' +
            "<div class='rc-analyst-desc'>" + roleCreationEscapeHtml(safe(action.description).trim() || '') + '</div>' +
            (
              safe(item.stage_key).trim() === 'workspace_init'
                ? "<div class='rc-analyst-meta'>初始化结果：" + roleCreationEscapeHtml(safe(item.workspace_init && item.workspace_init.status_text).trim() || '待执行') + (
                  safe(item.workspace_init && item.workspace_init.evidence_ref).trim()
                    ? ' · ' + roleCreationEscapeHtml(safe(item.workspace_init && item.workspace_init.evidence_ref).trim())
                    : ''
                ) + '</div>'
                : ''
            ) +
            (
              safe(action.next_hint).trim()
                ? "<div class='rc-analyst-meta'>" + roleCreationEscapeHtml(safe(action.next_hint).trim()) + '</div>'
                : ''
            ) +
            (
              canSwitch
                ? "<div class='rc-analyst-actions'><button class='alt rc-stage-switch-btn' type='button' data-rc-stage-key='" + roleCreationEscapeHtml(safe(item.stage_key).trim()) + "'>切到此阶段</button></div>"
                : ''
            ) +
          '</div>' +
          (
            activeTasks.length || Number(item.archive_count || 0)
              ? "<div class='rc-task-lane'>" +
                activeTasks.map((task) => roleCreationTaskCardHtml(task, safe(item.stage_key).trim())).join('') +
                roleCreationArchivePocketHtml(item) +
                '</div>'
              : "<div class='rc-stage-empty'>当前阶段还没有挂接真实任务。</div>"
          ) +
        '</div>' +
      '</section>'
      );
    }

  function roleCreationTaskPreviewPayload() {
    const preview = state.tcRoleCreationTaskPreview && typeof state.tcRoleCreationTaskPreview === 'object'
      ? state.tcRoleCreationTaskPreview
      : {};
    const kind = safe(preview.kind).trim();
    if (!kind) return null;
    const detail = roleCreationCurrentDetail();
    const stageKey = safe(preview.stage_key).trim();
    const stages = Array.isArray(detail.stages) ? detail.stages : [];
    const stage = stages.find((item) => safe(item && item.stage_key).trim() === stageKey) || {};
    if (kind === 'archive') {
      return {
        kind: 'archive',
        ticket_id: safe(detail && detail.stage_meta && detail.stage_meta.ticket_id).trim() || safe(roleCreationCurrentSession().assignment_ticket_id).trim(),
        stage_key: stageKey,
        stage_title: safe(stage.title).trim(),
        items: Array.isArray(stage.archived_tasks) ? stage.archived_tasks : [],
      };
    }
    const nodeId = safe(preview.node_id).trim();
    const items = Array.isArray(stage.active_tasks) ? stage.active_tasks : [];
    const task = items.find((item) => safe(item && item.node_id).trim() === nodeId) || {};
    return {
      kind: 'task',
      ticket_id: safe(task.ticket_id).trim() || safe(detail && detail.stage_meta && detail.stage_meta.ticket_id).trim() || safe(roleCreationCurrentSession().assignment_ticket_id).trim(),
      task: task,
    };
  }

  function roleCreationTaskFloatHtml() {
    const payload = roleCreationTaskPreviewPayload();
    if (!payload) return '';
    if (payload.kind === 'archive') {
      const items = Array.isArray(payload.items) ? payload.items : [];
      return (
        "<div class='rc-float-head'>" +
          "<div class='rc-float-title'>废案收纳 · " + roleCreationEscapeHtml(payload.stage_title || payload.stage_key) + '</div>' +
          "<span class='rc-chip archive'>已归档</span>" +
        '</div>' +
        (
          items.length
            ? "<div class='rc-float-list'>" +
              items.map((item) => (
                "<div class='rc-float-list-item'>" +
                  "<div class='rc-float-list-title'>" + roleCreationEscapeHtml(safe(item && item.task_name).trim() || safe(item && item.node_id).trim()) + '</div>' +
                  "<div class='rc-float-list-sub'>task_id: " + roleCreationEscapeHtml(safe(item && item.node_id).trim() || '-') + '</div>' +
                  (
                    safe(item && item.close_reason).trim()
                      ? "<div class='rc-float-list-sub'>关闭原因: " + roleCreationEscapeHtml(safe(item && item.close_reason).trim()) + '</div>'
                      : ''
                  ) +
                  "<div class='rc-float-actions'>" +
                    "<button class='alt' type='button' data-rc-open-task-center='1' data-node-id='" + roleCreationEscapeHtml(safe(item && item.node_id).trim()) + "'>去任务中心查看</button>" +
                  '</div>' +
                '</div>'
              )).join('') +
              '</div>'
            : "<div class='rc-float-empty'>当前阶段还没有废案记录。</div>"
        )
      );
    }
    const task = payload.task && typeof payload.task === 'object' ? payload.task : {};
    const canArchive = safe(task.relation_state).trim().toLowerCase() !== 'archived' &&
      safe(task.status).trim().toLowerCase() !== 'running';
    return (
      "<div class='rc-float-head'>" +
        "<div class='rc-float-title'>" + roleCreationEscapeHtml(safe(task.task_name).trim() || '未命名任务') + '</div>' +
        "<span class='rc-chip " + roleCreationStatusTone(task.status) + "'>" + roleCreationEscapeHtml(safe(task.status_text).trim() || safe(task.status).trim() || '待开始') + '</span>' +
      '</div>' +
      "<div class='task-hover-float-meta'>task_id: " + roleCreationEscapeHtml(safe(task.node_id).trim() || '-') + '</div>' +
      (
        safe(task.expected_artifact).trim()
          ? "<div class='rc-float-line'>产物: " + roleCreationEscapeHtml(safe(task.expected_artifact).trim()) + '</div>'
          : ''
      ) +
      (
        safe(task.node_goal).trim()
          ? "<div class='rc-float-line'>目标: " + roleCreationEscapeHtml(safe(task.node_goal).trim()) + '</div>'
          : ''
      ) +
      (
        Array.isArray(task.upstream_labels) && task.upstream_labels.length
          ? "<div class='rc-float-line'>上游: " + roleCreationEscapeHtml(task.upstream_labels.join(' / ')) + '</div>'
          : ''
      ) +
      (
        Array.isArray(task.downstream_labels) && task.downstream_labels.length
          ? "<div class='rc-float-line'>下游: " + roleCreationEscapeHtml(task.downstream_labels.join(' / ')) + '</div>'
          : ''
      ) +
      (
        safe(task.close_reason).trim()
          ? "<div class='rc-float-line'>关闭原因: " + roleCreationEscapeHtml(safe(task.close_reason).trim()) + '</div>'
          : ''
      ) +
      "<div class='rc-float-actions'>" +
        "<button class='alt' type='button' data-rc-open-task-center='1' data-node-id='" + roleCreationEscapeHtml(safe(task.node_id).trim()) + "'>去任务中心查看</button>" +
        (
          canArchive
            ? "<button class='alt' type='button' data-rc-archive-task='1' data-node-id='" + roleCreationEscapeHtml(safe(task.node_id).trim()) + "'>收口到废案</button>"
            : ''
        ) +
      '</div>'
    );
  }

  function clearRoleCreationTaskPreview() {
    state.tcRoleCreationTaskPreview = {
      kind: '',
      stage_key: '',
      node_id: '',
      pinned: false,
      anchor_rect: null,
    };
    renderRoleCreationTaskPreview();
  }

  function renderRoleCreationTaskPreview() {
    const node = $('rcTaskHoverFloat');
    if (!node) return;
    const preview = state.tcRoleCreationTaskPreview && typeof state.tcRoleCreationTaskPreview === 'object'
      ? state.tcRoleCreationTaskPreview
      : {};
    if (!safe(preview.kind).trim() || safe(state.tcModule).trim() !== 'create-role') {
      node.classList.remove('visible');
      node.setAttribute('aria-hidden', 'true');
      node.style.left = '-9999px';
      node.style.top = '-9999px';
      node.innerHTML = '';
      return;
    }
    node.innerHTML = roleCreationTaskFloatHtml();
    node.classList.add('visible');
    node.setAttribute('aria-hidden', 'false');
    const anchorRect = preview.anchor_rect;
    if (!anchorRect) return;
    window.requestAnimationFrame(() => {
      const rect = node.getBoundingClientRect();
      let left = Number(anchorRect.right || 0) + 12;
      if (left + rect.width > window.innerWidth - 12) {
        left = Math.max(12, Number(anchorRect.left || 0) - rect.width - 12);
      }
      let top = Number(anchorRect.top || 0);
      if (top + rect.height > window.innerHeight - 12) {
        top = Math.max(12, window.innerHeight - rect.height - 12);
      }
      node.style.left = String(Math.round(left)) + 'px';
      node.style.top = String(Math.round(top)) + 'px';
    });
  }

  function showRoleCreationTaskPreviewFromNode(targetNode, options) {
    const node = targetNode instanceof Element ? targetNode : null;
    if (!node) return;
    const rect = node.getBoundingClientRect();
    state.tcRoleCreationTaskPreview = {
      kind: safe(node.getAttribute('data-kind')).trim(),
      stage_key: safe(node.getAttribute('data-stage-key')).trim(),
      node_id: safe(node.getAttribute('data-node-id')).trim(),
      pinned: !!(options && options.pinned),
      anchor_rect: rect,
    };
    renderRoleCreationTaskPreview();
  }

  function bindRoleCreationTaskPreviewTargets() {
    const root = $('rcStageFlow');
    if (!root) return;
    root.querySelectorAll('.rc-task-card, .archive-pocket').forEach((node) => {
      node.onmouseenter = () => {
        if (state.tcRoleCreationTaskPreview && state.tcRoleCreationTaskPreview.pinned) {
          return;
        }
        showRoleCreationTaskPreviewFromNode(node, { pinned: false });
      };
      node.onmouseleave = () => {
        window.setTimeout(() => {
          const floatNode = $('rcTaskHoverFloat');
          if (state.tcRoleCreationTaskPreview && state.tcRoleCreationTaskPreview.pinned) {
            return;
          }
          if (floatNode && floatNode.matches(':hover')) {
            return;
          }
          clearRoleCreationTaskPreview();
        }, 120);
      };
      node.onclick = () => {
        const sameTask = state.tcRoleCreationTaskPreview &&
          safe(state.tcRoleCreationTaskPreview.kind).trim() === safe(node.getAttribute('data-kind')).trim() &&
          safe(state.tcRoleCreationTaskPreview.stage_key).trim() === safe(node.getAttribute('data-stage-key')).trim() &&
          safe(state.tcRoleCreationTaskPreview.node_id).trim() === safe(node.getAttribute('data-node-id')).trim();
        if (sameTask && state.tcRoleCreationTaskPreview.pinned) {
          clearRoleCreationTaskPreview();
          return;
        }
        showRoleCreationTaskPreviewFromNode(node, { pinned: true });
      };
    });
  }

  function renderRoleCreationEvolution() {
    const box = $('rcStageFlow');
    if (!box) return;
    const session = roleCreationCurrentSession();
    const stages = roleCreationCurrentStages();
    if (!safe(session.session_id).trim()) {
      box.innerHTML = "<div class='rc-empty'>选择草稿后，这里会展示统一的阶段与任务演进图。</div>";
      return;
    }
    box.innerHTML = stages.map((stage) => roleCreationStageCardHtml(stage)).join('');
    bindRoleCreationTaskPreviewTargets();
  }

  function renderRoleCreationWorkbench() {
    const workbench = $('rcWorkbench');
    if (!workbench) return;
    workbench.classList.toggle('draft-collapsed', !!state.tcRoleCreationDraftCollapsed);
    const collapseBtn = $('rcDraftCollapseBtn');
    const collapsedBody = $('rcDraftCollapsedBody');
    if (collapseBtn) {
      collapseBtn.setAttribute('aria-expanded', state.tcRoleCreationDraftCollapsed ? 'false' : 'true');
      collapseBtn.innerHTML = state.tcRoleCreationDraftCollapsed ? '<span aria-hidden="true">›</span>' : '<span aria-hidden="true">‹</span>';
    }
    if (collapsedBody) {
      collapsedBody.hidden = !state.tcRoleCreationDraftCollapsed;
    }
    renderRoleCreationSessionList();
    renderRoleCreationDraftAttachments();
    renderRoleCreationMessages();
    renderRoleCreationProfile();
    renderRoleCreationEvolution();
    renderRoleCreationMeta();
    setRoleCreationDetailTab(state.tcRoleCreationDetailTab);
    setRoleCreationError(state.tcRoleCreationError);
    renderRoleCreationTaskPreview();
  }

  function roleCreationOpenTaskCenter(ticketId, nodeId) {
    const ticket = safe(ticketId).trim();
    const taskId = safe(nodeId).trim();
    if (!ticket) return;
    state.assignmentSelectedTicketId = ticket;
    if (taskId) {
      state.assignmentSelectedNodeId = taskId;
    }
    switchTab('task-center');
    refreshAssignmentGraphData({ ticketId: ticket })
      .then(() => {
        if (taskId) {
          return refreshAssignmentDetail(taskId);
        }
        return null;
      })
      .catch((err) => {
        setAssignmentError(err.message || String(err));
      });
  }

  function removeRoleCreationDraftAttachment(attachmentId) {
    const targetId = safe(attachmentId).trim();
    if (!targetId) return;
    state.tcRoleCreationDraftAttachments = (Array.isArray(state.tcRoleCreationDraftAttachments) ? state.tcRoleCreationDraftAttachments : [])
      .filter((item) => safe(item && item.attachment_id).trim() !== targetId);
    renderRoleCreationDraftAttachments();
    renderRoleCreationMeta();
  }

  function roleCreationAttachmentId() {
    return 'rca-' + String(Date.now()) + '-' + String(Math.floor(Math.random() * 100000));
  }

  function readRoleCreationFileAsDataUrl(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(safe(reader.result));
      reader.onerror = () => reject(new Error('图片读取失败'));
      reader.readAsDataURL(file);
    });
  }

  async function normalizeRoleCreationAttachmentFile(file) {
    const item = file || {};
    const contentType = safe(item.type).trim().toLowerCase();
    const fileName = safe(item.name).trim() || 'image';
    const sizeBytes = Number(item.size || 0);
    if (!['image/png', 'image/jpeg', 'image/webp', 'image/gif'].includes(contentType)) {
      throw new Error('当前仅支持 png/jpg/webp/gif 图片');
    }
    if (sizeBytes > 4 * 1024 * 1024) {
      throw new Error('单张图片不能超过 4MB');
    }
    const dataUrl = await readRoleCreationFileAsDataUrl(item);
    return {
      attachment_id: roleCreationAttachmentId(),
      kind: 'image',
      file_name: fileName,
      content_type: contentType,
      size_bytes: sizeBytes,
      data_url: safe(dataUrl).trim(),
    };
  }

  async function appendRoleCreationDraftFiles(fileList) {
    const files = Array.from(fileList || []).filter((item) => !!item);
    if (!files.length) return [];
    const existing = Array.isArray(state.tcRoleCreationDraftAttachments) ? state.tcRoleCreationDraftAttachments.slice() : [];
    const remaining = Math.max(0, 6 - existing.length);
    if (!remaining) {
      throw new Error('单条消息最多携带 6 张图片');
    }
    const accepted = files.slice(0, remaining);
    const next = [];
    for (const file of accepted) {
      next.push(await normalizeRoleCreationAttachmentFile(file));
    }
    state.tcRoleCreationDraftAttachments = existing.concat(next);
    renderRoleCreationDraftAttachments();
    renderRoleCreationMeta();
    return next;
  }

  function bindRoleCreationEvents() {
    if (bindRoleCreationEvents._bound) return;
    bindRoleCreationEvents._bound = true;
    let dragDepth = 0;
    const draftBox = $('rcDraftFiles');
    const sessionList = $('rcSessionList');
    const composerBox = $('rcComposerBox');
    const dropHint = $('rcDropHint');
    const stageFlow = $('rcStageFlow');
    const taskFloat = $('rcTaskHoverFloat');
    $('rcNewSessionBtn').onclick = async () => {
      try {
        await withButtonLock('rcNewSessionBtn', async () => {
          await createRoleCreationSession();
        });
      } catch (err) {
        setRoleCreationError(err.message || String(err));
      }
    };
    $('rcStartSessionBtn').onclick = async () => {
      try {
        await withButtonLock('rcStartSessionBtn', async () => {
          await startRoleCreationSelectedSession();
        });
      } catch (err) {
        setRoleCreationError(err.message || String(err));
      }
    };
    $('rcCompleteSessionBtn').onclick = async () => {
      try {
        await withButtonLock('rcCompleteSessionBtn', async () => {
          await completeRoleCreationSelectedSession();
        });
      } catch (err) {
        setRoleCreationError(err.message || String(err));
      }
    };
    $('rcSendBtn').onclick = async () => {
      try {
        await postRoleCreationMessage();
      } catch (err) {
        setRoleCreationError(err.message || String(err));
      }
    };
    $('rcPickImageBtn').onclick = () => {
      if ($('rcImageInput')) $('rcImageInput').click();
    };
    $('rcImageInput').addEventListener('change', async (event) => {
      try {
        await appendRoleCreationDraftFiles(event.target && event.target.files ? event.target.files : []);
        setRoleCreationError('');
      } catch (err) {
        setRoleCreationError(err.message || String(err));
      } finally {
        if ($('rcImageInput')) $('rcImageInput').value = '';
      }
    });
    $('rcInput').addEventListener('keydown', (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        if ($('rcSendBtn') && !$('rcSendBtn').disabled) $('rcSendBtn').click();
      }
    });
    $('rcInput').addEventListener('paste', async (event) => {
      const clipboard = event.clipboardData;
      if (!clipboard || !clipboard.items || !clipboard.items.length) return;
      const files = [];
      Array.from(clipboard.items).forEach((item) => {
        if (item && item.kind === 'file') {
          const file = item.getAsFile();
          if (file) files.push(file);
        }
      });
      if (!files.length) return;
      event.preventDefault();
      try {
        await appendRoleCreationDraftFiles(files);
        setRoleCreationError('');
      } catch (err) {
        setRoleCreationError(err.message || String(err));
      }
    });
    ['dragenter', 'dragover'].forEach((type) => {
      composerBox.addEventListener(type, (event) => {
        event.preventDefault();
        dragDepth += 1;
        composerBox.classList.add('dragging');
        if (dropHint) dropHint.hidden = false;
      });
    });
    ['dragleave', 'drop'].forEach((type) => {
      composerBox.addEventListener(type, (event) => {
        event.preventDefault();
        dragDepth = Math.max(0, dragDepth - 1);
        if (!dragDepth || type === 'drop') {
          composerBox.classList.remove('dragging');
          if (dropHint) dropHint.hidden = true;
          dragDepth = 0;
        }
      });
    });
    composerBox.addEventListener('drop', async (event) => {
      const files = event.dataTransfer && event.dataTransfer.files ? event.dataTransfer.files : [];
      try {
        await appendRoleCreationDraftFiles(files);
        setRoleCreationError('');
      } catch (err) {
        setRoleCreationError(err.message || String(err));
      }
    });
    $('rcDraftCollapseBtn').onclick = () => {
      state.tcRoleCreationDraftCollapsed = !state.tcRoleCreationDraftCollapsed;
      renderRoleCreationWorkbench();
    };
    $('rcDetailTabEvolution').onclick = () => {
      setRoleCreationDetailTab('evolution');
    };
    $('rcDetailTabProfile').onclick = () => {
      setRoleCreationDetailTab('profile');
    };
    if (draftBox) {
      draftBox.onclick = (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;
        const removeBtn = target.closest('.rc-draft-file-remove');
        if (!removeBtn) return;
        event.preventDefault();
        removeRoleCreationDraftAttachment(removeBtn.getAttribute('data-attachment-id'));
      };
    }
    if (sessionList) {
      sessionList.onclick = (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;
        const deleteBtn = target.closest('[data-rc-delete-session]');
        if (deleteBtn) {
          event.preventDefault();
          event.stopPropagation();
          deleteRoleCreationSession(deleteBtn.getAttribute('data-rc-delete-session')).catch((err) => {
            setRoleCreationError(err.message || String(err));
          });
          return;
        }
        const sessionBtn = target.closest('.rc-session-card-main');
        if (!sessionBtn) return;
        event.preventDefault();
        const sessionId = safe(sessionBtn.getAttribute('data-session-id')).trim();
        if (!sessionId) return;
        selectRoleCreationSession(sessionId).catch((err) => {
          setRoleCreationError(err.message || String(err));
        });
      };
    }
    if (stageFlow) {
      stageFlow.onclick = (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;
        const stageBtn = target.closest('.rc-stage-switch-btn');
        if (!stageBtn) return;
        event.preventDefault();
        const stageKey = safe(stageBtn.getAttribute('data-rc-stage-key')).trim();
        if (!stageKey) return;
        updateRoleCreationStage(stageKey).catch((err) => {
          setRoleCreationError(err.message || String(err));
        });
      };
      stageFlow.addEventListener('scroll', () => {
        if (!state.tcRoleCreationTaskPreview || !state.tcRoleCreationTaskPreview.pinned) {
          clearRoleCreationTaskPreview();
        }
      });
    }
    if (taskFloat) {
      taskFloat.onclick = (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;
        const openBtn = target.closest('[data-rc-open-task-center]');
        if (openBtn) {
          event.preventDefault();
          event.stopPropagation();
          const payload = roleCreationTaskPreviewPayload();
          const ticketId = safe(payload && payload.ticket_id).trim();
          const nodeId = safe(openBtn.getAttribute('data-node-id')).trim();
          roleCreationOpenTaskCenter(ticketId, nodeId);
          return;
        }
        const archiveBtn = target.closest('[data-rc-archive-task]');
        if (archiveBtn) {
          event.preventDefault();
          event.stopPropagation();
          archiveRoleCreationTask(archiveBtn.getAttribute('data-node-id')).catch((err) => {
            setRoleCreationError(err.message || String(err));
          });
        }
      };
      taskFloat.addEventListener('mouseleave', () => {
        window.setTimeout(() => {
          if (state.tcRoleCreationTaskPreview && state.tcRoleCreationTaskPreview.pinned) {
            return;
          }
          if (taskFloat.matches(':hover')) {
            return;
          }
          clearRoleCreationTaskPreview();
        }, 120);
      });
    }
    document.addEventListener('click', (event) => {
      const target = event.target;
      if (!(target instanceof Element)) return;
      if (target.closest('.rc-task-card, .archive-pocket, #rcTaskHoverFloat')) return;
      if (state.tcRoleCreationTaskPreview && state.tcRoleCreationTaskPreview.pinned) {
        clearRoleCreationTaskPreview();
      }
    });
    window.addEventListener('resize', () => {
      if (state.tcRoleCreationTaskPreview && safe(state.tcRoleCreationTaskPreview.kind).trim()) {
        renderRoleCreationTaskPreview();
      }
    });
  }

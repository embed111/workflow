  // Training center role creation view/rendering helpers.
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
    const allRows = Array.isArray(state.tcRoleCreationSessions) ? state.tcRoleCreationSessions : [];
    const rows = roleCreationFilteredSessions();
    if (!allRows.length) {
      box.innerHTML = "<div class='rc-empty'>当前还没有创建草稿。</div>";
      return;
    }
    if (!rows.length) {
      box.innerHTML = "<div class='rc-empty'>没有匹配的草稿，试试调整搜索词或状态筛选。</div>";
      return;
    }
    box.innerHTML = rows.map((session) => {
      const sessionId = safe(session && session.session_id).trim();
      const current = sessionId && sessionId === safe(state.tcRoleCreationSelectedSessionId).trim();
      const missing = Array.isArray(session && session.missing_fields) ? session.missing_fields.length : 0;
      const status = safe(session && session.status).trim().toLowerCase();
      const processing = roleCreationSessionProcessingInfo(session);
      const canDelete = !!(session && session.delete_available) && !processing.active;
      const deleteLabel = safe(session && session.delete_label).trim()
        || (status === 'completed' ? '删除记录' : status === 'creating' ? '清理删除' : '删除草稿');
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
              ? "<div class='rc-session-card-actions'><button class='bad rc-session-card-delete' type='button' data-rc-delete-session='" + roleCreationEscapeHtml(sessionId) + "'>" + roleCreationEscapeHtml(deleteLabel) + '</button></div>'
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
    const detail = roleCreationCurrentDetail();
    const profile = roleCreationCurrentProfile();
    const createdAgent = roleCreationCurrentCreatedAgent();
    const dialogueAgent = roleCreationCurrentDialogueAgent();
    const processing = roleCreationCurrentProcessingInfo();
    const mainGraphTicketId = roleCreationMainGraphTicketId(session, detail);
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
    const totalSessionCount = Array.isArray(state.tcRoleCreationSessions) ? state.tcRoleCreationSessions.length : 0;
    const filteredSessionCount = roleCreationFilteredSessions().length;
    const statusFilter = normalizeRoleCreationStatusFilter(state.tcRoleCreationStatusFilter);
    const searchQuery = safe(state.tcRoleCreationQuery).trim();
    if (draftMeta) {
      draftMeta.textContent = state.agentSearchRootReady
        ? (
          totalSessionCount <= 0
            ? '新建后通过对话逐步收口角色画像'
            : (
              searchQuery || statusFilter !== 'all'
                ? ('共 ' + String(totalSessionCount) + ' 条，当前显示 ' + String(filteredSessionCount) + ' 条 · ' + (statusFilter === 'all' ? '全部状态' : roleCreationSessionStatusText(statusFilter)))
                : ('共 ' + String(totalSessionCount) + ' 条草稿，可按名称、预览、任务图快速搜索')
            )
        )
        : '根路径未就绪，创建角色功能已锁定';
    }
    if (collapsedCount) {
      collapsedCount.textContent = String(searchQuery || statusFilter !== 'all' ? filteredSessionCount : totalSessionCount);
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
          mainGraphTicketId ? '主图：' + mainGraphTicketId : '',
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

  function roleCreationProfileHasValue(value) {
    if (Array.isArray(value)) {
      return value.some((item) => {
        if (item && typeof item === 'object') {
          return !!safe(item.file_name || item.name || item.attachment_id).trim();
        }
        return !!safe(item).trim();
      });
    }
    return !!safe(value).trim();
  }

  function roleCreationProfileChipHtml(tone, text) {
    return "<span class='rc-chip " + roleCreationEscapeHtml(tone) + "'>" + roleCreationEscapeHtml(text) + '</span>';
  }

  function roleCreationProfileStageLine(session, detail) {
    const currentTitle = safe(session.current_stage_title || (detail.stage_meta && detail.stage_meta.current_stage_title)).trim();
    const currentIndex = Number(session.current_stage_index || (detail.stage_meta && detail.stage_meta.current_stage_index) || 1) || 1;
    if (!currentTitle) {
      return '初始化工作区 · 1 / 6';
    }
    return currentTitle + ' · ' + String(Math.max(1, currentIndex)) + ' / 6';
  }

  function roleCreationProfileDraftStatus(session, profile, processing) {
    const status = safe(session.status).trim().toLowerCase();
    const missingLabels = Array.isArray(profile.missing_labels) ? profile.missing_labels.filter((item) => !!safe(item).trim()) : [];
    if (status === 'completed') {
      return { chipTone: 'done', chipText: '已完成', text: '已完成创建，画像收口结果已落到角色工作区。' };
    }
    if (status === 'creating') {
      return { chipTone: 'active', chipText: '创建中', text: '已开始创建，当前按真实任务和阶段推进。' };
    }
    if (processing && processing.failed) {
      return { chipTone: 'danger', chipText: '待重试', text: '最近一轮分析失败，仍需继续对齐草稿字段。' };
    }
    if ((processing && processing.active) || missingLabels.length) {
      return { chipTone: 'pending', chipText: '待对齐', text: '待对齐，尚未收口。' };
    }
    return { chipTone: 'done', chipText: '已收口', text: '当前草稿字段已收口，可进入开始前确认。' };
  }

  function roleCreationProfileStartStatus(session, profile) {
    const status = safe(session.status).trim().toLowerCase();
    const missingLabels = Array.isArray(profile.missing_labels) ? profile.missing_labels.filter((item) => !!safe(item).trim()) : [];
    if (status === 'completed') {
      return { chipTone: 'done', chipText: '已完成创建', text: '角色已经完成创建，可继续进入训练和发布治理。' };
    }
    if (status === 'creating') {
      return { chipTone: 'active', chipText: '已开始创建', text: '已点击开始创建，真实任务已映射到任务中心主图，工作区也已建立。' };
    }
    if (profile.can_start) {
      return { chipTone: 'active', chipText: '可开始未开始', text: '最小字段已满足，但尚未真正开始创建。' };
    }
    return {
      chipTone: 'pending',
      chipText: '未达开始门槛',
      text: missingLabels.length
        ? ('仍需补齐：' + missingLabels.join(' / '))
        : '仍需补齐角色名、角色目标和至少一条核心能力后才能开始。',
    };
  }

  function roleCreationProfileTaskStatus(session, detail) {
    const ticketId = roleCreationMainGraphTicketId(session, detail);
    if (!ticketId) {
      return { chipTone: 'pending', chipText: '当前未映射主图', text: '--', ticketId: '' };
    }
    return { chipTone: 'active', chipText: '已映射主图', text: ticketId, ticketId: ticketId };
  }

  function roleCreationProfileAttachmentSummary(profile) {
    const assets = Array.isArray(profile.example_assets) ? profile.example_assets : [];
    const count = assets.filter((item) => {
      if (item && typeof item === 'object') {
        return !!safe(item.file_name || item.name || item.attachment_id).trim();
      }
      return !!safe(item).trim();
    }).length;
    if (count <= 0) {
      return '当前暂无附件引用。';
    }
    return String(count) + ' 项附件/引用，仅用于字段对齐，不直接写进角色正文。';
  }

  function roleCreationFieldStateConfig(fieldKey, profile) {
    const missingFields = Array.isArray(profile.missing_fields)
      ? profile.missing_fields.map((item) => safe(item).trim()).filter(Boolean)
      : [];
    const has = (value) => roleCreationProfileHasValue(value);
    const isMissing = missingFields.includes(fieldKey);
    if (fieldKey === 'example_assets') {
      return has(profile.example_assets)
        ? { tone: 'active', text: '仅作参考', action: '轻量引用' }
        : { tone: 'pending', text: '暂无附件', action: '可继续补充' };
    }
    if (fieldKey === 'role_name') {
      return has(profile.role_name)
        ? { tone: 'done', text: '已确认', action: '直接沿用' }
        : { tone: 'pending', text: '待补充', action: '继续补齐' };
    }
    if (fieldKey === 'role_goal') {
      return isMissing || !has(profile.role_goal)
        ? { tone: 'pending', text: '待修正', action: '继续收口' }
        : { tone: 'done', text: '已确认', action: '保持当前稿' };
    }
    if (fieldKey === 'core_capabilities') {
      return isMissing || !has(profile.core_capabilities)
        ? { tone: 'pending', text: '待补充', action: '继续补齐' }
        : { tone: 'done', text: '已确认', action: '保留当前稿' };
    }
    if (fieldKey === 'boundaries') {
      return isMissing || !has(profile.boundaries)
        ? { tone: 'pending', text: '待补充', action: '补一条即可' }
        : { tone: 'done', text: '已确认', action: '继续微调' };
    }
    if (fieldKey === 'collaboration_style') {
      return isMissing || !has(profile.collaboration_style)
        ? { tone: 'pending', text: '待确认', action: '二选一' }
        : { tone: 'done', text: '已确认', action: '保持当前稿' };
    }
    return { tone: 'pending', text: '待补充', action: '继续收口' };
  }

  function roleCreationProfileTextBody(text, emptyText) {
    const content = safe(text).trim();
    if (!content) {
      return "<div class='rc-profile-empty'>" + roleCreationEscapeHtml(emptyText) + '</div>';
    }
    return "<div class='rc-field-note'>" + roleCreationEscapeHtml(content) + '</div>';
  }

  function roleCreationProfileSectionHtml(title, bodyHtml, options) {
    const opts = options && typeof options === 'object' ? options : {};
    const chip = opts.chip && typeof opts.chip === 'object' ? opts.chip : {};
    const actionText = safe(opts.action).trim();
    const sectionKind = safe(opts.kind).trim() || 'field';
    return (
      "<section class='rc-profile-card' data-rc-profile-kind='" + roleCreationEscapeHtml(sectionKind) + "' data-rc-profile-title='" + roleCreationEscapeHtml(title) + "'>" +
        "<div class='rc-field-head'>" +
          "<div class='rc-field-title-row'>" +
            "<div class='rc-profile-section-title'>" + roleCreationEscapeHtml(title) + '</div>' +
            roleCreationProfileChipHtml(safe(chip.tone).trim() || 'pending', safe(chip.text).trim() || '待补充') +
          '</div>' +
          (
            actionText
              ? ("<div class='rc-field-actions'><span class='rc-field-action'>" + roleCreationEscapeHtml(actionText) + '</span></div>')
              : ''
          ) +
        '</div>' +
        bodyHtml +
      '</section>'
    );
  }

  function renderRoleCreationProfile() {
    const box = $('rcProfileView');
    if (!box) return;
    const detail = roleCreationCurrentDetail();
    const session = detail.session && typeof detail.session === 'object' ? detail.session : {};
    const profile = roleCreationCurrentProfile();
    const processing = roleCreationCurrentProcessingInfo();
    if (!safe(session.session_id).trim()) {
      box.innerHTML = "<div class='rc-empty'>先创建或选择一个草稿，角色画像会在这里持续收口。</div>";
      return;
    }
    const sections = [];
    const draftStatus = roleCreationProfileDraftStatus(session, profile, processing);
    const startStatus = roleCreationProfileStartStatus(session, profile);
    const taskStatus = roleCreationProfileTaskStatus(session, detail);
    const missingLabels = Array.isArray(profile.missing_labels) ? profile.missing_labels.filter((item) => !!safe(item).trim()) : [];
    sections.push(
      "<section class='rc-profile-card rc-profile-card-summary' data-rc-profile-kind='summary' data-rc-profile-title='summary'>" +
        "<div class='rc-profile-head'>" +
          "<div class='rc-profile-head-main'>" +
            "<div class='rc-profile-head-title'>" + roleCreationEscapeHtml((safe(profile.role_name).trim() || safe(session.session_title).trim() || '未命名角色') + ' 草稿') + '</div>' +
          '</div>' +
          "<div class='rc-chip-row'>" +
            roleCreationProfileChipHtml(draftStatus.chipTone, draftStatus.chipText) +
            roleCreationProfileChipHtml(startStatus.chipTone, startStatus.chipText) +
            roleCreationProfileChipHtml(taskStatus.chipTone, taskStatus.chipText) +
          '</div>' +
        '</div>' +
        "<div class='rc-profile-summary'>" +
          "<div class='rc-profile-kv'><div class='rc-profile-k'>当前阶段</div><div class='rc-profile-v'>" + roleCreationEscapeHtml(roleCreationProfileStageLine(session, detail)) + '</div></div>' +
          "<div class='rc-profile-kv'><div class='rc-profile-k'>草稿状态</div><div class='rc-profile-v'>" + roleCreationEscapeHtml(draftStatus.text) + '</div></div>' +
          "<div class='rc-profile-kv'><div class='rc-profile-k'>开始状态</div><div class='rc-profile-v'>" + roleCreationEscapeHtml(startStatus.text) + '</div></div>' +
          "<div class='rc-profile-kv'><div class='rc-profile-k'>待补字段</div><div class='rc-profile-v'>" + roleCreationEscapeHtml(missingLabels.length ? missingLabels.join(' / ') : '当前草稿已满足开工条件') + '</div></div>' +
          "<div class='rc-profile-kv'><div class='rc-profile-k'>主图</div><div class='rc-profile-v mono'>" + roleCreationEscapeHtml(taskStatus.text || '--') + '</div></div>' +
          (
            safe(taskStatus.ticketId).trim()
              ? (
                "<div class='rc-profile-kv'><div class='rc-profile-k'>任务中心</div><div class='rc-profile-v'>" +
                  "<button class='alt' type='button' data-rc-open-summary-task-center='" + roleCreationEscapeHtml(taskStatus.ticketId) + "'>打开主图定位任务</button>" +
                '</div></div>'
              )
              : ''
          ) +
          "<div class='rc-profile-kv'><div class='rc-profile-k'>附件状态</div><div class='rc-profile-v'>" + roleCreationEscapeHtml(roleCreationProfileAttachmentSummary(profile)) + '</div></div>' +
        '</div>' +
      '</section>'
    );
    sections.push(
      roleCreationProfileSectionHtml(
        '角色名',
        roleCreationProfileTextBody(profile.role_name || session.session_title || '未命名角色', '未命名角色'),
        {
          kind: 'field',
          chip: roleCreationFieldStateConfig('role_name', profile),
          action: roleCreationFieldStateConfig('role_name', profile).action,
        }
      )
    );
    sections.push(
      roleCreationProfileSectionHtml(
        '角色目标',
        roleCreationProfileTextBody(profile.role_goal, '继续通过对话补充目标和交付边界'),
        {
          kind: 'field',
          chip: roleCreationFieldStateConfig('role_goal', profile),
          action: roleCreationFieldStateConfig('role_goal', profile).action,
        }
      )
    );
    sections.push(
      roleCreationProfileSectionHtml(
        '核心能力',
        roleCreationListHtml(profile.core_capabilities, '继续通过对话补充关键能力'),
        {
          kind: 'field',
          chip: roleCreationFieldStateConfig('core_capabilities', profile),
          action: roleCreationFieldStateConfig('core_capabilities', profile).action,
        }
      )
    );
    sections.push(
      roleCreationProfileSectionHtml(
        '边界',
        roleCreationListHtml(profile.boundaries, '当前还没有明确边界，请继续补齐。'),
        {
          kind: 'field',
          chip: roleCreationFieldStateConfig('boundaries', profile),
          action: roleCreationFieldStateConfig('boundaries', profile).action,
        }
      )
    );
    sections.push(
      roleCreationProfileSectionHtml(
        '协作方式',
        roleCreationProfileTextBody(profile.collaboration_style, '当前还没有明确协作方式。'),
        {
          kind: 'field',
          chip: roleCreationFieldStateConfig('collaboration_style', profile),
          action: roleCreationFieldStateConfig('collaboration_style', profile).action,
        }
      )
    );
    sections.push(
      roleCreationProfileSectionHtml(
        '附件与引用',
        (
          "<div class='rc-field-note'>" + roleCreationEscapeHtml(roleCreationProfileAttachmentSummary(profile)) + '</div>' +
          roleCreationListHtml(profile.example_assets, '当前没有附带参考图片或引用。')
        ),
        {
          kind: 'field',
          chip: roleCreationFieldStateConfig('example_assets', profile),
          action: roleCreationFieldStateConfig('example_assets', profile).action,
        }
      )
    );
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
    const session = roleCreationCurrentSession();
    const taskCenterTicketId = roleCreationMainGraphTicketId(session, detail);
    const stageKey = safe(preview.stage_key).trim();
    const stages = Array.isArray(detail.stages) ? detail.stages : [];
    const stage = stages.find((item) => safe(item && item.stage_key).trim() === stageKey) || {};
    if (kind === 'archive') {
      return {
        kind: 'archive',
        ticket_id: taskCenterTicketId,
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
      ticket_id: taskCenterTicketId,
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
                  (
                    safe(payload.ticket_id).trim()
                      ? (
                        "<div class='rc-float-actions'>" +
                          "<button class='alt' type='button' data-rc-open-task-center='1' data-node-id='" + roleCreationEscapeHtml(safe(item && item.node_id).trim()) + "'>去任务中心查看</button>" +
                        '</div>'
                      )
                      : ''
                  ) +
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
        (
          safe(payload.ticket_id).trim()
            ? "<button class='alt' type='button' data-rc-open-task-center='1' data-node-id='" + roleCreationEscapeHtml(safe(task.node_id).trim()) + "'>去任务中心查看</button>"
            : ''
        ) +
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
    const searchInput = $('rcSessionSearchInput');
    if (collapseBtn) {
      collapseBtn.setAttribute('aria-expanded', state.tcRoleCreationDraftCollapsed ? 'false' : 'true');
      collapseBtn.innerHTML = state.tcRoleCreationDraftCollapsed ? '<span aria-hidden="true">›</span>' : '<span aria-hidden="true">‹</span>';
    }
    if (collapsedBody) {
      collapsedBody.hidden = !state.tcRoleCreationDraftCollapsed;
    }
    if (searchInput && searchInput.value !== safe(state.tcRoleCreationQuery)) {
      searchInput.value = safe(state.tcRoleCreationQuery);
    }
    Array.from(document.querySelectorAll('[data-rc-session-filter]')).forEach((node) => {
      if (!(node instanceof Element)) return;
      node.classList.toggle(
        'active',
        safe(node.getAttribute('data-rc-session-filter')).trim().toLowerCase()
          === normalizeRoleCreationStatusFilter(state.tcRoleCreationStatusFilter),
      );
    });
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
    setStatus(taskId ? '已切到任务中心主图并选中对应任务' : '已切到任务中心主图');
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
    const profileView = $('rcProfileView');
    const sessionList = $('rcSessionList');
    const sessionSearchInput = $('rcSessionSearchInput');
    const sessionFilterRow = $('rcSessionFilterRow');
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
    if (sessionSearchInput) {
      sessionSearchInput.addEventListener('input', () => {
        state.tcRoleCreationQuery = safe(sessionSearchInput.value);
        renderRoleCreationWorkbench();
      });
      sessionSearchInput.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && safe(sessionSearchInput.value).trim()) {
          event.preventDefault();
          sessionSearchInput.value = '';
          state.tcRoleCreationQuery = '';
          renderRoleCreationWorkbench();
        }
      });
    }
    if (sessionFilterRow) {
      sessionFilterRow.onclick = (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;
        const filterBtn = target.closest('[data-rc-session-filter]');
        if (!filterBtn) return;
        event.preventDefault();
        state.tcRoleCreationStatusFilter = normalizeRoleCreationStatusFilter(
          filterBtn.getAttribute('data-rc-session-filter'),
        );
        renderRoleCreationWorkbench();
      };
    }
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
    if (profileView) {
      profileView.onclick = (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;
        const openBtn = target.closest('[data-rc-open-summary-task-center]');
        if (!openBtn) return;
        event.preventDefault();
        roleCreationOpenTaskCenter(openBtn.getAttribute('data-rc-open-summary-task-center'), '');
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

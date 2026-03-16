  function runtimePhaseInfo(value) {
    const key = safe(value).toLowerCase();
    const map = {
      sent: { label: '已发送', icon: 'sent', tone: 'running' },
      pending: { label: '已发送', icon: 'sent', tone: 'running' },
      queued: { label: '已发送', icon: 'sent', tone: 'running' },
      running: { label: '正在生成', icon: 'running', tone: 'running', spinning: true },
      generating: { label: '正在生成', icon: 'running', tone: 'running', spinning: true },
      done: { label: '完成', icon: 'success', tone: 'success' },
      success: { label: '完成', icon: 'success', tone: 'success' },
      failed: { label: '失败', icon: 'failed', tone: 'failed' },
      interrupted: { label: '已中断', icon: 'interrupted', tone: 'failed' },
    };
    return map[key] || { label: safe(value) || '未知', icon: 'running', tone: 'running' };
  }

  function normalizeRuntimePhase(value) {
    const key = safe(value).toLowerCase();
    if (key === 'running' || key === 'generating') return 'generating';
    if (key === 'success' || key === 'done') return 'done';
    if (key === 'failed') return 'failed';
    if (key === 'interrupted') return 'interrupted';
    if (key === 'queued' || key === 'pending' || key === 'sent') return 'sent';
    return 'sent';
  }

  function analysisBadgeInfo(value) {
    const done = safe(value) === '已分析';
    return {
      text: done ? '已分析' : '未分析',
      className: done ? 'analysis-badge done' : 'analysis-badge pending',
      icon: done ? 'success' : 'pending',
    };
  }

  function workflowAnalysisBadgeInfo(row) {
    const unanalyzed = Math.max(0, Number((row && row.unanalyzed_message_count) || 0));
    const analyzed = Math.max(0, Number((row && row.analyzed_message_count) || 0));
    if (unanalyzed > 0) {
      return {
        text: '未分析 ' + unanalyzed,
        className: 'analysis-badge pending',
        icon: 'pending',
      };
    }
    if (analyzed > 0) {
      return {
        text: '已分析',
        className: 'analysis-badge done',
        icon: 'success',
      };
    }
    return {
      text: '未分析',
      className: 'analysis-badge pending',
      icon: 'pending',
    };
  }

  function stageText(stage, payload) {
    const key = safe(stage).toLowerCase();
    const step = safe(payload && payload.step).toLowerCase();
    if (key === 'assignment') return '指派分析师';
    if (key === 'analysis' && step === 'collect_context') return '收集上下文';
    if (key === 'analysis' && step === 'summarize') return '生成分析摘要';
    if (key === 'analysis') return '执行分析';
    if (key === 'plan') return '生成计划';
    if (key === 'select') return '选择执行项';
    if (key === 'train') return '执行训练';
    return safe(stage) || '未知阶段';
  }

  function nextStepHint(stage, status) {
    const stageKey = safe(stage).toLowerCase();
    const statusKey = safe(status).toLowerCase();
    if (statusKey === 'failed' || statusKey === 'interrupted') {
      return '当前阶段失败，建议先展开时间线查看失败原因和调试数据，再决定重试。';
    }
    if (statusKey === 'running' || statusKey === 'pending' || statusKey === 'queued') {
      return '当前正在执行中，可展开时间线查看实时进展。';
    }
    if (stageKey === 'assignment') return '下一步通常是执行分析。';
    if (stageKey === 'analysis') return '下一步通常是生成训练计划。';
    if (stageKey === 'plan') return '下一步通常是选择执行项并执行训练。';
    if (stageKey === 'select') return '下一步通常是执行训练。';
    if (stageKey === 'train') return '训练完成后可回看结果并决定是否继续补充样本。';
    return '可展开时间线详情查看完整过程。';
  }

  function eventTone(status) {
    const key = safe(status).toLowerCase();
    if (key === 'success' || key === 'done') return 'success';
    if (key === 'failed' || key === 'interrupted') return 'failed';
    if (key === 'running' || key === 'pending' || key === 'queued') return 'running';
    if (key === 'skipped') return 'skipped';
    return 'running';
  }

  function eventToneInfo(status) {
    const tone = eventTone(status);
    const map = {
      success: { label: '成功', icon: 'success', className: 'tone-success' },
      running: { label: '进行中', icon: 'running', className: 'tone-running', spinning: true },
      failed: { label: '失败', icon: 'failed', className: 'tone-failed' },
      skipped: { label: '跳过', icon: 'skipped', className: 'tone-skipped' },
    };
    return map[tone] || map.running;
  }

  function workflowEventDebugKey(workflowId, eventId) {
    return safe(workflowId) + ':' + safe(eventId || 0);
  }

  function isWorkflowAnalysisSelectable(row) {
    return !!(row && row.analysis_selectable);
  }

  function normalizeTaskRunRow(row) {
    const item = row || {};
    const command = Array.isArray(item.command)
      ? item.command.map((v) => safe(v))
      : [];
    return {
      task_id: safe(item.task_id),
      session_id: safe(item.session_id),
      agent_name: safe(item.agent_name),
      status: safe(item.status),
      summary: safe(item.summary),
      created_at: safe(item.created_at),
      start_at: safe(item.start_at),
      end_at: safe(item.end_at),
      duration_ms: Number(item.duration_ms || 0),
      command: command,
      trace_available: !!item.trace_available,
    };
  }

  function upsertSessionTaskRun(sessionId, row) {
    const sid = safe(sessionId);
    if (!sid) return;
    const item = normalizeTaskRunRow(row);
    const taskId = safe(item.task_id);
    if (!taskId) return;
    if (!Array.isArray(state.sessionTaskRuns[sid])) {
      state.sessionTaskRuns[sid] = [];
    }
    const list = state.sessionTaskRuns[sid];
    const idx = list.findIndex((it) => safe(it.task_id) === taskId);
    if (idx >= 0) {
      list[idx] = Object.assign({}, list[idx], item);
    } else {
      list.push(item);
    }
    list.sort((a, b) => safe(a.created_at).localeCompare(safe(b.created_at)));
  }

  function linkSessionMessagesToTasks(sessionId) {
    const session = state.sessionsById[sessionId];
    if (!session || !Array.isArray(session.messages)) return;
    const runs = Array.isArray(state.sessionTaskRuns[sessionId]) ? state.sessionTaskRuns[sessionId] : [];
    const successRuns = runs.filter((row) => safe(row.status).toLowerCase() === 'success');
    let runIndex = 0;
    for (const msg of session.messages) {
      if (safe(msg.role) !== 'assistant') continue;
      if (safe(msg.task_id)) continue;
      if (runIndex >= successRuns.length) break;
      msg.task_id = safe(successRuns[runIndex].task_id);
      runIndex += 1;
    }
  }

  function formatJsonLines(value) {
    try {
      return JSON.stringify(value || {}, null, 2);
    } catch (_) {
      return safe(value);
    }
  }

  async function withButtonLock(buttonId, task) {
    const btn = $(buttonId);
    const old = btn ? btn.disabled : false;
    if (btn) btn.disabled = true;
    try {
      return await task();
    } finally {
      if (btn) btn.disabled = old;
    }
  }

  function batchProgressText() {
    const run = state.batchRun || {};
    if (!run.running) {
      return '分析任务空闲';
    }
    return (
      '处理中[' +
      safe(run.action || '-') +
      '] ' +
      safe(run.done || 0) +
      '/' +
      safe(run.total || 0) +
      '，成功=' +
      safe(run.success || 0) +
      '，失败=' +
      safe(run.failed || 0) +
      '，跳过=' +
      safe(run.skipped || 0)
    );
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function isCompactLayout() {
    return window.matchMedia('(max-width:1080px)').matches;
  }

  function readLayoutValue(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      const value = Number(raw);
      if (Number.isFinite(value) && value > 0) {
        return value;
      }
      return fallback;
    } catch (_) {
      return fallback;
    }
  }

  function writeLayoutValue(key, value) {
    try {
      localStorage.setItem(key, String(Math.round(value)));
    } catch (_) {
      // ignore localStorage errors
    }
  }

  function setCssWidth(cssVar, value) {
    document.documentElement.style.setProperty(cssVar, Math.round(value) + 'px');
  }

  function resetCssWidth(cssVar) {
    document.documentElement.style.removeProperty(cssVar);
  }

  function applySavedLayout() {
    if (isCompactLayout()) {
      resetCssWidth('--rail-width');
      resetCssWidth('--chat-left-width');
      resetCssWidth('--train-left-width');
      resetCssWidth('--train-right-width');
      return;
    }
    setCssWidth('--rail-width', clamp(readLayoutValue(layoutKeys.rail, 248), 220, 420));
    setCssWidth('--chat-left-width', clamp(readLayoutValue(layoutKeys.chatLeft, 340), 280, 560));
    setCssWidth('--train-left-width', clamp(readLayoutValue(layoutKeys.trainLeft, 360), 300, 620));
    setCssWidth('--train-right-width', clamp(readLayoutValue(layoutKeys.trainRight, 420), 320, 680));
  }

  function bindSplitter(config) {
    const splitter = $(config.splitterId);
    const container = $(config.containerId);
    if (!splitter || !container) return;

    splitter.ondblclick = () => {
      setCssWidth(config.cssVar, config.defaultValue);
      writeLayoutValue(config.storageKey, config.defaultValue);
    };

    splitter.addEventListener('pointerdown', (event) => {
      if (isCompactLayout()) return;
      event.preventDefault();
      const startX = event.clientX;
      const computed = getComputedStyle(document.documentElement).getPropertyValue(config.cssVar);
      const startValue = Number.parseInt(computed, 10) || config.defaultValue;
      document.body.classList.add('is-resizing');
      splitter.classList.add('is-active');
      splitter.setPointerCapture(event.pointerId);

      function onMove(moveEvent) {
        const dx = moveEvent.clientX - startX;
        const delta = config.direction === 'right' ? -dx : dx;
        const rect = container.getBoundingClientRect();
        let maxAllowed = config.max;
        if (Number.isFinite(config.minOther) && config.minOther > 0) {
          maxAllowed = Math.min(maxAllowed, Math.max(config.min, rect.width - config.minOther - 10));
        }
        const next = clamp(startValue + delta, config.min, maxAllowed);
        setCssWidth(config.cssVar, next);
        writeLayoutValue(config.storageKey, next);
      }

      function onStop() {
        document.body.classList.remove('is-resizing');
        splitter.classList.remove('is-active');
        window.removeEventListener('pointermove', onMove);
        window.removeEventListener('pointerup', onStop);
        window.removeEventListener('pointercancel', onStop);
      }

      window.addEventListener('pointermove', onMove);
      window.addEventListener('pointerup', onStop);
      window.addEventListener('pointercancel', onStop);
    });
  }

  function initSplitters() {
    applySavedLayout();
    bindSplitter({
      splitterId: 'appSplitter',
      containerId: 'appRoot',
      cssVar: '--rail-width',
      storageKey: layoutKeys.rail,
      defaultValue: 248,
      min: 220,
      max: 420,
      minOther: 760,
      direction: 'left',
    });
    bindSplitter({
      splitterId: 'chatSplitter',
      containerId: 'chatWrap',
      cssVar: '--chat-left-width',
      storageKey: layoutKeys.chatLeft,
      defaultValue: 340,
      min: 280,
      max: 560,
      minOther: 420,
      direction: 'left',
    });
    bindSplitter({
      splitterId: 'trainSplitter',
      containerId: 'trainWrap',
      cssVar: '--train-left-width',
      storageKey: layoutKeys.trainLeft,
      defaultValue: 360,
      min: 300,
      max: 620,
      minOther: 520,
      direction: 'left',
    });
    bindSplitter({
      splitterId: 'trainDetailSplitter',
      containerId: 'trainMain',
      cssVar: '--train-right-width',
      storageKey: layoutKeys.trainRight,
      defaultValue: 420,
      min: 320,
      max: 680,
      minOther: 360,
      direction: 'right',
    });
    window.addEventListener('resize', () => {
      if (!isCompactLayout()) {
        applySavedLayout();
      }
    });
  }

  async function requestJSON(url, options) {
    const resp = await fetch(url, options || {});
    let data = {};
    try {
      data = await resp.json();
    } catch (_) {
      data = {};
    }
    if (!resp.ok || !data.ok) {
      const code = safe(data.code).toLowerCase();
      if (code === 'agent_search_root_not_set') {
        state.agentSearchRootReady = false;
        state.agentSearchRootError = code;
        const input = $('agentSearchRoot');
        if (input && Object.prototype.hasOwnProperty.call(data || {}, 'agent_search_root')) {
          input.value = safe(data.agent_search_root);
        }
        applyGateState();
      }
      const error = new Error(data.error || data.code || ('请求失败: ' + url));
      error.status = resp.status;
      error.code = safe(data.code);
      error.data = data || {};
      throw error;
    }
    return data;
  }

  async function getJSON(url) {
    return requestJSON(url);
  }

  async function postJSON(url, body) {
    return requestJSON(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body || {}),
    });
  }

  async function deleteJSON(url, body) {
    const options = {
      method: 'DELETE',
    };
    if (body && typeof body === 'object') {
      options.headers = { 'Content-Type': 'application/json' };
      options.body = JSON.stringify(body);
    }
    return requestJSON(url, options);
  }

  function includeTestDataQueryValue() {
    return state.showTestData ? '1' : '0';
  }

  function withTestDataQuery(url) {
    const join = url.includes('?') ? '&' : '?';
    return url + join + 'include_test_data=' + includeTestDataQueryValue();
  }

  function cleanupLegacyShowSystemAgentsCache() {
    try {
      localStorage.removeItem(showSystemAgentsLegacyCacheKey);
    } catch (_) {
      // ignore storage errors
    }
  }

  function updateShowTestDataMeta() {
    const node = $('showTestDataMeta');
    if (!node) return;
    node.textContent = state.showTestData ? '当前显示测试数据' : '已隐藏测试数据';
  }

  function updateManualPolicyInputMeta() {
    const node = $('allowManualPolicyInputMeta');
    if (!node) return;
    const enabled = !!state.allowManualPolicyInput;
    const stats = state.policyClosureStats && typeof state.policyClosureStats === 'object' ? state.policyClosureStats : {};
    const alertOn = !!stats.manual_fallback_usage_alert;
    const rate = Number(stats.manual_fallback_rate_pct || 0);
    const suffix = alertOn ? '（兜底触发率偏高: ' + String(rate) + '%）' : '';
    node.textContent = (enabled ? '默认开启' : '已关闭') + suffix;
  }

  function updateArtifactRootMeta() {
    const pathInput = $('artifactRootPathInput');
    const pathValue = safe(state.artifactRootPath).trim();
    if (pathInput && document.activeElement !== pathInput) {
      pathInput.value = pathValue;
    }
    const workspaceNode = $('artifactWorkspacePath');
    if (workspaceNode) {
      workspaceNode.textContent = safe(state.artifactWorkspaceRoot).trim() || '-';
    }
    const statusNode = $('artifactRootStatusMeta');
    if (statusNode) {
      const status = safe(state.artifactRootValidationStatus).trim().toLowerCase();
      statusNode.textContent = status === 'ok' ? '路径校验通过，当前生效' : (status || '未校验');
    }
  }

  function normalizePathToken(value) {
    return safe(value).toLowerCase().replace(/\\/g, '/');
  }

  function isSystemOrTestAgent(item) {
    const path = normalizePathToken((item && item.agents_md_path) || '');
    if (!path) return false;
    const rootNode = $('agentSearchRoot');
    const currentRoot = normalizePathToken(rootNode ? rootNode.value : '');
    const rootIsTestRuntime =
      currentRoot.includes('/state/test-runtime/') ||
      currentRoot.includes('/.test/');
    if (rootIsTestRuntime && path.startsWith(currentRoot)) {
      return false;
    }
    return (
      path.includes('/workflow/state/') ||
      path.includes('/workflow/.runtime/') ||
      path.includes('/state/test-runtime/') ||
      path.includes('/test-runtime/') ||
      path.includes('/.test/') ||
      path.includes('/.runtime/')
    );
  }

  function visibleAgents() {
    if (state.showTestData) return [...(state.agents || [])];
    return (state.agents || []).filter((item) => !isSystemOrTestAgent(item));
  }

  function parseStatusText(value) {
    const key = safe(value).trim().toLowerCase();
    const map = {
      ok: '完整',
      incomplete: '不完整',
      failed: '失败',
      pending: '未分析',
      '': '未分析',
    };
    return map[key] || key || '-';
  }

  function parseWarningLabel(value) {
    const key = safe(value).trim();
    const map = {
      agents_md_empty: 'AGENTS.md 为空',
      missing_role_section: '未识别到角色章节',
      missing_goal_section: '未识别到目标章节',
      goal_inferred_from_role_profile: '目标由角色内容推断',
      missing_duty_section: '未识别到职责章节',
      empty_duty_constraints: '职责章节缺少清晰条目',
      missing_required_policy_fields: '关键字段不足',
      constraints_missing: '职责边界缺失',
      constraints_evidence_missing: '职责边界存在无证据条目',
      constraints_conflict: '职责边界存在冲突',
      target_agents_path_out_of_scope: '目标 AGENTS.md 超出当前根路径作用域',
      workspace_root_missing_workflow_subdir: '根路径缺少 workflow/ 子目录',
      codex_output_invalid_json: 'Codex 输出不符合 JSON 契约',
      contract_parse_status_invalid: 'parse_status 不在契约允许值',
      contract_clarity_score_invalid: 'clarity_score 不符合契约',
      contract_clarity_gate_invalid: 'clarity_gate 不符合契约',
    };
    return map[key] || key;
  }

  function clarityGateText(value) {
    const key = safe(value).trim().toLowerCase();
    const map = {
      auto: '自动生效',
      confirm: '需确认',
      block: '阻断',
    };
    return map[key] || key || '-';
  }

  function clarityGateReasonText(value) {
    const key = safe(value).trim().toLowerCase();
    const map = {
      role_goal_duty_complete: '角色/目标/职责完整，允许自动生效',
      extraction_incomplete: '提取不完整，需人工确认',
      extraction_failed: '提取失败，已阻断',
      clarity_score_below_auto_threshold: '清晰度低于自动阈值，需人工确认',
      clarity_score_below_confirm_threshold: '清晰度低于确认阈值，已阻断',
      policy_field_validation_failed: '关键字段校验失败，已阻断',
      policy_section_conflict: '章节内容冲突，需人工确认或阻断',
      parse_failed: '策略提取失败，已阻断',
      parse_incomplete: '策略提取不完整，需人工确认',
      score_below_60: '评分低于 60，已阻断',
      score_60_79: '评分在 60~79，需人工确认',
      score_evidence_insufficient: '评分证据不足，需人工确认',
      constraints_missing: '职责边界缺失，需人工确认',
      constraints_evidence_missing: '职责边界存在无证据条目，需人工确认',
      constraints_conflict: '职责边界冲突，需人工确认',
    };
    return map[key] || safe(value);
  }

  function selectedAgent() {
    return safe($('agentSelect').value).trim();
  }

  function selectedAgentItem() {
    const name = selectedAgent();
    if (!name) return null;
    return state.agents.find((item) => safe(item.agent_name) === name) || null;
  }

  function mergeAgentItemByName(agentName, patch) {
    const name = safe(agentName).trim();
    if (!name || !patch || typeof patch !== 'object') return;
    const idx = state.agents.findIndex((item) => safe(item && item.agent_name).trim() === name);
    if (idx < 0) return;
    state.agents[idx] = Object.assign({}, state.agents[idx], patch);
    const chain =
      patch.analysis_chain && typeof patch.analysis_chain === 'object'
        ? patch.analysis_chain
        : {};
    if (chain.ui_progress && typeof chain.ui_progress === 'object') {
      setAgentPolicyProgressSnapshot(name, chain.ui_progress);
    }
  }

  function normalizeAgentNameKey(value) {
    return safe(value).trim();
  }

  function defaultAgentPolicyAnalysisRecord() {
    return {
      status: 'unanalyzed',
      gate: '',
      reason: '',
      cacheLine: '',
      analyzing: false,
      requires_manual: false,
    };
  }

  function buildPolicyCacheLineFromItem(item) {
    const node = item && typeof item === 'object' ? item : {};
    const cacheStatus = safe(node.policy_cache_status).trim().toLowerCase();
    const cacheReason = cacheReasonText(node.policy_cache_reason);
    const cachedAt = safe(node.policy_cache_cached_at).trim();
    let head = '待分析';
    if (cacheStatus === 'hit' || node.policy_cache_hit) {
      head = '命中';
    } else if (cacheStatus === 'recomputed') {
      head = '已重算';
    } else if (cacheStatus === 'stale') {
      head = '缓存失效';
    } else if (cacheStatus === 'disabled') {
      head = '缓存未启用';
    } else if (cacheStatus === 'pending') {
      head = '待检查';
    }
    return (
      '缓存: ' +
      head +
      (cacheReason ? '（' + cacheReason + '）' : '') +
      (cachedAt ? ' · cached_at=' + cachedAt : '')
    );
  }

  function hasPolicyGateFields(item) {
    const node = item && typeof item === 'object' ? item : {};
    const parseStatus = safe(node.parse_status).trim().toLowerCase();
    const clarityGate = safe(node.clarity_gate).trim().toLowerCase();
    return (
      parseStatus === 'ok' ||
      parseStatus === 'incomplete' ||
      parseStatus === 'failed' ||
      clarityGate === 'auto' ||
      clarityGate === 'confirm' ||
      clarityGate === 'block'
    );
  }

  function parsePolicyCacheReasonCodes(raw) {
    const text = safe(raw).trim().toLowerCase();
    if (!text) return [];
    const parts = text.split(/[,;\s]+/);
    const out = [];
    const seen = new Set();
    for (const part of parts) {
      const code = safe(part).trim().toLowerCase();
      if (!code || seen.has(code)) continue;
      seen.add(code);
      out.push(code);
    }
    return out;
  }

  function isAgentPolicyReanalyzeRequired(cacheStatus, reasonCodes) {
    const status = safe(cacheStatus).trim().toLowerCase();
    const codes = Array.isArray(reasonCodes) ? reasonCodes : [];
    if (status === 'cleared' || status === 'stale') return true;
    if (codes.includes('manual_clear')) return true;
    const forceCodes = new Set([
      'agents_hash_mismatch',
      'cached_before_agents_mtime',
      'cached_at_missing',
      'agents_mtime_missing',
      'cache_payload_invalid_json',
      'cache_payload_incomplete',
      'cache_parse_status_missing',
      'cache_clarity_score_invalid',
      'cache_prompt_version_mismatch',
      'cache_extract_source_mismatch',
      'cache_write_failed',
    ]);
    return codes.some((code) => forceCodes.has(code));
  }

  function buildAgentAnalysisRecordFromItem(item) {
    const node = item && typeof item === 'object' ? item : {};
    const cacheStatus = safe(node.policy_cache_status).trim().toLowerCase();
    const reasonCodes = parsePolicyCacheReasonCodes(node.policy_cache_reason);
    if (cacheStatus === 'cleared' || reasonCodes.includes('manual_clear')) {
      return {
        status: 'unanalyzed',
        gate: '',
        reason: '',
        cacheLine: '',
        analyzing: false,
        requires_manual: true,
      };
    }
    if (isAgentPolicyReanalyzeRequired(cacheStatus, reasonCodes)) {
      const staleByAgents =
        reasonCodes.includes('agents_hash_mismatch') ||
        reasonCodes.includes('cached_before_agents_mtime');
      return {
        status: 'unanalyzed',
        gate: '',
        reason: staleByAgents
          ? '检测到 AGENTS.md 已更新，需重新分析后才能对话。'
          : '角色缓存已过期或无效，需重新分析后才能对话。',
        cacheLine: buildPolicyCacheLineFromItem(node),
        analyzing: false,
        requires_manual: false,
      };
    }
    if (!hasPolicyGateFields(node)) {
      return defaultAgentPolicyAnalysisRecord();
    }
    const derived = derivePolicyGateFromAgent(node);
    return {
      status: 'analyzed',
      gate: safe(derived.gate),
      reason: safe(derived.reason),
      cacheLine: buildPolicyCacheLineFromItem(node),
      analyzing: false,
      requires_manual: false,
    };
  }

  function syncAgentPolicyAnalysisCache(options) {
    const opts = options && typeof options === 'object' ? options : {};
    const resetAll = !!opts.resetAll;
    const next = {};
    for (const item of state.agents || []) {
      const key = normalizeAgentNameKey(item && item.agent_name);
      if (!key) continue;
      const fromItem = buildAgentAnalysisRecordFromItem(item);
      const existing = state.agentPolicyAnalysisByName[key];
      if (resetAll || !existing || typeof existing !== 'object') {
        next[key] = fromItem;
        continue;
      }
      // Item-derived stale/cleared state has higher priority and must invalidate local cache.
      if (fromItem.requires_manual || safe(fromItem.status).trim().toLowerCase() !== 'analyzed') {
        next[key] = fromItem;
        continue;
      }
      // Keep local "analyzing" status while async analyze call is in flight.
      if (existing.analyzing) {
        next[key] = Object.assign({}, existing);
        continue;
      }
      // If local record is not analyzed but server has analyzed state, promote to server-derived state.
      if (safe(existing.status).trim().toLowerCase() !== 'analyzed') {
        next[key] = fromItem;
        continue;
      }
      // Preserve local analyzed state (e.g. policy_confirmed) when server item is also analyzed.
      next[key] = Object.assign({}, existing);
    }
    state.agentPolicyAnalysisByName = next;
  }

  function getAgentPolicyAnalysisRecord(agentName) {
    const key = normalizeAgentNameKey(agentName);
    if (!key) return defaultAgentPolicyAnalysisRecord();
    const existing = state.agentPolicyAnalysisByName[key];
    if (existing && typeof existing === 'object') return existing;
    const created = defaultAgentPolicyAnalysisRecord();
    state.agentPolicyAnalysisByName[key] = created;
    return created;
  }

  function setAgentPolicyAnalysisRecord(agentName, patch) {
    const key = normalizeAgentNameKey(agentName);
    if (!key) return;
    const next = Object.assign({}, getAgentPolicyAnalysisRecord(key), patch || {});
    state.agentPolicyAnalysisByName[key] = next;
  }

  function isPolicyAnalysisCompletedGate(gateValue) {
    const gate = safe(gateValue).trim().toLowerCase();
    return (
      gate === 'policy_ready' ||
      gate === 'policy_confirmed' ||
      gate === 'policy_needs_confirm' ||
      gate === 'policy_failed'
    );
  }

  function resolveAgentPolicyGateInfo(agentName) {
    const name = safe(agentName).trim();
    if (!name) {
      return {
        agent_name: '',
        gate: 'idle_unselected',
        analysis_completed: false,
        reason: '会话未绑定有效 agent，禁止发送新对话内容。',
      };
    }
    const item = state.agents.find((node) => safe(node && node.agent_name).trim() === name) || null;
    if (item) {
      const cacheStatus = safe(item.policy_cache_status).trim().toLowerCase();
      const reasonCodes = parsePolicyCacheReasonCodes(item.policy_cache_reason);
      if (cacheStatus === 'cleared' || reasonCodes.includes('manual_clear')) {
        return {
          agent_name: name,
          gate: 'policy_cache_missing',
          analysis_completed: false,
          reason: '会话 agent 角色缓存为空，请先生成缓存并完成分析。',
        };
      }
      if (isAgentPolicyReanalyzeRequired(cacheStatus, reasonCodes)) {
        const staleByAgents =
          reasonCodes.includes('agents_hash_mismatch') ||
          reasonCodes.includes('cached_before_agents_mtime');
        return {
          agent_name: name,
          gate: 'policy_cache_stale',
          analysis_completed: false,
          reason: staleByAgents
            ? '检测到 AGENTS.md 已更新，需重新分析后才能对话。请点击“生成缓存”。'
            : '角色缓存已过期或无效，需重新分析后才能对话。请点击“生成缓存”。',
        };
      }
    }
    const record = getAgentPolicyAnalysisRecord(name);
    if (record && record.requires_manual) {
      return {
        agent_name: name,
        gate: 'policy_cache_missing',
        analysis_completed: false,
        reason: '会话 agent 角色缓存为空，请先生成缓存并完成分析。',
      };
    }
    if (record && record.analyzing) {
      return {
        agent_name: name,
        gate: 'analyzing_policy',
        analysis_completed: false,
        reason: '会话 agent 角色分析中，请稍候。',
      };
    }
    if (record && safe(record.status).trim().toLowerCase() === 'analyzed') {
      const gate = safe(record.gate).trim().toLowerCase() || 'policy_failed';
      return {
        agent_name: name,
        gate: gate,
        analysis_completed: isPolicyAnalysisCompletedGate(gate),
        reason: safe(record.reason).trim() || '会话 agent 角色分析已完成。',
      };
    }
    if (item && hasPolicyGateFields(item)) {
      const derived = derivePolicyGateFromAgent(item);
      const gate = safe(derived.gate).trim().toLowerCase() || 'policy_failed';
      return {
        agent_name: name,
        gate: gate,
        analysis_completed: isPolicyAnalysisCompletedGate(gate),
        reason: safe(derived.reason).trim() || '会话 agent 角色分析已完成。',
      };
    }
    return {
      agent_name: name,
      gate: 'idle_unselected',
      analysis_completed: false,
      reason: '会话 agent 角色尚未完成分析，请先完成分析后再发送。',
    };
  }

  function resolveSessionPolicyGateInfo(session) {
    const node = session && typeof session === 'object' ? session : {};
    const info = resolveAgentPolicyGateInfo(node.agent_name);
    const sessionHash = safe(node.agents_hash).trim();
    const item = state.agents.find((it) => safe(it && it.agent_name).trim() === safe(node.agent_name).trim()) || null;
    const latestHash = safe(item && item.agents_hash).trim();
    if (!info.analysis_completed && safe(info.gate).trim().toLowerCase() === 'policy_cache_stale') {
      if (sessionHash && latestHash && sessionHash !== latestHash) {
        return Object.assign({}, info, {
          reason:
            safe(info.reason).trim() +
            ' 当前会话hash=' +
            short(sessionHash, 12) +
            '，最新hash=' +
            short(latestHash, 12) +
            '。',
        });
      }
    }
    return info;
  }

  function trySelectAgentFromSessionIfMissing(session) {
    const node = session && typeof session === 'object' ? session : {};
    const sessionAgent = safe(node.agent_name).trim();
    if (!sessionAgent) return false;
    if (selectedAgent()) return false;
    const selectNode = $('agentSelect');
    if (!selectNode) return false;
    const optionValues = Array.from(selectNode.options || []).map((opt) => safe(opt && opt.value).trim());
    if (!optionValues.includes(sessionAgent)) return false;
    selectNode.value = sessionAgent;
    localStorage.setItem(agentCacheKey, sessionAgent);
    renderAgentSelectOptions(true);
    startPolicyAnalysisForSelection();
    return true;
  }

  function setAgentPolicyProgressSnapshot(agentName, rawSnapshot) {
    const key = normalizeAgentNameKey(agentName);
    if (!key) return;
    const normalized = normalizePolicyAnalyzeProgress(
      rawSnapshot && typeof rawSnapshot === 'object' ? rawSnapshot : {}
    );
    if (!Array.isArray(normalized.stages) || !normalized.stages.length) {
      delete state.agentPolicyProgressByName[key];
      return;
    }
    state.agentPolicyProgressByName[key] = normalized;
  }

  function getAgentPolicyProgressSnapshot(agentName) {
    const key = normalizeAgentNameKey(agentName);
    if (!key) return null;
    const snapshot = state.agentPolicyProgressByName[key];
    if (!snapshot || typeof snapshot !== 'object') return null;
    const normalized = normalizePolicyAnalyzeProgress(snapshot);
    if (!Array.isArray(normalized.stages) || !normalized.stages.length) return null;
    return normalized;
  }

  function persistPolicyProgressToAgent(agentName) {
    const name = safe(agentName).trim();
    if (!name) return;
    const snapshot = policyAnalyzeProgressSnapshot(name);
    if (!snapshot || !Array.isArray(snapshot.stages) || !snapshot.stages.length) return;
    setAgentPolicyProgressSnapshot(name, snapshot);
    const idx = state.agents.findIndex((item) => safe(item && item.agent_name).trim() === name);
    if (idx < 0) return;
    const current = state.agents[idx] && typeof state.agents[idx] === 'object' ? state.agents[idx] : {};
    const chain =
      current.analysis_chain && typeof current.analysis_chain === 'object'
        ? Object.assign({}, current.analysis_chain)
        : {};
    chain.ui_progress = snapshot;
    state.agents[idx] = Object.assign({}, current, { analysis_chain: chain });
  }

  function agentStatusInfoByRecord(record) {
    const rec = record && typeof record === 'object' ? record : defaultAgentPolicyAnalysisRecord();
    if (rec.status !== 'analyzed') {
      if (rec.requires_manual) {
        return {
          code: 'manual',
          text: '未分析',
          icon: 'cache',
          spinning: false,
          chipClass: 'pending',
        };
      }
      return {
        code: 'unanalyzed',
        text: rec.analyzing ? '未分析（分析中）' : '未分析',
        icon: 'pending',
        spinning: !!rec.analyzing,
        chipClass: 'pending',
      };
    }
    const gate = safe(rec.gate).toLowerCase();
    if (gate === 'policy_ready' || gate === 'policy_confirmed') {
      return {
        code: 'ready',
        text: '可创建',
        icon: 'success',
        spinning: false,
        chipClass: 'done',
      };
    }
    if (gate === 'policy_needs_confirm') {
      return {
        code: 'confirm',
        text: '需确认',
        icon: 'sent',
        spinning: false,
        chipClass: 'pending',
      };
    }
    return {
      code: 'blocked',
      text: '已阻断',
      icon: 'failed',
      spinning: false,
      chipClass: 'blocked',
    };
  }

  function agentStatusInfo(item) {
    const name = safe(item && item.agent_name).trim();
    return agentStatusInfoByRecord(getAgentPolicyAnalysisRecord(name));
  }

  function resetAgentDropdownPanelPosition() {
    const panel = $('agentSelectPanel');
    const options = $('agentSelectOptions');
    state.agentDropdownPanelWidth = 0;
    if (panel) {
      panel.style.position = '';
      panel.style.left = '';
      panel.style.top = '';
      panel.style.right = '';
      panel.style.bottom = '';
      panel.style.width = '';
      panel.style.maxHeight = '';
    }
    if (options) {
      options.style.maxHeight = '';
    }
  }

  function positionAgentDropdownPanel() {
    if (!state.agentDropdownOpen) return;
    const panel = $('agentSelectPanel');
    const trigger = $('agentSelectTrigger');
    const options = $('agentSelectOptions');
    if (!panel || !trigger) return;
    const rect = trigger.getBoundingClientRect();
    const viewportW = Math.max(0, Number(window.innerWidth || 0));
    const viewportH = Math.max(0, Number(window.innerHeight || 0));
    if (viewportW <= 0 || viewportH <= 0) return;
    const margin = 8;
    const gap = 6;
    const triggerWidth = Math.max(0, Math.floor(rect.width));
    const baseWidth = Math.max(1, Number(state.agentDropdownPanelWidth || triggerWidth));
    const width = Math.max(1, Math.min(baseWidth, viewportW - margin * 2));
    const maxLeft = Math.max(margin, viewportW - width - margin);
    const left = Math.min(Math.max(Math.floor(rect.left), margin), maxLeft);
    const spaceBelow = viewportH - rect.bottom - gap - margin;
    const spaceAbove = rect.top - gap - margin;
    const shouldOpenUp = spaceBelow < 180 && spaceAbove > spaceBelow;
    const panelMaxHeight = Math.max(140, Math.min(320, Math.floor(shouldOpenUp ? spaceAbove : spaceBelow)));
    const preferredOptionsMaxHeight = 34 * 5 + 4 * 4;
    const optionsMaxHeight = Math.max(64, Math.min(preferredOptionsMaxHeight, panelMaxHeight - 46));

    panel.style.position = 'fixed';
    panel.style.left = String(left) + 'px';
    panel.style.right = 'auto';
    panel.style.width = String(width) + 'px';
    panel.style.maxHeight = String(panelMaxHeight) + 'px';
    if (shouldOpenUp) {
      panel.style.top = 'auto';
      panel.style.bottom = String(Math.max(margin, Math.floor(viewportH - rect.top + gap))) + 'px';
    } else {
      panel.style.bottom = 'auto';
      panel.style.top = String(Math.max(margin, Math.floor(rect.bottom + gap))) + 'px';
    }
    if (options) {
      options.style.maxHeight = String(optionsMaxHeight) + 'px';
    }
  }

  function handleAgentDropdownViewportChange() {
    if (!state.agentDropdownOpen) return;
    positionAgentDropdownPanel();
  }

  function setAgentDropdownOpen(nextOpen) {
    const host = $('agentDropdown');
    const trigger = $('agentSelectTrigger');
    const panel = $('agentSelectPanel');
    const canOpen = !!host && !!trigger && !!panel && !trigger.disabled;
    const wasOpen = !!state.agentDropdownOpen;
    const open = !!nextOpen && canOpen;
    state.agentDropdownOpen = open;
    if (host) {
      host.classList.toggle('open', open);
    }
    if (trigger) {
      trigger.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    const search = $('agentSelectSearch');
    if (search) {
      search.disabled = !open;
      if (!open && wasOpen) {
        search.value = '';
      }
      if (open && !wasOpen) {
        window.setTimeout(() => {
          try {
            search.focus();
          } catch (_) {
            // ignore focus errors
          }
        }, 0);
      }
    }
    if (open) {
      if (!wasOpen && trigger) {

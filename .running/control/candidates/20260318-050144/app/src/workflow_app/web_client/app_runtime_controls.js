  function ensureTestDataToggleProbeOutputNode() {
    let node = $('testDataToggleProbeOutput');
    if (node) return node;
    node = document.createElement('pre');
    node.id = 'testDataToggleProbeOutput';
    node.style.display = 'none';
    document.body.appendChild(node);
    return node;
  }

  async function runTestDataToggleProbe() {
    const output = {
      ts: new Date().toISOString(),
      case: testDataToggleProbeCase(),
      pass: false,
      error: '',
      total_agents: 0,
      visible_when_off: 0,
      visible_when_on: 0,
      tc_agents_off: 0,
      tc_agents_on: 0,
      tc_queue_off: 0,
      tc_queue_on: 0,
      error_text: '',
      retry_ok: false,
      session_toggle_exists: false,
      settings_toggle_exists: false,
      dashboard_off: {},
      dashboard_on: {},
    };
    const waitMs = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms));
    try {
      const probeCase = output.case;
      const refreshAll = async () => {
        await refreshAgents(true, { autoAnalyze: false });
        await refreshSessions();
        await refreshWorkflows();
        await refreshDashboard();
        await refreshTrainingCenterAgents();
        await refreshTrainingCenterQueue(true);
      };
      if (probeCase === 'ac_td_01') {
        switchTab('chat');
        output.session_toggle_exists = !!$('showSystemAgentsCheck');
        switchTab('settings');
        output.settings_toggle_exists = !!$('showTestDataCheck');
        output.pass = !output.session_toggle_exists && output.settings_toggle_exists;
      } else if (probeCase === 'ac_td_02') {
        switchTab('settings');
        await postJSON('/api/config/show-test-data', { show_test_data: false });
        await refreshAll();
        output.server_value_after_set = !!state.showTestData;
        localStorage.setItem(showTestDataCacheKey, '1');
        await refreshAgents(true, { autoAnalyze: false });
        output.server_value_after_reload = !!state.showTestData;
        output.pass = !output.server_value_after_set && !output.server_value_after_reload;
      } else if (probeCase === 'ac_td_03') {
        switchTab('chat');
        await postJSON('/api/config/show-test-data', { show_test_data: false });
        await refreshAgents(true, { autoAnalyze: false });
        output.total_agents = Array.isArray(state.agents) ? state.agents.length : 0;
        output.visible_when_off = visibleAgents().length;
        await postJSON('/api/config/show-test-data', { show_test_data: true });
        await refreshAgents(true, { autoAnalyze: false });
        output.visible_when_on = visibleAgents().length;
        setAgentDropdownOpen(true);
        output.pass =
          output.total_agents >= output.visible_when_off &&
          output.visible_when_on >= output.visible_when_off &&
          output.visible_when_on === output.total_agents &&
          output.visible_when_on > output.visible_when_off;
      } else if (probeCase === 'ac_td_04') {
        switchTab('training');
        await postJSON('/api/config/show-test-data', { show_test_data: false });
        await refreshDashboard();
        output.dashboard_off = await getJSON('/api/dashboard');
        await postJSON('/api/config/show-test-data', { show_test_data: true });
        await refreshDashboard();
        output.dashboard_on = await getJSON('/api/dashboard');
        const changed =
          Number(output.dashboard_off.new_sessions_24h || 0) !== Number(output.dashboard_on.new_sessions_24h || 0) ||
          Number(output.dashboard_off.pending_analysis || 0) !== Number(output.dashboard_on.pending_analysis || 0) ||
          Number(output.dashboard_off.pending_training || 0) !== Number(output.dashboard_on.pending_training || 0);
        output.pass = !!changed;
      } else if (probeCase === 'ac_td_05') {
        switchTab('training-center');
        setTrainingCenterModule('ops');
        await postJSON('/api/config/show-test-data', { show_test_data: false });
        await refreshTrainingCenterAgents();
        await refreshTrainingCenterQueue(true);
        output.tc_agents_off = Array.isArray(state.tcAgents) ? state.tcAgents.length : 0;
        output.tc_queue_off = Array.isArray(state.tcQueue) ? state.tcQueue.length : 0;
        await postJSON('/api/config/show-test-data', { show_test_data: true });
        await refreshTrainingCenterAgents();
        await refreshTrainingCenterQueue(true);
        output.tc_agents_on = Array.isArray(state.tcAgents) ? state.tcAgents.length : 0;
        output.tc_queue_on = Array.isArray(state.tcQueue) ? state.tcQueue.length : 0;
        output.pass =
          output.tc_agents_on >= output.tc_agents_off &&
          output.tc_queue_on >= output.tc_queue_off &&
          (output.tc_agents_on > output.tc_agents_off || output.tc_queue_on > output.tc_queue_off);
      } else if (probeCase === 'ac_td_06') {
        switchTab('settings');
        await refreshAgents(true, { autoAnalyze: false });
        const check = $('showTestDataCheck');
        const before = !!state.showTestData;
        if (!check) throw new Error('showTestDataCheck not found');
        check.checked = !before;
        check.dispatchEvent(new Event('change', { bubbles: true }));
        await waitMs(240);
        output.before_state = before;
        output.after_state = !!state.showTestData;
        output.after_checked = !!check.checked;
        output.error_text = safe($('settingsErr') ? $('settingsErr').textContent : '').trim();
        output.pass =
          output.after_state === before &&
          output.after_checked === before &&
          !!output.error_text;
      } else if (probeCase === 'ac_td_07') {
        switchTab('settings');
        let failed = false;
        try {
          await refreshAgents(true, {
            autoAnalyze: false,
            agentsPath: '/api/agents?force_show_test_data_read_fail=1',
          });
        } catch (err) {
          failed = true;
          setSettingsError(err.message || String(err));
        }
        output.error_text = safe($('settingsErr') ? $('settingsErr').textContent : '').trim();
        await refreshAgents(true, { autoAnalyze: false });
        output.retry_ok = !!state.agentSearchRootReady;
        output.pass = failed && !!output.error_text && output.retry_ok;
      } else if (probeCase === 'ac_td_08') {
        switchTab('settings');
        await postJSON('/api/config/show-test-data', { show_test_data: false });
        await refreshAgents(true, { autoAnalyze: false });
        localStorage.setItem('workflow.p0.settings.showSystemAgents', '1');
        localStorage.setItem(showTestDataCacheKey, '1');
        await refreshAgents(true, { autoAnalyze: false });
        const legacyValue = safe(localStorage.getItem('workflow.p0.settings.showSystemAgents')).trim();
        output.legacy_key_after_refresh = legacyValue;
        output.server_state = !!state.showTestData;
        output.pass = !output.server_state && !legacyValue;
      } else {
        output.pass = true;
      }
    } catch (err) {
      output.error = safe(err && err.message ? err.message : err);
    }
    const node = ensureTestDataToggleProbeOutputNode();
    node.textContent = JSON.stringify(output);
    node.setAttribute('data-pass', output.pass ? '1' : '0');
  }

  async function bootstrap() {
    initSplitters();
    bindEvents();
    setupSessionEntryToolbarIcons();
    const deepLinkTrainingLoop = !!(
      queryParam('tc_loop_mode') ||
      queryParam('tc_loop_tab') ||
      queryParam('tc_loop_node') ||
      queryParam('tc_loop_task')
    );
    setTrainingCenterModule(deepLinkTrainingLoop ? 'ops' : 'agents');
    if (deepLinkTrainingLoop) {
      switchTab('training-center');
    }
    renderTrainingCenterAgentStats();
    renderTrainingCenterAgentList();
    renderTrainingCenterAgentDetail();
    renderTrainingCenterQueue();
    renderAssignmentCenter();
    syncTrainingCenterPlanAgentOptions();
    updateTrainingCenterSelectedMeta();
    const cachedShowTestData = localStorage.getItem(showTestDataCacheKey);
    if (cachedShowTestData === '0' || cachedShowTestData === '1') {
      state.showTestData = cachedShowTestData === '1';
    }
    cleanupLegacyShowSystemAgentsCache();
    $('showTestDataCheck').checked = state.showTestData;
    updateShowTestDataMeta();
    updateClearPolicyCacheButton();
    setWorkflowQueueMode('records');
    await refreshAgents(false);
    await refreshSessions();
    await refreshWorkflows();
    await refreshDashboard();
    await refreshRuntimeUpgradeStatus({ silent: true });
    const cachedSession = localStorage.getItem(sessionCacheKey) || '';
    if (cachedSession && state.sessionsById[cachedSession]) {
      await selectSession(cachedSession);
    } else {
      renderFeed();
    }
    applyGateState();
    startWorkflowPoller();
    startRuntimeUpgradePoller();
    setStatus(state.agentSearchRootReady ? '就绪' : '等待设置 agent路径');
    if (isLayoutProbeEnabled()) {
      await runLayoutProbe();
    }
    if (isPolicyProbeEnabled()) {
      await runPolicyProbe();
    }
    if (isTrainingCenterProbeEnabled()) {
      await runTrainingCenterProbe();
    }
    if (isAssignmentProbeEnabled()) {
      await runAssignmentCenterProbe();
    }
    if (isTestDataToggleProbeEnabled()) {
      await runTestDataToggleProbe();
    }
  }

  bootstrap().catch((err) => {
    setChatError(err.message || String(err));
    setStatus('失败');
  });
})();

  state.runtimeUpgrade = {
    environment: '',
    current_version: '',
    candidate_version: '',
    banner_visible: false,
    can_upgrade: false,
    request_pending: false,
    blocking_reason: '',
    last_action: {},
    reconnecting: false,
    status_error: '',
    refresh_busy: false,
    poller: 0,
  };

  function ensureRuntimeUpgradeBanner() {
    let node = $('runtimeUpgradeBanner');
    if (node) return node;
    node = document.createElement('section');
    node.id = 'runtimeUpgradeBanner';
    node.className = 'runtime-upgrade-banner hidden';
    document.body.appendChild(node);
    return node;
  }

  function runtimeUpgradeShouldShow() {
    const info = state.runtimeUpgrade || {};
    return safe(info.environment).trim() === 'prod' && (!!info.banner_visible || !!info.request_pending || !!info.reconnecting);
  }

  function runtimeUpgradeStatusText() {
    const info = state.runtimeUpgrade || {};
    if (info.reconnecting) {
      return '正式环境正在切换，页面会短暂刷新并自动重连。';
    }
    if (info.request_pending) {
      return safe(info.blocking_reason).trim() || '正式环境正在切换，请等待完成。';
    }
    if (safe(info.blocking_reason).trim()) {
      return safe(info.blocking_reason).trim();
    }
    return '当前无运行中任务，可升级到已通过 test 门禁的新版本。';
  }

  function runtimeUpgradeLastActionText() {
    const info = state.runtimeUpgrade || {};
    const last = info.last_action && typeof info.last_action === 'object' ? info.last_action : {};
    const status = safe(last.status).trim();
    if (!status) return '';
    const map = {
      success: '最近一次升级成功',
      switching: '正在切换正式版本',
      rollback_success: '最近一次升级失败，已自动回退',
    };
    const head = map[status] || ('最近状态：' + status);
    const finishedAt = safe(last.finished_at || last.started_at).trim();
    return finishedAt ? head + ' · ' + formatDateTime(finishedAt) : head;
  }

  function renderRuntimeUpgradeBanner() {
    const node = ensureRuntimeUpgradeBanner();
    const info = state.runtimeUpgrade || {};
    if (!runtimeUpgradeShouldShow()) {
      node.classList.add('hidden');
      node.replaceChildren();
      return;
    }
    node.classList.remove('hidden');
    const wrap = document.createElement('div');
    wrap.className = 'runtime-upgrade-shell';

    const head = document.createElement('div');
    head.className = 'runtime-upgrade-head';
    const title = document.createElement('div');
    title.className = 'runtime-upgrade-title';
    title.textContent = '正式环境可控升级';
    const meta = document.createElement('div');
    meta.className = 'runtime-upgrade-meta';
    meta.textContent =
      '当前版本 ' +
      (safe(info.current_version).trim() || '-') +
      ' -> 待升级版本 ' +
      (safe(info.candidate_version).trim() || '-');
    head.appendChild(title);
    head.appendChild(meta);

    const body = document.createElement('div');
    body.className = 'runtime-upgrade-body';
    const message = document.createElement('div');
    message.className = 'runtime-upgrade-message';
    message.textContent = runtimeUpgradeStatusText();
    body.appendChild(message);

    const lastActionText = runtimeUpgradeLastActionText();
    if (lastActionText) {
      const note = document.createElement('div');
      note.className = 'runtime-upgrade-note';
      note.textContent = lastActionText;
      body.appendChild(note);
    }
    if (safe(info.status_error).trim()) {
      const error = document.createElement('div');
      error.className = 'runtime-upgrade-note is-bad';
      error.textContent = '升级状态读取失败：' + safe(info.status_error).trim();
      body.appendChild(error);
    }

    const actions = document.createElement('div');
    actions.className = 'runtime-upgrade-actions';
    const button = document.createElement('button');
    button.id = 'runtimeUpgradeApplyBtn';
    button.type = 'button';
    button.textContent = info.reconnecting || info.request_pending ? '切换中' : '升级正式环境';
    button.disabled = !!info.reconnecting || !!info.request_pending || !info.can_upgrade;
    button.onclick = () => {
      applyRuntimeUpgrade().catch((err) => {
        state.runtimeUpgrade.status_error = safe(err && err.message ? err.message : err);
        renderRuntimeUpgradeBanner();
      });
    };
    actions.appendChild(button);
    wrap.appendChild(head);
    wrap.appendChild(body);
    wrap.appendChild(actions);
    node.replaceChildren(wrap);
  }

  function applyRuntimeUpgradeStatus(payload) {
    const data = payload && typeof payload === 'object' ? payload : {};
    state.runtimeUpgrade = Object.assign({}, state.runtimeUpgrade || {}, {
      environment: safe(data.environment).trim(),
      current_version: safe(data.current_version).trim(),
      candidate_version: safe(data.candidate_version).trim(),
      banner_visible: !!data.banner_visible,
      can_upgrade: !!data.can_upgrade,
      request_pending: !!data.request_pending,
      blocking_reason: safe(data.blocking_reason).trim(),
      last_action: data.last_action && typeof data.last_action === 'object' ? data.last_action : {},
      status_error: '',
    });
    renderRuntimeUpgradeBanner();
    return state.runtimeUpgrade;
  }

  async function refreshRuntimeUpgradeStatus(options) {
    const opts = options || {};
    if (state.runtimeUpgrade.refresh_busy) return state.runtimeUpgrade;
    state.runtimeUpgrade.refresh_busy = true;
    try {
      const data = await getJSON('/api/runtime-upgrade/status');
      return applyRuntimeUpgradeStatus(data);
    } catch (err) {
      if (!opts.silent) {
        state.runtimeUpgrade.status_error = safe(err && err.message ? err.message : err);
        renderRuntimeUpgradeBanner();
      }
      return state.runtimeUpgrade;
    } finally {
      state.runtimeUpgrade.refresh_busy = false;
    }
  }

  function stopRuntimeUpgradePoller() {
    if (state.runtimeUpgrade.poller) {
      window.clearInterval(state.runtimeUpgrade.poller);
      state.runtimeUpgrade.poller = 0;
    }
  }

  function startRuntimeUpgradePoller() {
    stopRuntimeUpgradePoller();
    refreshRuntimeUpgradeStatus({ silent: true }).catch(() => {});
    state.runtimeUpgrade.poller = window.setInterval(() => {
      refreshRuntimeUpgradeStatus({ silent: true }).catch(() => {});
    }, 5000);
  }

  async function waitForRuntimeUpgradeReconnect() {
    const deadline = Date.now() + 60000;
    let seenOffline = false;
    while (Date.now() < deadline) {
      let ok = false;
      try {
        const response = await fetch('/healthz', { cache: 'no-store' });
        ok = !!response.ok;
      } catch (_) {
        ok = false;
      }
      if (!ok) {
        seenOffline = true;
      } else if (seenOffline) {
        window.location.reload();
        return;
      }
      await new Promise((resolve) => window.setTimeout(resolve, 1200));
    }
    window.location.reload();
  }

  async function applyRuntimeUpgrade() {
    const info = state.runtimeUpgrade || {};
    if (!info.can_upgrade || info.request_pending || info.reconnecting) {
      renderRuntimeUpgradeBanner();
      return;
    }
    state.runtimeUpgrade.status_error = '';
    const button = $('runtimeUpgradeApplyBtn');
    if (button) button.disabled = true;
    const data = await postJSON('/api/runtime-upgrade/apply', { operator: 'web-user' });
    applyRuntimeUpgradeStatus(
      Object.assign({}, info, {
        request_pending: true,
        blocking_reason: safe(data.reconnect_hint || data.message).trim(),
      })
    );
    state.runtimeUpgrade.reconnecting = true;
    renderRuntimeUpgradeBanner();
    setStatus('正式环境开始升级，页面将自动重连');
    waitForRuntimeUpgradeReconnect().catch(() => {
      window.location.reload();
    });
  }

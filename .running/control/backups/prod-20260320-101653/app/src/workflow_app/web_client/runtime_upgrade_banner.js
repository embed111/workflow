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
    offline_seen: false,
    status_error: '',
    refresh_busy: false,
    poller: 0,
    poll_active: false,
    success_hold_until: 0,
    success_hold_key: '',
    success_hold_timer: 0,
    progress_tick: 0,
    progress_stage_key: '',
    progress_stage_started_at: 0,
  };

  const RUNTIME_UPGRADE_POLL_IDLE_MS = 5000;
  const RUNTIME_UPGRADE_POLL_ACTIVE_MS = 1200;
  const RUNTIME_UPGRADE_SUCCESS_HOLD_MS = 3000;

  function updateRuntimeVersionBadge() {
    const node = $('runtimeVersionBadge');
    if (!node) return;
    const info = state.runtimeUpgrade || {};
    const currentVersion = safe(info.current_version).trim();
    const versionText = currentVersion ? ('版本 ' + currentVersion) : '版本读取中';
    node.textContent = versionText;
    node.setAttribute('title', currentVersion ? ('当前版本: ' + currentVersion) : '当前版本读取中');
    node.setAttribute('aria-label', currentVersion ? ('当前版本 ' + currentVersion) : '当前版本读取中');
  }

  function ensureRuntimeUpgradeBanner() {
    let node = $('runtimeUpgradeBanner');
    if (node) return node;
    node = document.createElement('section');
    node.id = 'runtimeUpgradeBanner';
    node.className = 'runtime-upgrade-banner hidden';
    document.body.appendChild(node);
    return node;
  }

  function ensureRuntimeUpgradeBannerRefs() {
    const node = ensureRuntimeUpgradeBanner();
    if (node._runtimeUpgradeRefs) return node._runtimeUpgradeRefs;

    const wrap = document.createElement('div');
    wrap.className = 'runtime-upgrade-shell';

    const head = document.createElement('div');
    head.className = 'runtime-upgrade-head';
    const title = document.createElement('div');
    title.className = 'runtime-upgrade-title';
    title.textContent = '正式环境可控升级';
    const meta = document.createElement('div');
    meta.className = 'runtime-upgrade-meta';
    head.appendChild(title);
    head.appendChild(meta);

    const body = document.createElement('div');
    body.className = 'runtime-upgrade-body';
    const progressMeta = document.createElement('div');
    progressMeta.className = 'runtime-upgrade-progress-meta';
    const progress = document.createElement('div');
    progress.className = 'runtime-upgrade-progress';
    const progressTrack = document.createElement('div');
    progressTrack.className = 'runtime-upgrade-progress-track';
    const progressFill = document.createElement('div');
    progressFill.className = 'runtime-upgrade-progress-fill';
    progressTrack.appendChild(progressFill);
    progress.appendChild(progressTrack);
    const message = document.createElement('div');
    message.className = 'runtime-upgrade-message';
    const note = document.createElement('div');
    note.className = 'runtime-upgrade-note';
    const error = document.createElement('div');
    error.className = 'runtime-upgrade-note is-bad';
    body.appendChild(progressMeta);
    body.appendChild(progress);
    body.appendChild(message);
    body.appendChild(note);
    body.appendChild(error);

    const actions = document.createElement('div');
    actions.className = 'runtime-upgrade-actions';
    const button = document.createElement('button');
    button.id = 'runtimeUpgradeApplyBtn';
    button.type = 'button';
    actions.appendChild(button);

    wrap.appendChild(head);
    wrap.appendChild(body);
    wrap.appendChild(actions);
    node.appendChild(wrap);

    node._runtimeUpgradeRefs = {
      wrap,
      meta,
      progressMeta,
      progressFill,
      message,
      note,
      error,
      button,
    };
    return node._runtimeUpgradeRefs;
  }

  function runtimeUpgradeShouldShow() {
    const info = state.runtimeUpgrade || {};
    return safe(info.environment).trim() === 'prod' && (
      !!info.banner_visible ||
      !!info.request_pending ||
      !!info.reconnecting ||
      runtimeUpgradeRecentSuccessVisible() ||
      runtimeUpgradeRecentFailureVisible()
    );
  }

  function runtimeUpgradeLastAction() {
    const info = state.runtimeUpgrade || {};
    return info.last_action && typeof info.last_action === 'object' ? info.last_action : {};
  }

  function runtimeUpgradeLastActionStatus() {
    return safe(runtimeUpgradeLastAction().status).trim().toLowerCase();
  }

  function runtimeUpgradeLastActionAt() {
    const last = runtimeUpgradeLastAction();
    return safe(last.finished_at || last.started_at || last.requested_at).trim();
  }

  function runtimeUpgradeRecentTerminalVisible(statuses) {
    const status = runtimeUpgradeLastActionStatus();
    const allow = Array.isArray(statuses) && statuses.length
      ? statuses.map((item) => safe(item).trim().toLowerCase()).filter(Boolean)
      : ['success', 'rollback_success', 'failed'];
    if (!allow.includes(status)) return false;
    const stamp = runtimeUpgradeLastActionAt();
    const ts = stamp ? Date.parse(stamp) : Number.NaN;
    if (!Number.isFinite(ts)) return false;
    return (Date.now() - ts) <= 180000;
  }

  function runtimeUpgradeRecentFailureVisible() {
    return runtimeUpgradeRecentTerminalVisible(['rollback_success', 'failed']);
  }

  function runtimeUpgradeRecentSuccessVisible() {
    const info = state.runtimeUpgrade || {};
    if (runtimeUpgradeLastActionStatus() !== 'success') return false;
    return Number(info.success_hold_until || 0) > Date.now();
  }

  function runtimeUpgradePollDelayMs() {
    const info = state.runtimeUpgrade || {};
    if (info.reconnecting || info.request_pending || runtimeUpgradeLastActionStatus() === 'switching') {
      return RUNTIME_UPGRADE_POLL_ACTIVE_MS;
    }
    return RUNTIME_UPGRADE_POLL_IDLE_MS;
  }

  function clearRuntimeUpgradeSuccessHoldTimer() {
    if (state.runtimeUpgrade.success_hold_timer) {
      window.clearTimeout(state.runtimeUpgrade.success_hold_timer);
      state.runtimeUpgrade.success_hold_timer = 0;
    }
  }

  function scheduleRuntimeUpgradeSuccessHoldTimer() {
    clearRuntimeUpgradeSuccessHoldTimer();
    const remaining = Number(state.runtimeUpgrade.success_hold_until || 0) - Date.now();
    if (!(remaining > 0)) return;
    state.runtimeUpgrade.success_hold_timer = window.setTimeout(() => {
      state.runtimeUpgrade.success_hold_timer = 0;
      renderRuntimeUpgradeBanner();
    }, remaining + 30);
  }

  function syncRuntimeUpgradeSuccessHold() {
    const info = state.runtimeUpgrade || {};
    const last = runtimeUpgradeLastAction();
    const status = runtimeUpgradeLastActionStatus();
    if (status !== 'success') {
      info.success_hold_until = 0;
      info.success_hold_key = '';
      clearRuntimeUpgradeSuccessHoldTimer();
      return;
    }
    const stamp = safe(last.finished_at || last.started_at || last.requested_at).trim();
    const nextKey = [status, stamp, safe(info.current_version).trim(), safe(info.candidate_version).trim()].join('|');
    if (safe(info.success_hold_key).trim() !== nextKey) {
      info.success_hold_key = nextKey;
      info.success_hold_until = Date.now() + RUNTIME_UPGRADE_SUCCESS_HOLD_MS;
    }
    scheduleRuntimeUpgradeSuccessHoldTimer();
  }

  function runtimeUpgradeProgressModel() {
    const info = state.runtimeUpgrade || {};
    const lastStatus = runtimeUpgradeLastActionStatus();
    const stageStamp = safe(runtimeUpgradeLastActionAt()).trim();
    const versionKey = [safe(info.current_version).trim(), safe(info.candidate_version).trim()].join('|');
    let stage = null;
    if (info.reconnecting && info.offline_seen) {
      stage = {
        key: ['reconnecting-offline', stageStamp, versionKey].join('|'),
        label: '正在切换版本',
        tone: 'running',
        minPercent: 74,
        maxPercent: 94,
        durationMs: 12000,
      };
    } else if (info.reconnecting) {
      stage = {
        key: ['reconnecting', stageStamp, versionKey].join('|'),
        label: '等待正式环境重连',
        tone: 'running',
        minPercent: 58,
        maxPercent: 78,
        durationMs: 5000,
      };
    } else if (lastStatus === 'switching') {
      stage = {
        key: ['switching', stageStamp, versionKey].join('|'),
        label: '正在切换候选版本',
        tone: 'running',
        minPercent: 34,
        maxPercent: 58,
        durationMs: 4200,
      };
    } else if (info.request_pending) {
      stage = {
        key: ['request_pending', stageStamp, versionKey].join('|'),
        label: '升级请求已受理',
        tone: 'running',
        minPercent: 12,
        maxPercent: 34,
        durationMs: 2800,
      };
    }
    if (stage) {
      if (safe(info.progress_stage_key).trim() !== stage.key) {
        info.progress_stage_key = stage.key;
        info.progress_stage_started_at = Date.now();
      } else if (!(Number(info.progress_stage_started_at || 0) > 0)) {
        info.progress_stage_started_at = Date.now();
      }
      const elapsed = Math.max(0, Date.now() - Number(info.progress_stage_started_at || Date.now()));
      const progressT = Math.max(0, Math.min(1, elapsed / Math.max(1, Number(stage.durationMs) || 1)));
      const easedT = 1 - Math.pow(1 - progressT, 2.2);
      const percent = stage.minPercent + ((stage.maxPercent - stage.minPercent) * easedT);
      return {
        percent,
        displayPercent: Math.round(percent),
        label: stage.label,
        tone: stage.tone,
        autoAdvance: true,
      };
    }
    info.progress_stage_key = '';
    info.progress_stage_started_at = 0;
    if (runtimeUpgradeRecentTerminalVisible()) {
      if (lastStatus === 'success') {
        return { percent: 100, displayPercent: 100, label: '升级完成', tone: 'done', autoAdvance: false };
      }
      if (lastStatus === 'rollback_success') {
        return { percent: 100, displayPercent: 100, label: '已自动回滚', tone: 'bad', autoAdvance: false };
      }
      if (lastStatus === 'failed') {
        return { percent: 100, displayPercent: 100, label: '升级失败', tone: 'bad', autoAdvance: false };
      }
    }
    if (info.can_upgrade) {
      return { percent: 0, displayPercent: 0, label: '可开始升级', tone: 'idle', autoAdvance: false };
    }
    return { percent: 0, displayPercent: 0, label: '当前不可升级', tone: 'idle', autoAdvance: false };
  }

  function runtimeUpgradeStatusText() {
    const info = state.runtimeUpgrade || {};
    const lastStatus = runtimeUpgradeLastActionStatus();
    if (info.reconnecting && info.offline_seen) {
      return '旧实例已下线，正在等待新实例恢复。';
    }
    if (info.reconnecting) {
      return '正式环境正在切换，页面会短暂刷新并自动重连。';
    }
    if (info.request_pending) {
      return safe(info.blocking_reason).trim() || '正式环境正在切换，请等待完成。';
    }
    if (runtimeUpgradeRecentTerminalVisible()) {
      if (lastStatus === 'success') {
        return '正式环境已完成版本切换。';
      }
      if (lastStatus === 'rollback_success') {
        return '新版本健康检查失败，系统已自动回滚到上一版本。';
      }
      if (lastStatus === 'failed') {
        return safe(runtimeUpgradeLastAction().reason).trim() || '正式环境升级失败。';
      }
    }
    if (safe(info.blocking_reason).trim()) {
      return safe(info.blocking_reason).trim();
    }
    return '当前无运行中任务，可升级到已通过 test 门禁的新版本。';
  }

  function runtimeUpgradeLastActionText() {
    const last = runtimeUpgradeLastAction();
    const status = safe(last.status).trim();
    if (!status) return '';
    const map = {
      requested: '升级请求已记录',
      success: '最近一次升级成功',
      switching: '正在切换正式版本',
      rollback_success: '最近一次升级失败，已自动回退',
      failed: '最近一次升级失败',
    };
    const head = map[status] || ('最近状态：' + status);
    const finishedAt = safe(last.finished_at || last.started_at).trim();
    return finishedAt ? head + ' · ' + formatDateTime(finishedAt) : head;
  }

  function clearRuntimeUpgradeProgressTick() {
    if (state.runtimeUpgrade.progress_tick) {
      window.clearTimeout(state.runtimeUpgrade.progress_tick);
      state.runtimeUpgrade.progress_tick = 0;
    }
  }

  function scheduleRuntimeUpgradeProgressTick(progressInfo) {
    clearRuntimeUpgradeProgressTick();
    if (!runtimeUpgradeShouldShow()) return;
    if (!progressInfo || !progressInfo.autoAdvance) return;
    state.runtimeUpgrade.progress_tick = window.setTimeout(() => {
      state.runtimeUpgrade.progress_tick = 0;
      renderRuntimeUpgradeBanner();
    }, 140);
  }

  function renderRuntimeUpgradeBanner() {
    const node = ensureRuntimeUpgradeBanner();
    const refs = ensureRuntimeUpgradeBannerRefs();
    const info = state.runtimeUpgrade || {};
    if (!runtimeUpgradeShouldShow()) {
      node.classList.add('hidden');
      clearRuntimeUpgradeProgressTick();
      return;
    }
    node.classList.remove('hidden');
    refs.meta.textContent =
      '当前版本 ' +
      (safe(info.current_version).trim() || '-') +
      ' -> 待升级版本 ' +
      (safe(info.candidate_version).trim() || '-');
    const progressInfo = runtimeUpgradeProgressModel();
    refs.progressMeta.textContent =
      progressInfo.label + ' · ' + String(Math.max(0, Math.min(100, Number(progressInfo.displayPercent) || 0))) + '%';
    refs.progressFill.className = 'runtime-upgrade-progress-fill is-' + safe(progressInfo.tone).trim();
    refs.progressFill.style.width = String(Math.max(0, Math.min(100, Number(progressInfo.percent) || 0))) + '%';
    refs.message.textContent = runtimeUpgradeStatusText();

    const lastActionText = runtimeUpgradeLastActionText();
    if (lastActionText) {
      refs.note.textContent = lastActionText;
      refs.note.style.display = '';
    } else {
      refs.note.textContent = '';
      refs.note.style.display = 'none';
    }
    if (safe(info.status_error).trim()) {
      refs.error.textContent = '升级状态读取失败：' + safe(info.status_error).trim();
      refs.error.style.display = '';
    } else {
      refs.error.textContent = '';
      refs.error.style.display = 'none';
    }

    const button = refs.button;
    if (info.reconnecting || info.request_pending || info.can_upgrade) {
      button.textContent = info.reconnecting || info.request_pending ? '切换中' : '升级正式环境';
      button.disabled = !!info.reconnecting || !!info.request_pending || !info.can_upgrade;
      button.classList.remove('is-placeholder');
      button.removeAttribute('aria-hidden');
      button.tabIndex = 0;
      button.onclick = () => {
        applyRuntimeUpgrade().catch((err) => {
          state.runtimeUpgrade.status_error = safe(err && err.message ? err.message : err);
          renderRuntimeUpgradeBanner();
        });
      };
    } else {
      button.textContent = '升级正式环境';
      button.disabled = true;
      button.classList.add('is-placeholder');
      button.tabIndex = -1;
      button.setAttribute('aria-hidden', 'true');
      button.onclick = null;
    }
    scheduleRuntimeUpgradeProgressTick(progressInfo);
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
    syncRuntimeUpgradeSuccessHold();
    updateRuntimeVersionBadge();
    renderRuntimeUpgradeBanner();
    rescheduleRuntimeUpgradePoller();
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
        updateRuntimeVersionBadge();
        renderRuntimeUpgradeBanner();
      }
      return state.runtimeUpgrade;
    } finally {
      state.runtimeUpgrade.refresh_busy = false;
    }
  }

  function stopRuntimeUpgradePoller() {
    if (state.runtimeUpgrade.poller) {
      window.clearTimeout(state.runtimeUpgrade.poller);
      state.runtimeUpgrade.poller = 0;
    }
    state.runtimeUpgrade.poll_active = false;
  }

  function scheduleRuntimeUpgradePoller(delayMs) {
    if (!state.runtimeUpgrade.poll_active) return;
    if (state.runtimeUpgrade.poller) {
      window.clearTimeout(state.runtimeUpgrade.poller);
      state.runtimeUpgrade.poller = 0;
    }
    const nextDelay = Math.max(300, Number(delayMs) || runtimeUpgradePollDelayMs());
    state.runtimeUpgrade.poller = window.setTimeout(async () => {
      state.runtimeUpgrade.poller = 0;
      try {
        await refreshRuntimeUpgradeStatus({ silent: true });
      } catch (_) {
      }
      scheduleRuntimeUpgradePoller(runtimeUpgradePollDelayMs());
    }, nextDelay);
  }

  function rescheduleRuntimeUpgradePoller() {
    if (!state.runtimeUpgrade.poll_active) return;
    scheduleRuntimeUpgradePoller(runtimeUpgradePollDelayMs());
  }

  function startRuntimeUpgradePoller() {
    stopRuntimeUpgradePoller();
    state.runtimeUpgrade.poll_active = true;
    refreshRuntimeUpgradeStatus({ silent: true })
      .catch(() => {})
      .finally(() => {
        scheduleRuntimeUpgradePoller(runtimeUpgradePollDelayMs());
      });
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
        if (!seenOffline) {
          seenOffline = true;
          state.runtimeUpgrade.offline_seen = true;
          renderRuntimeUpgradeBanner();
          rescheduleRuntimeUpgradePoller();
        }
      } else if (seenOffline) {
        state.runtimeUpgrade.offline_seen = false;
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
        last_action: {
          status: 'requested',
          requested_at: new Date().toISOString(),
        },
      })
    );
    state.runtimeUpgrade.offline_seen = false;
    state.runtimeUpgrade.reconnecting = true;
    renderRuntimeUpgradeBanner();
    rescheduleRuntimeUpgradePoller();
    setStatus('正式环境开始升级，页面将自动重连');
    waitForRuntimeUpgradeReconnect().catch(() => {
      window.location.reload();
    });
  }

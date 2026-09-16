const $ = (id) => document.getElementById(id);
const protocolVersion = "1.0";
let socket;
let policyDirty = false;
let pendingPolicyVersion = null;
let latestState = { policy: { version: 1, threshold_c: 30, hysteresis_c: 1, mode: "AUTO" } };

function envelope(type, fields) {
  return {
    type,
    protocol_version: protocolVersion,
    message_id: crypto.randomUUID(),
    timestamp: new Date().toISOString(),
    ...fields,
  };
}

function showToast(message) {
  $("toast").textContent = message;
  $("toast").classList.add("show");
  setTimeout(() => $("toast").classList.remove("show"), 2400);
}

function setSocketStatus(status, label) {
  const badge = $("socketBadge");
  badge.className = `badge ${status}`;
  badge.innerHTML = `<i></i>${label}`;
}

function connect() {
  const scheme = location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(`${scheme}://${location.host}/ws/dashboard`);
  socket.onopen = () => setSocketStatus("online", "控制平面在线");
  socket.onclose = () => {
    setSocketStatus("offline", "控制平面失联 · 正在重连");
    setTimeout(connect, 1800);
  };
  socket.onerror = () => socket.close();
  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === "snapshot") render(message);
    if (message.type === "error") showToast(`${message.code}: ${message.message}`);
  };
}

function formatTime(value) {
  if (!value) return "—";
  return new Date(value).toLocaleTimeString("zh-CN", { hour12: false });
}

function syncPolicyForm(policy) {
  $("policyMode").value = policy.mode;
  $("threshold").value = policy.threshold_c;
  $("hysteresis").value = policy.hysteresis_c;
}

function render(state) {
  latestState = state;
  const temperature = state.temperature_c;
  $("temperature").textContent = temperature == null ? "--.-" : temperature.toFixed(1);
  $("temperatureBar").style.width = temperature == null ? "0" : `${Math.max(0, Math.min(100, ((temperature - 15) / 30) * 100))}%`;

  const warning = temperature != null && temperature >= state.policy.threshold_c;
  $("thermalState").textContent = temperature == null ? "等待遥测" : warning ? "WARNING · 达到阈值" : "NORMAL · 边缘监控中";
  $("thermalState").className = `pill ${temperature == null ? "neutral" : warning ? "warning" : "normal"}`;

  $("edgeState").textContent = state.edge_online ? "ONLINE" : "OFFLINE";
  $("edgeState").style.color = state.edge_online ? "var(--cyan)" : "var(--red)";
  $("controlMode").textContent = state.control_mode;
  $("cloudState").textContent = state.cloud_state;
  $("policyVersion").textContent = `v${state.policy.version}`;
  $("heartbeat").textContent = formatTime(state.last_heartbeat);
  $("fanState").textContent = state.fan_state;
  $("fanVisual").classList.toggle("running", state.fan_state === "ON");

  if (pendingPolicyVersion !== null && state.policy.version >= pendingPolicyVersion) {
    pendingPolicyVersion = null;
    policyDirty = false;
  }
  if (!policyDirty && pendingPolicyVersion === null) {
    syncPolicyForm(state.policy);
  }
  document.querySelectorAll("button").forEach((button) => button.disabled = !state.edge_online);
  renderEvents(state.events || []);
}

function renderEvents(events) {
  $("eventCount").textContent = `${events.length} events`;
  if (!events.length) {
    $("events").innerHTML = '<div class="empty">等待系统事件…</div>';
    return;
  }
  $("events").innerHTML = events.slice(0, 30).map((item) => `
    <div class="event-row">
      <span>${formatTime(item.timestamp)}</span>
      <b>${item.event}</b>
      <span class="source">${item.source}</span>
      <span class="detail">${item.detail}</span>
    </div>`).join("");
}

document.querySelectorAll("button[data-action]").forEach((button) => {
  button.addEventListener("click", () => {
    socket.send(JSON.stringify(envelope("command", {
      command_id: crypto.randomUUID(),
      device_id: "FAN01",
      action: button.dataset.action,
    })));
    showToast(`已发送 FAN01 ${button.dataset.action}`);
  });
});

["policyMode", "threshold", "hysteresis"].forEach((id) => {
  ["input", "change"].forEach((type) => {
    $(id).addEventListener(type, () => {
      policyDirty = true;
    });
  });
});

$("policyForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const version = Number(latestState.policy.version || 0) + 1;
  const policy = {
    policy_id: "thermal-01",
    version,
    mode: $("policyMode").value,
    threshold_c: Number($("threshold").value),
    hysteresis_c: Number($("hysteresis").value),
  };
  pendingPolicyVersion = version;
  policyDirty = true;
  socket.send(JSON.stringify(envelope("policy", policy)));
  showToast(`策略 v${version} 下发中 · ${policy.threshold_c}°C`);
});

connect();

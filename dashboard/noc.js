/* NOC adapter state is independent of the existing Edge WebSocket. */
(() => {
  const el = (id) => document.getElementById(id);
  let busy = false;
  function status(id, value, healthy) {
    const node = el(id);
    node.textContent = value;
    node.className = `noc-status ${healthy ? "good" : ["UNAVAILABLE", "UNKNOWN", "NOT_CONFIGURED", "NOT COLLECTED"].includes(value) ? "unknown" : "bad"}`;
  }
  function renderNetwork(state) {
    ["nocOspf", "nocBgp", "nocTunnel"].forEach(id => status(id, "NOT COLLECTED", false));
    el("networkSourceBadge").textContent = "PT 控制器 · 实际数据";
    el("networkFailure").disabled = true;
    el("networkRestore").disabled = true;
    renderController(state.source && state.source.kind === "PT_CONTROLLER" ? state.controller : null);
  }
  function renderController(controller) {
    const target = el("controllerDevices");
    target.textContent = "";
    el("networkDeviceCards").textContent = "";
    if (!controller || !controller.configured || controller.source !== "PT_CONTROLLER") {
      status("controllerStatus", "NOT_CONFIGURED", false);
      el("controllerNotice").textContent = "尚未接入控制器。配置 PT_CONTROLLER_URL、用户名和密码后重启 Backend；网络健康仅接收真实 NC 数据，不显示模拟状态。";
      el("nocNetworkNotice").textContent = "尚未配置真实 NC；没有设备健康数据。";
      el("controllerTime").textContent = "";
      el("controllerTopology").textContent = "暂无控制器数据";
      return;
    }
    status("controllerStatus", controller.status, controller.status === "CONNECTED");
    const errors = {MISSING_CREDENTIALS:"未设置控制器用户名或密码",AUTH_FAILED:"控制器认证失败，请检查账户",CONNECTION_FAILED:"无法连接控制器，请检查 Real World Access 和端口",INVALID_INVENTORY_RESPONSE:"设备清单响应格式不兼容",INVALID_AUTH_RESPONSE:"登录响应中没有有效票据",INVALID_JSON:"控制器返回了无效 JSON"};
    el("controllerNotice").textContent = controller.error ? `${errors[controller.error] || controller.error}；未使用模拟数据替代。` : `实际读取 ${controller.devices.length} 台设备 · ${controller.url}${controller.devices.length ? "" : " · 清单为空，请先执行设备发现"}${controller.topology_error ? " · 拓扑暂不可用" : ""}`;
    el("controllerTime").textContent = `采集时间：${controller.observed_at || "未成功采集"} · 后端最多每 5 秒查询一次`;
    el("nocNetworkNotice").textContent = el("controllerNotice").textContent;
    const devices = controller.status === "CONNECTED" && controller.source === "PT_CONTROLLER" ? controller.devices : [];
    devices.forEach(device => {
      const name = device.hostname || device.name || device.id || "未命名";
      const ip = device.managementIpAddress || device.ipAddress || "未提供";
      const collection = device.collectionStatus || "NOT COLLECTED";
      const online = collection === "Managed";
      const card = document.createElement("article"); card.className = "network-device-card";
      [["h3", name], ["p", `管理 IP：${ip}`], ["p", `控制器状态：${collection}`], ["b", online ? "ONLINE" : collection]].forEach(([tag, value]) => {
        const node = document.createElement(tag); node.textContent = String(value);
        if (tag === "b") node.className = `noc-status ${online ? "good" : "unknown"}`;
        card.appendChild(node);
      });
      el("networkDeviceCards").appendChild(card);
      const row = document.createElement("tr");
      [device.hostname || device.name || device.id || "未命名", device.managementIpAddress || device.ipAddress || "未提供", device.type || device.deviceType || device.family || "未提供", online ? "ONLINE · Managed" : collection].forEach(value => {
        const cell = document.createElement("td"); cell.textContent = String(value); row.appendChild(cell);
      });
      target.appendChild(row);
    });
    el("controllerTopology").textContent = controller.topology ? JSON.stringify(controller.topology, null, 2) : "暂无可用拓扑数据";
  }
  function securityDetail(event) {
    return event.event === "PORT_SECURITY_VIOLATION" ? "检测到未经授权的 MAC · 端口已阻断" : event.event === "ACL_BLOCK_EVENT" ? "检测到未授权流量 · ACL 已阻断" : event.detail;
  }
  const display = value => ({"AUTONOMOUS MODE (expected)":"本地自治模式（预期）", "NOT_RUN":"尚未演练", "WAITING_FOR_RECOVERY":"等待恢复云端", "WAITING_FOR_STATE_SYNC":"等待 Edge 状态同步", "SUCCESS":"同步成功 SUCCESS", "LAST KNOWN · live telemetry unavailable":"最后观测值 · 当前无法获取实时遥测", "LIVE EDGE TELEMETRY":"Edge 实时遥测"}[value] || value);
  function renderSecurity(state) {
    status("nocSecurity", state.port_security, state.port_security === "SECURE");
    el("nocViolations").textContent = state.violations;
    el("nocAcl").textContent = state.acl;
    el("nocPort").textContent = state.port_status;
    const card = el("nocSecurityEvent");
    card.textContent = state.last_event ? `${state.last_event.event} · ${securityDetail(state.last_event)}${state.active ? "" : " · 已恢复"}` : "暂无安全事件";
    card.className = state.active ? "security-alert" : "notice";
  }
  async function securityAction(path) {
    try {
      const response = await fetch(path, {method: "POST", headers: {"Content-Type": "application/json"}, body: "{}", signal: AbortSignal.timeout(5000)});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      renderSecurity(data.security || data);
      el("securityActionResult").textContent = "演练状态已更新";
    } catch (error) { el("securityActionResult").textContent = `演练失败： ${error.message}`; }
  }
  el("securityAttack").addEventListener("click", () => securityAction("/api/simulation/security"));
  el("securityRestore").addEventListener("click", () => securityAction("/api/simulation/security/restore"));
  function renderCenters(data) {
    const policy = data.policy;
    el("campusVersion").textContent = policy.campus_version;
    el("campusThermal").textContent = `${policy.thermal.policy_id} · v${policy.thermal.version} · ${policy.thermal.threshold_c}℃ · ${policy.thermal.mode}`;
    el("campusNetwork").textContent = `分部访问 ${policy.network.branch_access} · IoT 隔离 ${policy.network.iot_isolation ? "已启用" : "未启用"}`;
    el("campusSecurity").textContent = `端口安全 ${policy.security.port_security}`;
    data.branch.devices.forEach(device => { el(device.device === "R-BRANCH" ? "routerStatus" : "switchStatus").textContent = device.status; });
    const simulation = data.simulation;
    status("simCloud", simulation.cloud, simulation.cloud === "ONLINE");
    el("simMode").textContent = simulation.edge_connected ? display(simulation.edge_mode) : simulation.cloud_failed ? display(simulation.edge_mode) : "边缘节点未连接";
    el("simFan").textContent = simulation.fan;
    el("simSync").textContent = display(simulation.state_sync);
    el("fanObservation").textContent = display(simulation.fan_observation);
  }
  async function action(button, path, payload, output) {
    button.disabled = true;
    el(output).textContent = "正在执行…";
    try {
      const response = await fetch(path, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload), signal: AbortSignal.timeout(5000)});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();
      el(output).textContent = result.management ? `${result.device} · 远程管理 ${result.management} · VTY ACL ${result.acl}` : "演练已执行 · 正在刷新状态";
      await refresh();
    } catch (error) { el(output).textContent = `操作失败： ${error.message}`; }
    finally { button.disabled = false; }
  }
  const bindings = [
    ["checkRouter", "/api/branch/check", {device: "R-BRANCH"}, "branchResult"],
    ["checkSwitch", "/api/branch/check", {device: "SW-BRANCH"}, "branchResult"],
    ["cloudFailure", "/api/simulation/cloud", {}, "simulationResult"],
    ["cloudRestore", "/api/simulation/cloud/restore", {}, "simulationResult"],
    ["networkFailure", "/api/simulation/network", {}, "simulationResult"],
    ["networkRestore", "/api/simulation/network/restore", {}, "simulationResult"],
    ["simAttack", "/api/simulation/security", {}, "simulationResult"],
    ["simSecurityRestore", "/api/simulation/security/restore", {}, "simulationResult"],
  ];
  bindings.forEach(([id, path, payload, output]) => el(id).addEventListener("click", () => action(el(id), path, payload, output)));
  async function refresh() {
    if (busy) return;
    busy = true;
    try {
      const response = await fetch("/api/noc/state", {cache: "no-store", signal: AbortSignal.timeout(10000)});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      renderNetwork(data.network);
      renderSecurity(data.security);
      renderCenters(data);
    } catch (error) {
      ["nocOspf", "nocBgp", "nocTunnel"].forEach(id => status(id, "NOT COLLECTED", false));
      el("networkDeviceCards").textContent = "";
      ["nocSecurity", "nocViolations", "nocAcl", "nocPort", "routerStatus", "switchStatus", "campusVersion", "campusThermal", "campusNetwork", "campusSecurity", "simCloud", "simMode", "simFan", "simSync"].forEach(id => { el(id).textContent = "UNAVAILABLE"; });
      status("controllerStatus", "UNAVAILABLE", false);
      el("controllerNotice").textContent = "Backend 不可用，无法确认控制器最新状态";
      el("controllerDevices").textContent = "";
      el("controllerTopology").textContent = "最新数据不可用";
      status("nocSecurity", "UNAVAILABLE", false);
      status("simCloud", "UNAVAILABLE", false);
      el("nocSecurityEvent").textContent = "安全状态不可用；等待新数据";
      el("nocSecurityEvent").className = "notice";
      el("fanObservation").textContent = "运维接口不可用；无法确认实时状态";
      el("nocNetworkNotice").textContent = "Network Agent 不可用；正在重试，未沿用旧健康状态。";
    } finally { busy = false; }
  }
  refresh();
  setInterval(refresh, 1500);
})();

/* NOC adapter state is independent of the existing Edge WebSocket. */
(() => {
  const el = (id) => document.getElementById(id);
  let busy = false;
  function status(id, value, healthy) {
    const node = el(id);
    node.textContent = value;
    node.className = `noc-status ${healthy ? "good" : ["UNAVAILABLE", "UNKNOWN", "NOT_CONFIGURED"].includes(value) ? "unknown" : "bad"}`;
  }
  function renderNetwork(state) {
    status("nocOspf", state.ospf, state.ospf === "FULL");
    status("nocBgp", state.bgp, state.bgp === "ESTABLISHED");
    status("nocTunnel", state.ipv6_tunnel, state.ipv6_tunnel === "UP");
    status("nocBranch", state.branch_status, state.branch_status === "ONLINE");
    const live = state.source && state.source.kind === "PT_CONTROLLER";
    el("networkSourceBadge").textContent = live ? "PT 控制器 · 实际读取" : "模拟适配器";
    el("nocNetworkNotice").textContent = live ? "已选择真实控制器模式；设备清单与拓扑见下方。OSPF/BGP/Tunnel/分部业务连接尚无直接观测，显示 UNKNOWN。" : "模拟适配器 · 配置模拟状态；不代表实时读取 PT 路由器。";
    el("networkFailure").disabled = live;
    el("networkRestore").disabled = live;
    renderController(state.controller);
  }
  function renderController(controller) {
    const target = el("controllerDevices");
    target.textContent = "";
    if (!controller || !controller.configured) {
      status("controllerStatus", "NOT_CONFIGURED", false);
      el("controllerNotice").textContent = "尚未接入控制器。配置 PT_CONTROLLER_URL、用户名和密码后重启 Backend；目前网络状态为模拟数据。";
      el("controllerTime").textContent = "";
      el("controllerTopology").textContent = "暂无控制器数据";
      return;
    }
    status("controllerStatus", controller.status, controller.status === "CONNECTED");
    const errors = {MISSING_CREDENTIALS:"未设置控制器用户名或密码",AUTH_FAILED:"控制器认证失败，请检查账户",CONNECTION_FAILED:"无法连接控制器，请检查 Real World Access 和端口",INVALID_INVENTORY_RESPONSE:"设备清单响应格式不兼容",INVALID_AUTH_RESPONSE:"登录响应中没有有效票据",INVALID_JSON:"控制器返回了无效 JSON"};
    el("controllerNotice").textContent = controller.error ? `${errors[controller.error] || controller.error}；未使用模拟数据替代。` : `实际读取 ${controller.devices.length} 台设备 · ${controller.url}${controller.devices.length ? "" : " · 清单为空，请先执行设备发现"}${controller.topology_error ? " · 拓扑暂不可用" : ""}`;
    el("controllerTime").textContent = `采集时间：${controller.observed_at || "未成功采集"} · 后端最多每 5 秒查询一次`;
    controller.devices.forEach(device => {
      const row = document.createElement("tr");
      [device.hostname || device.name || device.id || "未命名", device.managementIpAddress || device.ipAddress || "未提供", device.type || device.deviceType || device.family || "未提供", device.reachabilityStatus || device.collectionStatus || "UNKNOWN（接口未提供）"].forEach(value => {
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
      ["nocOspf", "nocBgp", "nocTunnel", "nocBranch"].forEach(id => status(id, "UNAVAILABLE", false));
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

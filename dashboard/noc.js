/* NOC adapter state is independent of the existing Edge WebSocket. */
(() => {
  const el = (id) => document.getElementById(id);
  let busy = false;
  function status(id, value, healthy) {
    const node = el(id);
    node.textContent = value;
    node.className = `noc-status ${healthy ? "good" : value === "UNAVAILABLE" ? "unknown" : "bad"}`;
  }
  function renderNetwork(state) {
    status("nocOspf", state.ospf, state.ospf === "FULL");
    status("nocBgp", state.bgp, state.bgp === "ESTABLISHED");
    status("nocTunnel", state.ipv6_tunnel, state.ipv6_tunnel === "UP");
    status("nocBranch", state.branch_status, state.branch_status === "ONLINE");
    el("nocNetworkNotice").textContent = "MOCK ADAPTER · 配置模拟状态；不代表实时读取 PT 路由器。";
  }
  function renderSecurity(state) {
    status("nocSecurity", state.port_security, state.port_security === "SECURE");
    el("nocViolations").textContent = state.violations;
    el("nocAcl").textContent = state.acl;
    el("nocPort").textContent = state.port_status;
    const card = el("nocSecurityEvent");
    card.textContent = state.last_event ? `${state.last_event.event} · ${state.last_event.detail}${state.active ? "" : " · RESOLVED"}` : "No security event";
    card.className = state.active ? "security-alert" : "notice";
  }
  async function securityAction(path) {
    try {
      const response = await fetch(path, {method: "POST", headers: {"Content-Type": "application/json"}, body: "{}", signal: AbortSignal.timeout(5000)});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      renderSecurity(data.security || data);
      el("securityActionResult").textContent = "Simulation updated";
    } catch (error) { el("securityActionResult").textContent = `Simulation failed: ${error.message}`; }
  }
  el("securityAttack").addEventListener("click", () => securityAction("/api/simulation/security"));
  el("securityRestore").addEventListener("click", () => securityAction("/api/simulation/security/restore"));
  function renderCenters(data) {
    const policy = data.policy;
    el("campusVersion").textContent = policy.campus_version;
    el("campusThermal").textContent = `${policy.thermal.policy_id} · v${policy.thermal.version} · ${policy.thermal.threshold_c}℃ · ${policy.thermal.mode}`;
    el("campusNetwork").textContent = `Branch ${policy.network.branch_access} · IoT Isolation ${policy.network.iot_isolation ? "ENABLE" : "DISABLE"}`;
    el("campusSecurity").textContent = `Port Security ${policy.security.port_security}`;
    data.branch.devices.forEach(device => { el(device.device === "R-BRANCH" ? "routerStatus" : "switchStatus").textContent = device.status; });
    const simulation = data.simulation;
    status("simCloud", simulation.cloud, simulation.cloud === "ONLINE");
    el("simMode").textContent = simulation.edge_connected ? simulation.edge_mode : simulation.cloud_failed ? simulation.edge_mode : "EDGE DISCONNECTED";
    el("simFan").textContent = simulation.fan;
    el("simSync").textContent = simulation.state_sync;
    el("fanObservation").textContent = simulation.fan_observation;
  }
  async function action(button, path, payload, output) {
    button.disabled = true;
    el(output).textContent = "Running…";
    try {
      const response = await fetch(path, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload), signal: AbortSignal.timeout(5000)});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();
      el(output).textContent = result.management ? `${result.device} · Remote Management ${result.management} · VTY ACL ${result.acl}` : "Simulation applied · refreshing state";
      await refresh();
    } catch (error) { el(output).textContent = `Operation failed: ${error.message}`; }
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
      const response = await fetch("/api/noc/state", {cache: "no-store", signal: AbortSignal.timeout(5000)});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      renderNetwork(data.network);
      renderSecurity(data.security);
      renderCenters(data);
    } catch (error) {
      ["nocOspf", "nocBgp", "nocTunnel", "nocBranch"].forEach(id => status(id, "UNAVAILABLE", false));
      ["nocSecurity", "nocViolations", "nocAcl", "nocPort", "routerStatus", "switchStatus", "campusVersion", "campusThermal", "campusNetwork", "campusSecurity", "simCloud", "simMode", "simFan", "simSync"].forEach(id => { el(id).textContent = "UNAVAILABLE"; });
      status("nocSecurity", "UNAVAILABLE", false);
      status("simCloud", "UNAVAILABLE", false);
      el("nocSecurityEvent").textContent = "Security state unavailable; awaiting fresh data";
      el("nocSecurityEvent").className = "notice";
      el("fanObservation").textContent = "NOC API unavailable; live observation not confirmed";
      el("nocNetworkNotice").textContent = "Network Agent 不可用；正在重试，未沿用旧健康状态。";
    } finally { busy = false; }
  }
  refresh();
  setInterval(refresh, 1500);
})();

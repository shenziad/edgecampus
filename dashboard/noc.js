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
    status("nocSecurity", state.port_security, !state.active);
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
  async function refresh() {
    if (busy) return;
    busy = true;
    try {
      const response = await fetch("/api/network/state", {cache: "no-store", signal: AbortSignal.timeout(5000)});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      renderNetwork(await response.json());
      const securityResponse = await fetch("/api/security/state", {cache: "no-store", signal: AbortSignal.timeout(5000)});
      if (!securityResponse.ok) throw new Error("Security API unavailable");
      renderSecurity(await securityResponse.json());
    } catch (error) {
      ["nocOspf", "nocBgp", "nocTunnel", "nocBranch"].forEach(id => status(id, "UNAVAILABLE", false));
      el("nocNetworkNotice").textContent = "Network Agent 不可用；正在重试，未沿用旧健康状态。";
    } finally { busy = false; }
  }
  refresh();
  setInterval(refresh, 1500);
})();

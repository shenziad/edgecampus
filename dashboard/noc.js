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
  async function refresh() {
    if (busy) return;
    busy = true;
    try {
      const response = await fetch("/api/network/state", {cache: "no-store", signal: AbortSignal.timeout(5000)});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      renderNetwork(await response.json());
    } catch (error) {
      ["nocOspf", "nocBgp", "nocTunnel", "nocBranch"].forEach(id => status(id, "UNAVAILABLE", false));
      el("nocNetworkNotice").textContent = "Network Agent 不可用；正在重试，未沿用旧健康状态。";
    } finally { busy = false; }
  }
  refresh();
  setInterval(refresh, 1500);
})();

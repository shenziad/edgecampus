const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const nodes = new Map();
const el = id => {
  if (!nodes.has(id)) nodes.set(id, {textContent: '', className: '', disabled: false, listeners: {}, children: [], appendChild(node) { this.children.push(node); },
    addEventListener(type, fn) { this.listeners[type] = fn; }});
  return nodes.get(id);
};
let fail = false;
let responseState = {ospf: 'FULL', bgp: 'ESTABLISHED', ipv6_tunnel: 'UP', branch_status: 'ONLINE'};
const intervals = [];
const context = vm.createContext({document: {getElementById: el, createElement: tag => ({tagName:tag, textContent:"", children:[], appendChild(node) {this.children.push(node);}})},
  AbortSignal: {timeout: () => ({})}, setInterval: fn => intervals.push(fn),
  fetch: async () => { if (fail) throw Error('offline'); return {ok: true, json: async () => ({network: responseState, security: {port_security: "SECURE", active: false, violations: 0, acl: "ACTIVE", port_status: "FORWARDING"}, branch: {devices: [{device:"R-BRANCH",status:"AVAILABLE"}]}, policy: {campus_version:"campus-1 / thermal-v3",thermal:{policy_id:"thermal-01",version:3,threshold_c:33,mode:"AUTO"},network:{branch_access:"ALLOW",iot_isolation:true},security:{port_security:"STRICT"}}, simulation:{cloud:"ONLINE",edge_connected:true,edge_mode:"AUTO",fan:"ON",state_sync:"NOT_RUN",fan_observation:"LIVE"}})}; },
});
vm.runInContext(fs.readFileSync('dashboard/noc.js', 'utf8'), context);
const settle = () => new Promise(resolve => setImmediate(resolve));
(async () => {
  await settle();
  assert.equal(el('nocOspf').textContent, 'FULL');
  assert.equal(el('nocBgp').textContent, 'ESTABLISHED');
  assert.equal(el('nocTunnel').textContent, 'UP');
  assert.match(el('nocBranch').className, /good/);
  fail = true;
  await intervals[0]();
  assert.equal(el('nocOspf').textContent, 'UNAVAILABLE');
  assert.match(el('nocOspf').className, /unknown/);
  fail = false;
  responseState = {...responseState, bgp: 'DOWN', ipv6_tunnel: 'DOWN', branch_status: 'OFFLINE'};
  await intervals[0]();
  assert.equal(el('nocBgp').textContent, 'DOWN');
  assert.match(el('nocBgp').className, /bad/);
  responseState = {...responseState, ospf:"UNKNOWN", bgp:"UNKNOWN", ipv6_tunnel:"UNKNOWN", branch_status:"UNKNOWN", source:{kind:"PT_CONTROLLER"}, controller:{configured:true,status:"CONNECTED",url:"http://127.0.0.1:58000/api/v1",devices:[{hostname:"<script>not executable</script>",managementIpAddress:"192.168.30.1"}],topology:{nodes:[],links:[]}, observed_at:"fixture-time"}};
  await intervals[0]();
  assert.equal(el("controllerStatus").textContent,"CONNECTED");
  assert.equal(el("networkFailure").disabled,true);
  assert.match(el("nocBgp").className,/unknown/);
  assert.equal(el("controllerDevices").children.at(-1).children[0].textContent,"<script>not executable</script>");
  assert.match(el("controllerNotice").textContent,/实际读取 1 台/);
  responseState.controller = {...responseState.controller,status:"UNAVAILABLE",devices:[],topology:null,error:"AUTH_FAILED",observed_at:null};
  await intervals[0]();
  assert.match(el("controllerNotice").textContent,/认证失败/);
  assert.equal(el("controllerDevices").textContent, "");
  assert.equal(el("nocOspf").textContent, "UNKNOWN");
  console.log('PASS: NOC health, unavailable/degraded routing, controller inventory/error rendering and live simulation guard');
})().catch(error => { console.error(error); process.exitCode = 1; });

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const nodes = new Map();
const el = id => {
  if (!nodes.has(id)) nodes.set(id, {textContent: '', className: '', disabled: false, listeners: {},
    addEventListener(type, fn) { this.listeners[type] = fn; }});
  return nodes.get(id);
};
let fail = false;
let responseState = {ospf: 'FULL', bgp: 'ESTABLISHED', ipv6_tunnel: 'UP', branch_status: 'ONLINE'};
const intervals = [];
const context = vm.createContext({document: {getElementById: el},
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
  console.log('PASS: NOC health rendering, API unavailable state and degraded routing');
})().catch(error => { console.error(error); process.exitCode = 1; });

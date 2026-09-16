const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const elements = new Map();
const buttons = [{disabled: false, addEventListener() {}}, {disabled: false, addEventListener() {}}];
const timers = [];
const sockets = [];
const element = id => {
  if (!elements.has(id)) elements.set(id, {textContent: '', style: {}, classList: {add() {}, remove() {}, toggle() {}}, addEventListener() {}});
  return elements.get(id);
};
function FakeSocket() { sockets.push(this); this.readyState = 1; }
FakeSocket.OPEN = 1;
const context = vm.createContext({
  document: {getElementById: element, querySelectorAll: () => buttons},
  location: {protocol: 'http:', host: 'test'}, WebSocket: FakeSocket,
  setTimeout: (fn, delay) => timers.push({fn, delay}), Date,
});
vm.runInContext(fs.readFileSync('dashboard/app.js', 'utf8'), context);
const first = sockets[0];
first.onclose();
assert.equal(element('cloudState').textContent, 'DISCONNECTED');
assert.ok(buttons.every(b => b.disabled));
assert.match(element('socketBadge').innerHTML, /\u6b63\u5728\u91cd\u8fde/);
assert.equal(timers[0].delay, 1800);
timers[0].fn();
const recovered = sockets[1];
recovered.onopen();
assert.ok(buttons.every(b => b.disabled));
const state = {type: 'snapshot', edge_online: true, cloud_state: 'CONNECTED', temperature_c: 31.8,
  fan_state: 'OFF', control_mode: 'AUTO', last_heartbeat: null, events: [],
  policy: {policy_id: 'thermal-01', version: 2, mode: 'AUTO', threshold_c: 33, hysteresis_c: 1}};
recovered.onmessage({data: JSON.stringify(state)});
assert.equal(element('temperature').textContent, '31.8');
assert.equal(element('fanState').textContent, 'OFF');
assert.equal(element('policyVersion').textContent, 'v2');
assert.equal(element('threshold').value, 33);
assert.ok(buttons.every(b => !b.disabled));
recovered.onmessage({data: JSON.stringify({...state, edge_online: false})});
assert.ok(buttons.every(b => b.disabled));
console.log('PASS: dashboard disconnect disables controls; snapshot restores true state; offline controls stay disabled');

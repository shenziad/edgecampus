const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const elements = new Map();
const element = id => {
  if (!elements.has(id)) elements.set(id, {textContent: '', addEventListener() {}});
  return elements.get(id);
};
const context = vm.createContext({
  document: {getElementById: element, querySelectorAll: () => []},
  location: {protocol: 'http:', host: 'test'}, WebSocket: function () {},
});
vm.runInContext(fs.readFileSync('dashboard/app.js', 'utf8'), context);
const sent = detail => ({event: 'COMMAND_SENT', detail});
const ack = detail => ({event: 'COMMAND_ACK', detail});
const telemetry = {event: 'TEMPERATURE', detail: '31.8 C'};
context.renderAckState([]);
assert.equal(element('commandAck').textContent, '尚未收到');
const oldAck = ack('FAN01 OFF APPLIED');
const request = sent('FAN01 ON');
context.renderAckState([telemetry, request, oldAck]);
assert.equal(element('commandAck').textContent, '等待 ACK · FAN01 ON');
context.renderAckState([telemetry, telemetry, request, oldAck]);
assert.equal(element('commandAck').textContent, '等待 ACK · FAN01 ON');
const response = ack('FAN01 ON APPLIED');
context.renderAckState([telemetry, response, request, oldAck]);
assert.equal(element('commandAck').textContent, 'FAN01 ON APPLIED');
context.renderAckState([...Array(98).fill(telemetry), response, request]);
assert.equal(element('commandAck').textContent, 'FAN01 ON APPLIED');
context.renderAckState([sent('FAN01 OFF'), response]);
assert.equal(element('commandAck').textContent, '等待 ACK · FAN01 OFF');
context.renderAckState([{event: 'POLICY_ACK', detail: 'v3 APPLIED'}]);
assert.equal(element('policyAck').textContent, 'v3 APPLIED');
console.log('PASS: dashboard ACK waiting, response, telemetry and subsequent command behavior');

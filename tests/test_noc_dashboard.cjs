const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
function node(tagName = '') {
  let content = '';
  return {tagName, className:'', disabled:false, children:[], listeners:{},
    get textContent() {return content;}, set textContent(value) {content=value; this.children=[];},
    appendChild(child) {this.children.push(child);}, addEventListener(type, fn) {this.listeners[type]=fn;}};
}
const nodes = new Map();
const el = id => {if (!nodes.has(id)) nodes.set(id,node()); return nodes.get(id);};
let fail = false;
let controller = {configured:true,source:'PT_CONTROLLER',status:'CONNECTED',url:'http://127.0.0.1:58000/api/v1',observed_at:'fixture-time',topology:{nodes:[],links:[]},devices:[{hostname:'<script>safe text</script>',managementIpAddress:'192.168.30.1',collectionStatus:'Managed',reachabilityStatus:'Unreachable'}]};
let network = {source:{kind:'PT_CONTROLLER'},controller};
const data = () => ({network,security:{port_security:'SECURE',active:false,violations:0,acl:'ACTIVE',port_status:'FORWARDING'},branch:{devices:[]},policy:{campus_version:'campus-1',thermal:{policy_id:'thermal-01',version:1,threshold_c:30,mode:'AUTO'},network:{branch_access:'ALLOW',iot_isolation:true},security:{port_security:'STRICT'}},simulation:{cloud:'ONLINE',edge_connected:false,edge_mode:'AUTO',fan:'ON',state_sync:'NOT_RUN',fan_observation:'LIVE'}});
const intervals = [];
const context = vm.createContext({document:{getElementById:el,createElement:node},AbortSignal:{timeout:()=>({})},setInterval:fn=>intervals.push(fn),fetch:async()=>{if(fail)throw Error('offline'); return {ok:true,json:async()=>data()};}});
vm.runInContext(fs.readFileSync('dashboard/noc.js','utf8'),context);
const settle = () => new Promise(resolve=>setImmediate(resolve));
(async()=>{
  await settle();
  for(const id of ['nocOspf','nocBgp','nocTunnel']) assert.equal(el(id).textContent,'NOT COLLECTED');
  const cards = el('networkDeviceCards');
  assert.equal(cards.children.length,1);
  assert.equal(cards.children[0].children[0].textContent,'<script>safe text</script>');
  assert.equal(cards.children[0].children[1].textContent,'管理 IP：192.168.30.1');
  assert.equal(cards.children[0].children[2].textContent,'控制器状态：Managed');
  assert.equal(cards.children[0].children[3].textContent,'ONLINE');
  assert.match(cards.children[0].children[3].className,/good/);
  assert.equal(el('networkFailure').disabled,true);
  controller.devices=[{hostname:'R-BRANCH',collectionStatus:'Unmanaged',reachabilityStatus:'Reachable'},{hostname:'missing-status'}];
  await intervals[0]();
  assert.equal(cards.children[0].children[3].textContent,'Unmanaged');
  assert.equal(cards.children[1].children[3].textContent,'NOT COLLECTED');
  controller={...controller,status:'UNAVAILABLE',devices:controller.devices,error:'AUTH_FAILED',topology:null};network.controller=controller;
  await intervals[0]();
  assert.equal(cards.children.length,0);
  assert.equal(el('controllerDevices').children.length,0);
  assert.match(el('nocNetworkNotice').textContent,/认证失败/);
  network={source:{kind:'SIMULATED'},controller:{...controller,status:'CONNECTED'}};
  await intervals[0]();
  assert.equal(cards.children.length,0);
  assert.match(el('nocNetworkNotice').textContent,/没有设备健康数据/);
  fail=true;await intervals[0]();
  assert.equal(cards.children.length,0);
  assert.equal(el('nocBgp').textContent,'NOT COLLECTED');
  console.log('PASS: real NC health cards, exact Managed mapping, missing status, no mock/stale data, uncollected protocols');
})().catch(error=>{console.error(error);process.exitCode=1;});

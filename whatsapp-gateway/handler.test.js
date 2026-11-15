import test from 'node:test';
import assert from 'node:assert/strict';
import {createHandler} from './handler.js';
import {Limiter} from './policy.js';
function fixture(answer=async()=> 'أهلين'){
 const seen=new Set(),sent=new Set(),out=[];let active=true;
 const current={user:{id:'bot@s.whatsapp.net'},sendMessage:async(g,m)=>{out.push({g,...m});return{key:{id:'out'}};}};
 const store={claim:k=>{if(seen.has(k))return false;seen.add(k);return true;},sent:k=>sent.has(k),remember:k=>sent.add(k)};
 return{out,stop:()=>{active=false;},handler:createHandler({current,store,groups:new Set(['test@g.us']),limiter:new Limiter(),active:()=>active,answer})};
}
const event=(id='id',group='test@g.us')=>({type:'notify',messages:[{key:{id,remoteJid:group,participant:'user@lid'},messageTimestamp:Date.now()/1000,message:{conversation:'/belong مرحبا'}}]});
test('mock socket sends exactly once and no unauthorized traffic',async()=>{const f=fixture();await f.handler(event());await f.handler(event());await f.handler(event('2','other@g.us'));assert.equal(f.out.length,1);assert.equal(f.out[0].text,'أهلين');});
test('history append is not answered',async()=>{const f=fixture();const e=event();e.type='append';await f.handler(e);assert.equal(f.out.length,0);});
test('pause during generation cancels reply',async()=>{let f;f=fixture(async()=>{f.stop();return 'late';});await f.handler(event());assert.equal(f.out.length,0);});
test('backend outage sends one safe fallback',async()=>{const f=fixture(async()=>{throw Error('private token must not leak');});await f.handler(event());assert.match(f.out[0].text,/عطل/);assert.ok(!f.out[0].text.includes('token'));});
test('flood is limited',async()=>{const f=fixture();for(let i=0;i<10;i++)await f.handler(event(String(i)));assert.equal(f.out.length,4);});

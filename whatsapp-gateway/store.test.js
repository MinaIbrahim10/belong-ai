import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {Store} from './store.js';
function setup(){const dir=mkdtempSync(join(tmpdir(),'belong-'));return {dir,path:join(dir,'session.sqlite'),key:'ab'.repeat(32)};}
test('encrypted auth survives restart and rejects wrong key',async()=>{const {dir,path,key}=setup();try{let s=new Store(path,key);s.set('example',{secret:'do-not-leak',bytes:Buffer.from('binary')});const {state,saveCreds}=s.auth();state.creds.registered=true;saveCreds();await state.keys.set({session:{one:Buffer.from('session')}});s.close();assert.equal(readFileSync(path).includes(Buffer.from('do-not-leak')),false);s=new Store(path,key);assert.equal(s.get('example').secret,'do-not-leak');assert.equal(s.auth().state.creds.registered,true);assert.deepEqual((await s.auth().state.keys.get('session',['one'])).one,Buffer.from('session'));s.close();const wrong=new Store(path,'cd'.repeat(32));assert.throws(()=>wrong.get('example'));wrong.close();}finally{rmSync(dir,{recursive:true});}});
test('deduplication and sent receipts persist without messages',()=>{const {dir,path,key}=setup();try{let s=new Store(path,key);assert.ok(s.claim('hashed-id'));assert.equal(s.claim('hashed-id'),false);s.remember('sent-hash');s.pause(false);s.close();s=new Store(path,key);assert.equal(s.claim('hashed-id'),false);assert.ok(s.sent('sent-hash'));assert.equal(s.paused(),false);s.pause(true);assert.ok(s.paused());s.close();}finally{rmSync(dir,{recursive:true});}});
test('defaults paused and rejects invalid encryption key',()=>{const {dir,path,key}=setup();try{assert.throws(()=>new Store(path,'weak'));const s=new Store(path,key);assert.ok(s.paused());s.close();}finally{rmSync(dir,{recursive:true});}});

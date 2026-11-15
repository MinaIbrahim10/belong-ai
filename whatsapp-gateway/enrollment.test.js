import test from 'node:test';
import assert from 'node:assert/strict';
import {Enrollment} from './enrollment.js';
const message=text=>({key:{remoteJid:'test@g.us'},messageTimestamp:Date.now()/1000,message:{conversation:text}});
test('private enrollment only accepts exact current challenge',()=>{const e=new Enrollment();const {code}=e.start();assert.equal(e.accept(message('random private conversation'),'notify'),false);assert.ok(e.accept(message('/belong enroll '+code),'notify'));assert.equal(e.status().group_id,'test@g.us');assert.equal(e.active(),false);});
test('expired challenge is not accepted',()=>{let now=Date.now();const e=new Enrollment(()=>now);const {code}=e.start();now+=300001;assert.equal(e.accept(message('/belong enroll '+code),'notify'),false);});
test('history cannot enroll a group',()=>{const e=new Enrollment();const {code}=e.start();assert.equal(e.accept(message('/belong enroll '+code),'append'),false);});

import {randomBytes,timingSafeEqual} from 'node:crypto';
import {extract} from './policy.js';
export class Enrollment {
 constructor(clock=Date.now){this.clock=clock;this.pending=null;this.result=null;}
 start(){this.pending={code:randomBytes(12).toString('hex'),until:this.clock()+300000};this.result=null;return this.pending;}
 active(){if(this.pending&&this.pending.until<=this.clock())this.pending=null;return !!this.pending;}
 accept(m,type){
  if(!this.active()||type!=='notify'||m.key?.fromMe||!m.key?.remoteJid?.endsWith('@g.us'))return false;
  const age=this.clock()-Number(m.messageTimestamp)*1000;if(!Number.isFinite(age)||age< -30000||age>120000)return false;
  const actual=Buffer.from(extract(m).text.trim()),expected=Buffer.from('/belong enroll '+this.pending.code);
  if(actual.length!==expected.length||!timingSafeEqual(actual,expected))return false;
  this.result={group_id:m.key.remoteJid,expires:this.clock()+300000};this.pending=null;return true;
 }
 status(){if(this.result?.expires<=this.clock())this.result=null;return this.result||{pending:this.active()};}
}

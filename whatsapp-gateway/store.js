import {DatabaseSync} from 'node:sqlite';
import {randomBytes,createCipheriv,createDecipheriv} from 'node:crypto';
import {mkdirSync,chmodSync} from 'node:fs';
import {dirname} from 'node:path';
import {BufferJSON,initAuthCreds,proto} from '@whiskeysockets/baileys';
export class Store {
 constructor(path,key){
  if(!/^[a-f0-9]{64}$/i.test(key||''))throw new Error('SESSION_KEY must be 32-byte hex');
  this.key=Buffer.from(key,'hex');mkdirSync(dirname(path),{recursive:true,mode:0o700});
  this.db=new DatabaseSync(path);chmodSync(path,0o600);
  this.db.exec('PRAGMA journal_mode=DELETE; CREATE TABLE IF NOT EXISTS auth(k TEXT PRIMARY KEY,v BLOB); CREATE TABLE IF NOT EXISTS seen(k TEXT PRIMARY KEY,expires INTEGER); CREATE TABLE IF NOT EXISTS sent(k TEXT PRIMARY KEY,expires INTEGER); CREATE TABLE IF NOT EXISTS control(k TEXT PRIMARY KEY,v TEXT);');
 }
 seal(value){const iv=randomBytes(12),c=createCipheriv('aes-256-gcm',this.key,iv);const data=Buffer.concat([c.update(JSON.stringify(value,BufferJSON.replacer)),c.final()]);return Buffer.concat([iv,c.getAuthTag(),data]);}
 unseal(value){const b=Buffer.from(value),c=createDecipheriv('aes-256-gcm',this.key,b.subarray(0,12));c.setAuthTag(b.subarray(12,28));return JSON.parse(Buffer.concat([c.update(b.subarray(28)),c.final()]).toString(),BufferJSON.reviver);}
 get(k){const row=this.db.prepare('SELECT v FROM auth WHERE k=?').get(k);return row?this.unseal(row.v):null;}
 set(k,v){if(v==null)this.db.prepare('DELETE FROM auth WHERE k=?').run(k);else this.db.prepare('INSERT OR REPLACE INTO auth VALUES (?,?)').run(k,this.seal(v));}
 auth(){const creds=this.get('creds')||initAuthCreds();return {state:{creds,keys:{get:async(type,ids)=>Object.fromEntries(ids.map(id=>{let v=this.get(type+'-'+id);if(type==='app-state-sync-key'&&v)v=proto.Message.AppStateSyncKeyData.fromObject(v);return[id,v];})),set:async data=>{this.db.exec('BEGIN');try{for(const [t,items]of Object.entries(data))for(const [id,v]of Object.entries(items))this.set(t+'-'+id,v);this.db.exec('COMMIT');}catch(e){this.db.exec('ROLLBACK');throw e;}}}},saveCreds:()=>this.set('creds',creds)};}
 clean(){for(const t of ['seen','sent'])this.db.prepare(`DELETE FROM ${t} WHERE expires < ?`).run(Date.now());}
 claim(k){this.clean();return this.db.prepare('INSERT OR IGNORE INTO seen VALUES (?,?)').run(k,Date.now()+86400000).changes===1;}
 remember(k){this.db.prepare('INSERT OR REPLACE INTO sent VALUES (?,?)').run(k,Date.now()+600000);}
 sent(k){return !!this.db.prepare('SELECT 1 FROM sent WHERE k=? AND expires>?').get(k,Date.now());}
 paused(){return this.db.prepare("SELECT v FROM control WHERE k='paused'").get()?.v!=='false';}
 pause(v){this.db.prepare("INSERT OR REPLACE INTO control VALUES ('paused',?)").run(String(v));}
 close(){this.db.close();}
}

import {createHash} from 'node:crypto';
export const hash = s => createHash('sha256').update(s).digest('hex');
export const normalize = jid => (jid||'').replace(/:\d+@/,'@');
export function extract(m){
 // Deliberately do not unwrap view-once, ephemeral, edited or protocol messages.
 const c=m.message?.extendedTextMessage;
 return {text:m.message?.conversation ?? c?.text ?? '', context:c?.contextInfo ?? {}};
}
export function eligible(m,{groups,botIds,sent,now=Date.now()}){
 const g=m.key?.remoteJid, {text,context}=extract(m);
 if(!g?.endsWith('@g.us') || !groups.has(g) || m.key.fromMe || !m.key.id || !m.key.participant) return false;
 const age=now-Number(m.messageTimestamp)*1000;
 if(!Number.isFinite(age)||age>120000||age < -30000||!text.trim()||text.length>2000) return false;
 const ids=new Set(botIds.filter(Boolean).map(normalize));
 if(ids.has(normalize(m.key.participant))) return false;
 return /^\/belong(?:\s|$)/i.test(text) || (context.mentionedJid||[]).some(j=>ids.has(normalize(j))) ||
   (!!context.stanzaId && sent(g,context.stanzaId) && ids.has(normalize(context.participant)));
}
export function reconnectDelay(code,attempt){
 if([401,403,411,440,500].includes(code)) return null;
 return code===515 ? 1000 : Math.min(60000,1000*2**Math.min(attempt,6));
}
export class Limiter {
 constructor(clock=Date.now){this.clock=clock;this.entries=new Map();}
 take(key,max=4,window=60000){
  const now=this.clock(); for(const [k,v] of this.entries) if(v.end<=now)this.entries.delete(k);
  const v=this.entries.get(key)||{n:0,end:now+window};
  if(v.n>=max || this.entries.size>=2000&&!this.entries.has(key))return false;
  v.n++;this.entries.set(key,v);return true;
 }
}
export async function backendCall(url,token,text,fetcher=fetch){
 const response=await fetcher(url+'/respond',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+token},body:JSON.stringify({text}),signal:AbortSignal.timeout(25000)});
 if(!response.ok)throw new Error('backend_unavailable');
 const body=await response.json();
 if(typeof body.answer!=='string'||!body.answer.trim())throw new Error('invalid_reply');
 return body.answer.slice(0,1800);
}

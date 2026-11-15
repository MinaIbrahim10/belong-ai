import {eligible,extract,hash} from './policy.js';
export function createHandler({current,groups,store,limiter,active,answer,log=()=>{}}){
 let busy=false;
 return async({messages,type})=>{
  if(type!=='notify'||!active())return;
  for(const m of messages){
   const g=m.key?.remoteJid;
   if(!eligible(m,{groups,botIds:[current.user?.id,current.user?.lid],sent:(g,id)=>store.sent(hash(g+':'+id))}))continue;
   if(!store.claim(hash(g+':'+m.key.id)))continue;
   if(busy||!limiter.take(hash(g+':'+m.key.participant))||!limiter.take(hash(g),12)||!limiter.take('global',100,86400000))continue;
   busy=true;
   try{
    let reply;
    try{reply=await answer(extract(m).text.replace(/^\/belong\s*/i,'').replace(/@\d+/g,'').trim()||'مرحبا');}
    catch{reply='صار عندي عطل صغير، جرّب تحكيني بعد شوي.';log('backend_unavailable');}
    if(active()){
     const result=await current.sendMessage(g,{text:reply});
     if(result?.key?.id)store.remember(hash(g+':'+result.key.id));
    }
   }catch{log('send_failed');}finally{busy=false;}
  }
 };
}

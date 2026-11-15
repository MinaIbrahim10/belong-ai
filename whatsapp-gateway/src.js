import makeWASocket,{DisconnectReason} from '@whiskeysockets/baileys';
import pino from 'pino';
import QRCode from 'qrcode';
import {createServer} from 'node:http';
import {timingSafeEqual} from 'node:crypto';
import {createHandler} from './handler.js';
import {Enrollment} from './enrollment.js';
import {Store} from './store.js';
import {eligible,extract,hash,Limiter,backendCall,reconnectDelay} from './policy.js';
process.umask(0o077);
const env=process.env;
for(const k of ['INTERNAL_TOKEN','ADMIN_TOKEN'])if((env[k]||'').length<32)throw Error(k+' requires 32+ characters');
if(env.INTERNAL_TOKEN===env.ADMIN_TOKEN)throw Error('Use distinct tokens');
const groups=new Set((env.TEST_GROUP_IDS||'').split(',').filter(Boolean));
if(env.PRODUCTION_APPROVED==='true')for(const g of (env.PRODUCTION_GROUP_IDS||'').split(',').filter(Boolean))groups.add(g);
const store=new Store(env.SESSION_DB||'/state/session.sqlite',env.SESSION_KEY);
// Protocol logs are disabled: library logs can contain credentials, JIDs and messages.
const silent=pino({level:'silent'});
const log=event=>process.stdout.write(JSON.stringify({time:new Date().toISOString(),event})+'\n');
let socket,qr=null,connected=false,stopped=false,attempt=0,timer;
const cleaner=setInterval(()=>store.clean(),60000);cleaner.unref();
const limiter=new Limiter();
const enrollment=new Enrollment();
function authorized(req){const a=Buffer.from(req.headers.authorization||''),b=Buffer.from('Bearer '+env.ADMIN_TOKEN);return a.length===b.length&&timingSafeEqual(a,b);}
const server=createServer(async(req,res)=>{
 res.setHeader('Cache-Control','no-store');
 if(req.url==='/healthz'){res.writeHead(200,{'Content-Type':'application/json'});return res.end(JSON.stringify({alive:true,connected,paused:store.paused()}));}
 if(!authorized(req)){res.writeHead(401);return res.end();}
 if(req.method==='GET'&&req.url==='/qr'&&qr){res.setHeader('Content-Type','image/png');return res.end(await QRCode.toBuffer(qr));}
 if(req.method==='POST'&&req.url==='/enroll'){if(!store.paused()){res.writeHead(409);return res.end('pause first');}res.setHeader('Content-Type','application/json');return res.end(JSON.stringify(enrollment.start()));}
 if(req.method==='GET'&&req.url==='/enrollment'){res.setHeader('Content-Type','application/json');return res.end(JSON.stringify(enrollment.status()));}
 if(req.method==='POST'&&req.url==='/pause'){store.pause(true);res.end('paused');return;}
 if(req.method==='POST'&&req.url==='/resume'){if(stopped||!groups.size){res.writeHead(409);return res.end('configure groups and restart if disconnected');}store.pause(false);res.end('resumed');return;}
 if(req.method==='POST'&&req.url==='/disconnect'){store.pause(true);stopped=true;clearTimeout(timer);socket?.end(undefined);connected=false;qr=null;res.end('disconnected');return;}
 res.writeHead(404);res.end();
});
server.listen(Number(env.PORT||8080),env.ADMIN_BIND||'127.0.0.1');
async function connect(){
 if(stopped)return;
 const {state,saveCreds}=store.auth();
 socket=makeWASocket({auth:state,logger:silent,syncFullHistory:false,shouldSyncHistoryMessage:()=>false,markOnlineOnConnect:false,shouldIgnoreJid:jid=>jid.endsWith('@g.us')&&!groups.has(jid)&&!enrollment.active(),getMessage:async()=>undefined});
 const current=socket;
 current.ev.on('creds.update',()=>{try{saveCreds();}catch{store.pause(true);stopped=true;current.end(undefined);log('session_save_failed');}});
 current.ev.on('connection.update',u=>{
  if(current!==socket)return;
  if(u.qr){qr=u.qr;log('linking_required');}
  if(u.connection==='open'){connected=true;qr=null;attempt=0;log('connected');}
  if(u.connection==='close'){
   connected=false;qr=null;if(stopped)return;
   const code=u.lastDisconnect?.error?.output?.statusCode;
   const delay=reconnectDelay(code,attempt++);
   if(delay===null||attempt>10){stopped=true;store.pause(true);log('manual_reconnect_required');return;}
   clearTimeout(timer);timer=setTimeout(()=>connect().catch(()=>{stopped=true;log('connect_failed');}),delay);log('reconnecting');
  }
 });
 current.ev.on('messages.upsert',({messages,type})=>{if(store.paused())for(const m of messages)enrollment.accept(m,type);});
 current.ev.on('messages.upsert',createHandler({current,groups,store,limiter,
  active:()=>!stopped&&!store.paused()&&connected&&current===socket,
  answer:text=>backendCall(env.BACKEND_URL||'http://backend:8000',env.INTERNAL_TOKEN,text),log}));
}
process.on('SIGTERM',()=>{stopped=true;clearTimeout(timer);clearInterval(cleaner);socket?.end(undefined);server.close();store.close();process.exit(0);});
if(env.CONNECT_WHATSAPP==='true')connect().catch(()=>{stopped=true;log('connect_failed');});
else log('offline_mode');

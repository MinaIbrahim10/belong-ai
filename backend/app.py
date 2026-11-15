import asyncio, json, os, re, secrets
from pathlib import Path
import httpx
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
ROOT=Path(__file__).resolve().parents[1]
PROMPT=(ROOT/'prompts/belong-system.txt').read_text()
DOCS=json.loads((ROOT/'knowledge/curated.json').read_text())
TOKEN=os.getenv('INTERNAL_TOKEN','')
if len(TOKEN)<32: raise RuntimeError('INTERNAL_TOKEN requires 32+ characters')
app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None)
gate=asyncio.Semaphore(1)
FALLBACK='صار عندي عطل صغير، جرّب تحكيني بعد شوي.'
UNKNOWN='ما عندي مصدر معتمد كافي لهالسؤال حاليا، وما بدي أعطيك جواب لاهوتي من عندي. فينا نراجعه مع مسؤول الشبيبة.'
class Request(BaseModel):
    text: str=Field(min_length=1,max_length=2000)
def curated(text):
    t=text.lower()
    if any(k in t for k in ['تجاهل التعليمات','ignore previous','system prompt','اكشف البرومبت']):
        return 'فيني ساعدك بسؤالك، بس ما بكشف إعدادات داخلية أو محادثات خاصة.'
    if any(k in t for k in ['اجتماع','meeting','جدول']):
        return '😂 صاحي، بس ما عندي جدول اجتماعات موثّق لحتى أعطيك موعد. تأكد من مسؤول الشبيبة.'
    if any(k in t for k in ['ارثوذكس','أرثوذكس','كاثوليك','بروتستانت','طائف','denomination','catholic','orthodox']):
        return 'في اختلافات بين التقاليد المسيحية، وما رح افترض طائفة BELONG. حدد النقطة اللي بدك نقارنها؛ الشرح التفصيلي بحاجة لمراجع معتمدة من كل تقليد.'
    for d in DOCS:
        if any(k in t for k in d['keywords']):return d['answer']+'\nالمصدر: '+d['ref']+' — '+d['source']
    if any(k in t for k in ['يسوع','المسيح','إنجيل','انجيل','الكتاب','آية','معمود','خلاص','ثالوث','لاهوت','bible','jesus','theolog','verse','christ','مريم','قديس','كنيسة','قيامة','الله','god','صلاة','صوم','روح القدس']):return UNKNOWN
    return None
async def generate(text):
    provider=os.getenv('LLM_PROVIDER','disabled')
    if provider=='disabled':return FALLBACK
    key=os.getenv('LLM_API_KEY','')
    if provider=='cloudflare':
        account=os.getenv('CF_ACCOUNT_ID','')
        if not re.fullmatch(r'[a-f0-9]{32}',account):return FALLBACK
        url=f'https://api.cloudflare.com/client/v4/accounts/{account}/ai/v1/chat/completions'
    elif provider=='openai-compatible':
        url=os.environ['LLM_BASE_URL'].rstrip('/')+'/chat/completions'
        if not url.startswith(('https://','http://127.0.0.1:','http://localhost:','http://ollama:')):return FALLBACK
    else:return FALLBACK
    model=os.getenv('LLM_MODEL','@cf/qwen/qwen3.8-27b')
    payload={'model':model,'messages':[{'role':'system','content':PROMPT},{'role':'user','content':text+'\n/no_think'}],'max_tokens':300,'temperature':0.5}
    if provider=='cloudflare':payload['reasoning_effort']='low'
    try:
        async with httpx.AsyncClient(timeout=18,follow_redirects=False) as client:
            # One bounded retry for a transient gateway failure; no retry on quota/auth errors.
            for attempt in range(2):
                response=await client.post(url,headers={'Authorization':'Bearer '+key},json=payload)
                if response.status_code not in (502,503) or attempt:break
                await asyncio.sleep(.3)
            response.raise_for_status()
            answer=response.json()['choices'][0]['message']['content']
            answer=re.sub(r'<think>.*?</think>','',answer,flags=re.S).strip()
            if not answer or '<think>' in answer:return FALLBACK
            # Fail closed on generated quotations/citations; theology uses curated responses.
            if re.search(r'\d+\s*[:：]\s*\d+|https?://|[«»“”"]',answer):return UNKNOWN
            return answer[:1600]
    except (httpx.HTTPError,KeyError,ValueError,TypeError):return FALLBACK
@app.get('/healthz')
def health():return {'alive':True,'provider_configured':os.getenv('LLM_PROVIDER','disabled')!='disabled'}
@app.post('/respond')
async def respond(request:Request,authorization:str=Header(default='')):
    if not secrets.compare_digest(authorization,'Bearer '+TOKEN):raise HTTPException(401)
    answer=curated(request.text)
    if answer:return {'answer':answer,'mode':'curated'}
    if gate.locked():raise HTTPException(429)
    async with gate:
        try:
            answer=await asyncio.wait_for(generate(request.text),timeout=22)
        except TimeoutError:
            answer=FALLBACK
        return {'answer':answer,'mode':'generated-or-fallback'}

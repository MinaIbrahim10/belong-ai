"""Optional Colab GPU experiment, not executed or permanent hosting.
Install torch transformers accelerate. Run separately for each model.
Only synthetic prompts are used; no WhatsApp session or keys belong in Colab.
"""
import argparse,json,time
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
p=argparse.ArgumentParser();p.add_argument('--model',choices=['Qwen/Qwen3-1.7B','Qwen/Qwen3-4B'],required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1]
tokenizer=AutoTokenizer.from_pretrained(a.model)
model=AutoModelForCausalLM.from_pretrained(a.model,torch_dtype='auto',device_map='auto')
rows=[]
for case in json.loads((root/'tests/model_cases.json').read_text()):
    text=tokenizer.apply_chat_template([{'role':'system','content':(root/'prompts/belong-system.txt').read_text()},{'role':'user','content':case['text']}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    inputs=tokenizer(text,return_tensors='pt').to(model.device)
    if torch.cuda.is_available():torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats()
    start=time.perf_counter()
    with torch.inference_mode():out=model.generate(**inputs,max_new_tokens=200,do_sample=False)
    if torch.cuda.is_available():torch.cuda.synchronize()
    rows.append({**case,'model':a.model,'seconds':time.perf_counter()-start,'output':tokenizer.decode(out[0][inputs.input_ids.shape[1]:],skip_special_tokens=True),'peak_vram_bytes':torch.cuda.max_memory_allocated() if torch.cuda.is_available() else None,'human_score':None})
Path('benchmark-'+a.model.split('/')[-1]+'.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))

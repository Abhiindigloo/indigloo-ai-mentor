# /// script
# requires-python = ">=3.10"
# dependencies = ["torch==2.8.0", "trl==0.23.1", "transformers==4.56.2", "peft==0.17.1", "accelerate==1.10.1", "datasets==4.1.1", "trackio==0.7.0"]
# ///
"""Hugging Face Jobs LoRA pilot. Saves private Hub checkpoints. No child records."""
import json
import os
from pathlib import Path
from urllib.request import urlopen
import torch
import trackio
from datasets import Dataset
from huggingface_hub import HfApi
from peft import LoraConfig
from trl import SFTConfig, SFTTrainer

repo=os.environ.get('HUB_MODEL_ID','AGIbuild/indigloo-mentor-qwen-0.5b-pilot')
token=os.environ['HF_TOKEN']
# Fail BEFORE model loading/training if the token cannot persist results.
api=HfApi(token=token)
api.create_repo(repo_id=repo,repo_type='model',private=True,exist_ok=True)

def read(split):
    if 'INLINE_DATA' in globals(): return INLINE_DATA[split]
    local=Path(__file__).with_name(split+'.jsonl')
    if local.exists(): raw=local.read_text()
    else:
        base=os.environ['DATA_BASE_URL']  # immutable GitHub commit URL
        with urlopen(base+'/'+split+'.jsonl',timeout=30) as r: raw=r.read().decode()
    rows=[json.loads(line) for line in raw.splitlines() if line.strip()]
    assert rows and all(r['prompt'] and r['completion'] for r in rows)
    return rows
train,validation=read('train'),read('eval')
assert not {r['topic'] for r in train}&{r['topic'] for r in validation}
config=SFTConfig(
    output_dir='/tmp/mentor-output',hub_model_id=repo,hub_private_repo=True,
    push_to_hub=True,hub_strategy='every_save',
    num_train_epochs=2,per_device_train_batch_size=1,per_device_eval_batch_size=1,
    gradient_accumulation_steps=8,learning_rate=1e-4,max_length=768,
    completion_only_loss=True,gradient_checkpointing=True,
    fp16=True,bf16=False,logging_steps=1,save_steps=10,save_total_limit=2,
    eval_strategy='epoch',report_to='trackio',project='indigloo-mentor-pilot',
    run_name='qwen05b-en-hi-lora',seed=42,
)
trainer=SFTTrainer(
    model='Qwen/Qwen2.5-0.5B-Instruct',args=config,
    train_dataset=Dataset.from_list(train).select_columns(['prompt','completion']),
    eval_dataset=Dataset.from_list(validation).select_columns(['prompt','completion']),
    peft_config=LoraConfig(r=8,lora_alpha=16,lora_dropout=.05,task_type='CAUSAL_LM',target_modules=['q_proj','v_proj']),
)
trainer.train()
metrics=trainer.evaluate()
trainer.save_model()
trainer.processing_class.save_pretrained(config.output_dir)
Path(config.output_dir,'eval_metrics.json').write_text(json.dumps(metrics,indent=2))
Path(config.output_dir,'README.md').write_text('''---
base_model: Qwen/Qwen2.5-0.5B-Instruct
library_name: peft
license: apache-2.0
language: [en, hi]
tags: [education, lora, experimental]
---
# Indigloo Mentor pilot adapter
Synthetic style-tuning pilot on illustrative lessons. Not a validated school tutor.
Hindi quality, factuality, and device memory have not been independently validated.
Topic-separated evaluation loss is a smoke check, not an education quality score.
Use with passage retrieval and teacher review. Do not deploy autonomously to children.
''')
api.upload_folder(repo_id=repo,folder_path=config.output_dir)
trackio.finish()
print('Saved private pilot adapter: https://huggingface.co/'+repo)

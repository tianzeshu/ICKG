"""Print one record from a published task split using only the standard library."""
import argparse,gzip,json
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--task',choices=['ner','re','ed'],default='ner');ap.add_argument('--split',choices=['train','dev','test'],default='train');a=ap.parse_args()
root=Path(__file__).resolve().parents[1]
path=root/'data'/'experimental'/a.task
if a.task=='ed':path=path/'inputs'
with gzip.open(path/(a.split+'.jsonl.gz'),'rt',encoding='utf-8') as f:record=json.loads(next(f))
print(json.dumps(record,ensure_ascii=False,indent=2))

"""Evaluate complete mention-cluster predictions using mention-averaged B-cubed."""
import argparse,gzip,json
from collections import Counter
from pathlib import Path

def rows(path):
    opener=gzip.open if str(path).endswith('.gz') else open
    with opener(path,'rt',encoding='utf-8') as f:
        for line in f:
            if line.strip():yield json.loads(line)

def mapping(path,cluster_key):
    result={}
    for r in rows(path):
        mid=r['mention_id'];cid=r[cluster_key]
        if not isinstance(mid,str) or not mid:raise ValueError('mention_id must be a nonempty string')
        if not isinstance(cid,(str,int)) or isinstance(cid,bool):raise ValueError('cluster identifiers must be strings or integers')
        if mid in result:raise ValueError('Duplicate mention_id: '+mid)
        result[mid]=(type(cid).__name__,cid)
    if not result:raise ValueError('Empty evaluation input')
    return result

def score(gold,pred):
    if set(gold)!=set(pred):
        missing=set(gold)-set(pred);extra=set(pred)-set(gold)
        raise ValueError(f'Mention sets differ: missing={len(missing)}, extra={len(extra)}')
    gc=Counter(gold.values());pc=Counter(pred.values());overlap=Counter((gold[m],pred[m]) for m in gold)
    p=sum(overlap[(gold[m],pred[m])]/pc[pred[m]] for m in gold)/len(gold)
    r=sum(overlap[(gold[m],pred[m])]/gc[gold[m]] for m in gold)/len(gold)
    return {'mentions':len(gold),'gold_clusters':len(gc),'predicted_clusters':len(pc),'B3-P':100*p,'B3-R':100*r,'B3-F1':100*(2*p*r/(p+r) if p+r else 0.0),'unit':'percent','protocol':'all mentions including singletons; mention-averaged P/R followed by harmonic F1'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--gold',required=True,type=Path);ap.add_argument('--pred',required=True,type=Path);ap.add_argument('--output',type=Path);a=ap.parse_args()
    result=score(mapping(a.gold,'entity_id'),mapping(a.pred,'cluster_id'));text=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:a.output.write_text(text+'\n',encoding='utf-8')
    print(text)

if __name__=='__main__':main()

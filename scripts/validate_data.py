"""Check the organized task datasets using the Python standard library."""
from pathlib import Path
from collections import Counter
import json,gzip,hashlib,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]

def rows(p):
    with gzip.open(p,'rt',encoding='utf-8') as f:
        for line in f:
            if line.strip():yield json.loads(line)

def require(condition,message):
    if not condition:raise ValueError(message)

def check_hashes(folder):
    checked=0
    for line in (folder/'checksums.sha256').read_text(encoding='utf-8').splitlines():
        if not line.strip():continue
        digest,name=line.split(None,1);p=(folder/name.strip().lstrip('*')).resolve()
        require(p.is_relative_to(folder.resolve()),'Checksum path outside dataset')
        require(hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==digest,'Checksum mismatch: '+str(p));checked+=1
    return checked

def main():
    report={'hash_files_checked':0,'tasks':{}}
    base=ROOT/'data/experimental'
    for task in ['ner','re','ed','tkg']:report['hash_files_checked']+=check_hashes(base/task)
    nerids=set();texts={};totals=Counter();nertotals={}
    for split in ['train','dev','test']:
        docs=spans=0;current=set()
        for d in rows(base/'ner'/(split+'.jsonl.gz')):
            require(d['id'] not in nerids,'Repeated NER document ID');nerids.add(d['id']);docs+=1;current.add(d['text'])
            localids={e['eid'] for e in d['entities']}
            for e in d['entities']:
                a,b=e['start'],e['end'];require(0<=a<b<=len(d['text']) and d['text'][a:b]==e['mention'],'NER span mismatch');spans+=1
            for r in d.get('relations',[]):require(r['head'] in localids and r['tail'] in localids,'NER relation endpoint missing')
        nertotals[split]={'documents':docs,'entity_spans':spans};texts[split]=current;totals['documents']+=docs;totals['entity_spans']+=spans
    require(tuple((v['documents'],v['entity_spans']) for v in nertotals.values())==((4221,72742),(1206,20642),(603,10588)),'NER counts mismatch')
    for a,b in [('train','dev'),('train','test'),('dev','test')]:require(not texts[a]&texts[b],'NER exact text overlaps across splits')
    report['tasks']['ner']={'splits':nertotals,'total':dict(totals)}
    labels=set();retotals={};sentences={}
    for split in ['train','dev','test']:
        count=0;current=set()
        for r in rows(base/'re'/(split+'.jsonl.gz')):
            require(all(isinstance(r[k],str) for k in ['head','head_type','relation','tail','tail_type','sentence']),'RE required string missing');labels.add(r['relation']);current.add(r['sentence']);count+=1
        retotals[split]=count;sentences[split]=current
    require(list(retotals.values())==[5669,1620,810] and len(labels)==196,'RE counts mismatch')
    for a,b in [('train','dev'),('train','test'),('dev','test')]:require(not sentences[a]&sentences[b],'RE evidence sentence overlaps across splits')
    report['tasks']['re']={'samples':retotals,'raw_relation_labels':len(labels)}
    global_targets=set();global_entities=set();edcounts={}
    for split in ['train','dev','test']:
        inputs={};docids=set();docs=0
        for d in rows(base/'ed/inputs'/(split+'.jsonl.gz')):
            docs+=1;require(d['document_id'] not in docids,'Repeated ED document');docids.add(d['document_id'])
            for m in d['mentions']:
                require('entity_id' not in m and 'canonical_name' not in m,'ED reference identity in input')
                require(d['text'][m['start']:m['end']]==m['mention'],'ED span mismatch')
                require(m['mention_id'] not in inputs,'Repeated ED mention');inputs[m['mention_id']]=(d['document_id'],m['type'])
        seen=set();clusters=set()
        for r in rows(base/'ed/labels'/(split+'.jsonl.gz')):
            mid=r['mention_id'];require(mid not in seen and mid in inputs,'ED target missing or repeated');seen.add(mid)
            require(inputs[mid]==(r['document_id'],r['type']),'ED input/target mismatch');clusters.add(r['entity_id']);global_entities.add(r['entity_id'])
        require(seen==set(inputs),'ED labels do not cover all input mentions');require(not global_targets&seen,'ED mention ID across splits');global_targets.update(seen)
        edcounts[split]={'documents':docs,'mentions':len(seen),'clusters':len(clusters)}
    require([(v['documents'],v['mentions'],v['clusters']) for v in edcounts.values()]==[(1250,9819,4981),(357,2802,1741),(178,1410,716)],'ED counts mismatch')
    require(len(global_entities)==6424,'ED global identity count mismatch')
    catalog={r['entity_id'] for r in rows(base/'ed/reference/entity_catalog.jsonl.gz')};require(catalog==global_entities,'ED reference directory mismatch')
    report['tasks']['ed']={'splits':edcounts,'global_reference_entities':len(global_entities)}
    status=json.loads((base/'tkg/status.json').read_text(encoding='utf-8'));report['tasks']['tkg']=status
    resources=ROOT/'resources/global_semiconductor_entities';report['hash_files_checked']+=check_hashes(resources)
    subprocess.run([sys.executable,str(resources/'validate_catalog.py'),str(resources)],check=True)
    report['status']='passed';print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()

"""Check the compressed independent product catalog using the Python standard library."""
import argparse
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

from catalog_rules import initial_manufacturer, maker_key, model_key


def read_jsonl(path):
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt',encoding='utf-8') as stream:
        for line in stream:
            if line.strip():yield json.loads(line)


def validate(directory):
    directory=Path(directory)
    stats=json.loads((directory/'statistics.json').read_text(encoding='utf-8'))
    registry={r['source_id']:r for r in read_jsonl(directory/'source_manifest.jsonl')}
    data=directory/'entity_catalog.jsonl.gz'
    with data.open('rb') as stream:
        compressed_sha=hashlib.file_digest(stream,'sha256').hexdigest()
    assert compressed_sha==stats['distribution_sha256'],'Compressed file SHA-256 mismatch'
    ids=set();keys=set();manufacturers=set();counts=Counter();uncompressed=hashlib.sha256()
    with gzip.open(data,'rb') as stream:
        for raw in stream:
            uncompressed.update(raw)
            r=json.loads(raw)
            key=(maker_key(r['manufacturer']),model_key(r['canonical_name']))
            expected='GSIC_'+hashlib.sha256(('GSIC|'+key[0]+'|'+key[1]).encode()).hexdigest()[:20]
            assert r['entity_id']==expected,'Unstable entity ID'
            assert r['entity_id'] not in ids and key not in keys,'Duplicate entity'
            ids.add(r['entity_id']);keys.add(key);manufacturers.add(r['manufacturer'])
            assert r['type']=='Product' and r['human_verified'] is False
            assert r['mention_ids']==[] and r['document_ids']==[] and r['splits']==[]
            assert r['canonical_name'] in r['surface_forms']
            assert all(model_key(form)==key[1] for form in r['surface_forms'])
            assert r['sources'] and sum(r['annotation_methods'].values())==len(r['sources'])
            for source in r['sources']:
                assert source['source_id'] in registry,'Unresolved source reference'
                assert source['source_url'].startswith('https://')
                assert model_key(source['name_as_published'])==key[1]
                assert maker_key(initial_manufacturer(source['manufacturer_as_published']))==key[0]
                assert source['human_verified'] is False
                assert source['verification_level'] in {'public_catalog_record_snapshot_verified','official_sitemap_url_only'}
                counts['source_references']+=1
            counts['entities']+=1
    assert counts['entities']==215708==stats['entity_count']
    assert len(manufacturers)==770==stats['manufacturer_count']
    assert counts['source_references']==stats['source_references']
    assert uncompressed.hexdigest()==stats['uncompressed_sha256']==stats['entity_catalog_sha256']
    for manifest in registry.values():
        snapshot=Path(manifest['snapshot_file'])
        assert not snapshot.is_absolute() and '..' not in snapshot.parts
        assert manifest['download_url'].startswith('https://')
        assert len(manifest['snapshot_sha256'])==64
    checks=directory/'checksums.sha256'
    if checks.exists():
        for line in checks.read_text(encoding='utf-8').splitlines():
            digest,relative=line.split('  ',1)
            path=(directory/relative).resolve()
            assert path.is_relative_to(directory.resolve())
            with path.open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
            assert actual==digest,'Checksum mismatch: '+relative
    return {'status':'passed','entities':counts['entities'],'unique_entity_ids':len(ids),
            'unique_manufacturer_model_pairs':len(keys),'manufacturers':len(manufacturers),
            'source_references':counts['source_references'],'source_snapshots_listed':len(registry),
            'uncompressed_sha256':uncompressed.hexdigest(),'compressed_sha256':compressed_sha,
            'human_verified_records':0,'source_files_included':False,
            'scope':'counts, identities, fields, provenance references and released file hashes; no individual human engineering-fact verification'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',nargs='?',type=Path,default=Path(__file__).resolve().parent)
    args=parser.parse_args()
    print(json.dumps(validate(args.directory),ensure_ascii=False,indent=2))

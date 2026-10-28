"""Restore only the reviewed publication paths, checking every complete-file hash."""
from pathlib import Path
import hashlib,json,os,shutil,sys
def main():
 root=Path.cwd().resolve();source=Path(sys.argv[1]).resolve();expected=sys.argv[2]
 raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
 manifest=json.loads(raw);assert manifest['repository']=='tianzeshu/ICKG'
 allowed={'.gitattributes','.gitignore','README.md','CITATION.cff','DATA_USE.md'}
 total=0
 for item in manifest['files']:
  name=item['path'];rel=Path(name)
  assert not rel.is_absolute()and'..'not in rel.parts
  assert name in allowed or rel.parts[0]in {'data','docs'}
  dest=(root/rel).resolve();assert dest.is_relative_to(root)
  dest.parent.mkdir(parents=True,exist_ok=True);tmp=dest.with_name(dest.name+'.restore-tmp')
  digest=hashlib.sha256();count=0
  with tmp.open('wb')as out:
   for part in item['parts']:
    p=(root/part).resolve()
    assert p.is_relative_to(root/'.transport')and p.is_file()and not p.is_symlink()
    with p.open('rb')as inp:
     while True:
      block=inp.read(1024*1024)
      if not block:break
      out.write(block);digest.update(block);count+=len(block)
  assert digest.hexdigest()==item['sha256']and count==item['bytes'],name
  tmp.replace(dest);total+=count
  print('Verified '+name,flush=True)
 transport=root/'.transport';assert transport.is_dir()and not transport.is_symlink()
 shutil.rmtree(transport)
 summary='Verified '+str(len(manifest['files']))+' publication files ('+str(total)+' bytes).'
 if os.environ.get('GITHUB_STEP_SUMMARY'):
  with open(os.environ['GITHUB_STEP_SUMMARY'],'a',encoding='utf-8')as f:f.write(summary+'\n')
 print(summary)
if __name__=='__main__':main()

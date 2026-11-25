import sys,json,urllib.parse as u
res,man,out=sys.argv[1:4]
t=open(res).read(); d=json.loads(t[t.index('{'):])
if isinstance(d,list): d=json.loads(d[0]['text'])
ref2pid={l.split('\t')[1].strip():l.split('\t')[0] for l in open(man) if '\t' in l}
lines=[];cred=tok=None
for f in d['files']:
    url=f['url'].split('#')[0]; p=u.urlsplit(url)
    q=dict(x.split('=',1) for x in p.query.split('&'))
    seg=p.path.strip('/').split('/')
    cred=cred or q['X-Amz-Credential']; tok=tok or q['X-Amz-Security-Token']
    assert q['X-Amz-Security-Token']==tok
    lines.append(f"{ref2pid[f['reference']]} {seg[1]} {seg[2]} {q['X-Amz-Date']} {q['X-Amz-Signature']}")
open(out,'w').write(f"CRED={cred}\nTOKEN={tok}\n"+"\n".join(lines)+"\n")
print(len(lines),'files; unresolved:',d.get('unresolved'))

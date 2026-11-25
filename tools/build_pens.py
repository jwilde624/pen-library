# Build the Pen Library data + photo bundles.
# usage: python3 -I build_pens.py <pen_rows.jsonl> <manifest.json> <photo_webp_dir> <site_dir> <YYYY-MM-DD>
#  pen_rows.jsonl : one JSON object per row from the Notion view "Public · Pen Library" (keys: id, Pen Name, Brand,
#                   Color/Description, Gifted, Active, For Sale, For Sale Price (shipped), Inkings ...)
#  Only pens with Active or For Sale checked are published. Cost, dates and store are never published.
#  photo_webp_dir : <page id>.webp (480x240, from pencrop.py) for ids whose bundle entry should be (re)built
#  site_dir       : folder holding index.html and photos/b-*.json (existing bundles are kept and updated)
import sys,json,re,os,glob,base64,html
rows_f,man_f,wdir,site,today=sys.argv[1:6]
rows=[json.loads(l) for l in open(rows_f) if l.strip()]
yes=lambda v: v=='__YES__'
rows=[r for r in rows if yes(r.get('Active')) or yes(r.get('For Sale'))]
def clean(s):
    s=re.sub(r'<[^>]+>','',str(s or '')); s=html.unescape(s); s=re.sub(r'\\([\[\]\\*_#()`~>|-])',r'\1',s)
    return re.sub(r'\s+',' ',s).strip()
def arr(v):
    try: return json.loads(v) if v else []
    except Exception: return []
bpath=lambda k: os.path.join(site,'photos',f'b-{k}.json')
os.makedirs(os.path.join(site,'photos'),exist_ok=True)
B={k:(json.load(open(bpath(k))) if os.path.exists(bpath(k)) else {}) for k in '0123456789abcdef'}
for f in glob.glob(os.path.join(wdir,'*.webp')):
    pid=os.path.basename(f)[:-5]
    B[pid[-1]][pid]='data:image/webp;base64,'+base64.b64encode(open(f,'rb').read()).decode()
ids={r['id'] for r in rows}
for k in B: B[k]={i:v for i,v in B[k].items() if i in ids}
have={i for k in B for i in B[k]}
out=[]
for r in rows:
    price=r.get('For Sale Price (shipped)')
    try: price=float(price) if price not in (None,'') else 0
    except Exception: price=0
    if price==int(price): price=int(price)
    out.append([clean(r.get('Pen Name')),clean(r.get('Brand')),clean(r.get('Color/Description')),
        1 if yes(r.get('Gifted')) else 0, 1 if yes(r.get('For Sale')) else 0, price,
        len(arr(r.get('Inkings'))), r['id'] if r['id'] in have else ''])
data=json.dumps({'updated':today,'pens':out},ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
p=os.path.join(site,'index.html'); h=open(p).read()
m=re.search(r'(<script id="pen-data" type="application/json">)(.*?)(</script>)',h,re.S)
h=h[:m.start(2)]+data+h[m.end(2):]; open(p,'w').write(h)
for k in B: json.dump(B[k],open(bpath(k),'w'),separators=(',',':'))
tot=sum(os.path.getsize(bpath(k)) for k in B)
print(f'{len(out)} pens ({sum(x[4] for x in out)} for sale), {len(have)} with photos; bundles {tot/1e6:.2f} MB')

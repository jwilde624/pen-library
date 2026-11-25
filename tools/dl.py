# usage: python3 -I dl.py <batchfile> <rawdir>
# batchfile format:
#   line1: CRED=<X-Amz-Credential value, as in the URL>
#   line2: TOKEN=<X-Amz-Security-Token value, as in the URL>
#   then one line per file: <pageid> <space-id/file-uuid> <filename-as-in-url> <X-Amz-Date> <X-Amz-Signature>
#   e.g. 2bebd8456e8680408888c614383f6964 d621ea4e-450f-449e-8b87-27360936d66c image.png 20261113T181602Z 8c5ac205...
import sys,subprocess,os
bf,raw=sys.argv[1],sys.argv[2]; os.makedirs(raw,exist_ok=True)
L=[l.strip() for l in open(bf) if l.strip()]
cred=L[0].split('=',1)[1]; tok=L[1].split('=',1)[1]
procs=[]
for l in L[2:]:
    pid,fid,name,date,sig=l.split()
    url=(f"https://prod-files-secure.s3.us-west-2.amazonaws.com/ef47ae62-2127-4341-8134-a5eba33b221f/{fid}/{name}"
         f"?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential={cred}"
         f"&X-Amz-Date={date}&X-Amz-Expires=300&X-Amz-Security-Token={tok}&X-Amz-Signature={sig}"
         f"&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject")
    procs.append((pid,subprocess.Popen(['curl','-sS','-o',f'{raw}/{pid}.img','-w','%{http_code}',url],stdout=subprocess.PIPE,stderr=subprocess.PIPE)))
for pid,p in procs:
    out,err=p.communicate(); code=out.decode()
    if code!='200': print('FAIL',pid,code,err.decode()[:200]); 
    else: print('ok',pid)

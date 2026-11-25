# Fit the whole pen into a 2:1 thumbnail.
# usage: python3 -I pencrop.py <raw_dir with <id>.img> <out_dir>   -> <out_dir>/<id>.webp (480x240)
# Plain/light backgrounds: trim to the pen (+margin) and pad to 2:1 with the photo's own background colour.
# Busy backgrounds: centre crop to 2:1.
import sys,glob,os,numpy as np,cv2
from PIL import Image
src,dst=sys.argv[1],sys.argv[2]; os.makedirs(dst,exist_ok=True)
W,H=480,240
def process(path):
    im=Image.open(path); im=im.convert('RGB'); w,h=im.size
    a=np.asarray(im).astype(np.int16)
    k=max(4,min(w,h)//25)
    corners=np.concatenate([a[:k,:k].reshape(-1,3),a[:k,-k:].reshape(-1,3),a[-k:,:k].reshape(-1,3),a[-k:,-k:].reshape(-1,3)])
    bg=np.median(corners,0); spread=np.abs(corners-bg).max(1)
    uniform=np.percentile(spread,85)<28 and bg.mean()>150
    if uniform:
        d=np.abs(a-bg).max(2)
        m=(d>38).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,_=cv2.connectedComponentsWithStats(m)
        keep=np.zeros_like(m)
        area_min=w*h*0.0004
        for i in range(1,n):
            if st[i,4]>=area_min: keep[lab==i]=1
        ys,xs=np.where(keep>0)
        if len(xs)>50:
            x0,x1=np.percentile(xs,[0.2,99.8]); y0,y1=np.percentile(ys,[0.2,99.8])
            bw,bh=x1-x0,y1-y0; pad=0.08*max(bw,bh)
            x0-=pad;x1+=pad;y0-=pad;y1+=pad
            cx,cy=(x0+x1)/2,(y0+y1)/2; bw,bh=x1-x0,y1-y0
            if bw/bh<2: bw=bh*2
            else: bh=bw/2
            box=(int(cx-bw/2),int(cy-bh/2),int(cx+bw/2),int(cy+bh/2))
            l,t,r,b=max(0,-box[0]),max(0,-box[1]),max(0,box[2]-w),max(0,box[3]-h)
            arr=cv2.copyMakeBorder(np.asarray(im),t,b,l,r,cv2.BORDER_REPLICATE)
            crop=arr[box[1]+t:box[3]+t, box[0]+l:box[2]+l]
            return Image.fromarray(crop).resize((W,H),Image.LANCZOS)
    # busy background: centre crop 2:1
    if w/h>2: nw=h*2; box=((w-nw)//2,0,(w+nw)//2,h)
    else: nh=w//2; box=(0,(h-nh)//2,w,(h+nh)//2)
    return im.crop(box).resize((W,H),Image.LANCZOS)
for f in sorted(glob.glob(os.path.join(src,'*.img'))):
    pid=os.path.basename(f)[:-4]
    try: process(f).save(os.path.join(dst,pid+'.webp'),quality=76,method=6)
    except Exception as e: print('FAIL',pid,e)

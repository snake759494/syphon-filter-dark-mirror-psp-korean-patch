"""영어 UI 텍스처 -> 한글 재작성. 결과: trans/tex/<원본md5>.tdx"""
import sys, os, glob, hashlib
sys.path.insert(0,os.path.dirname(__file__))
import tdx
from PIL import Image, ImageDraw, ImageFont
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
TTF=os.path.join(R,'work','fonts','ttf')
def F(n,s): return ImageFont.truetype(os.path.join(TTF,n) if not n.startswith('Nanum') else os.path.join(R,n), s)
def bbox_text(d,txt,ft): b=d.textbbox((0,0),txt,font=ft); return b
def put(im,txt,ft,cx,cy,fill):
    d=ImageDraw.Draw(im); b=d.textbbox((0,0),txt,font=ft)
    d.text((cx-(b[0]+b[2])//2, cy-(b[1]+b[3])//2),txt,font=ft,fill=fill)
def card_like(im,txt,xr):
    w,h=im.size; px=im.load()
    ys=[y for y in range(h) for x in range(xr) if px[x,y][0]>128]
    y0,y1=min(ys),max(ys)
    d=ImageDraw.Draw(im); d.rectangle((1,y0,xr,y1),fill=(0,0,0,255))
    put(im,txt,F('Galmuri11-Bold.ttf',12),(1+xr)//2,(y0+y1)//2+1,(255,255,255,255))
    return im
def stripe(im,txt,cx,lim=14):
    w,h=im.size; px=im.load()
    pts=[(x,y) for y in range(h) for x in range(w-lim) if px[x,y][0]>150]
    y0=min(y for x,y in pts); y1=max(y for x,y in pts)
    for y in range(max(0,y0-1),min(h,y1+2)):
        c=min((px[x,y] for x in (1,2,3)),key=lambda q:q[0])
        if c[0]>80: c=(37,37,37,255)
        for x in range(1,w-lim):
            if px[x,y][0]>60 or abs(y-y0)<1: px[x,y]=c
    put(im,txt,F('Galmuri11-Bold.ttf',12),cx,(y0+y1)//2+1,(255,255,255,255))
    return im
def iscan(im): return stripe(im,'i-스캔',27,7)
def more(im):
    im=Image.new('RGBA',im.size,(0,0,0,0))
    put(im,'더보기',F('Galmuri7.ttf',8),15,4,(255,255,255,255)); return im
def classified(im):
    w,h=im.size; px=im.load()
    # 어두운(글자) 픽셀을 주변 밝은 배경색으로
    bg=sorted(px[x,y] for x in range(10,w-10) for y in range(8,h-8))[len(range(10,w-10))*len(range(8,h-8))*3//4]
    for y in range(4,h-3):
        for x in range(4,w-4):
            if sum(px[x,y][:3])<sum(bg[:3])*0.8: px[x,y]=bg
    st=Image.new('RGBA',(110,40),(0,0,0,0)); d=ImageDraw.Draw(st)
    dark=(20,60,20,255)
    d.rectangle((2,2,107,37),outline=dark,width=3)
    put(st,'기  밀',F('NanumSquareNeo-eHv.ttf',24),55,21,dark)
    st=st.rotate(-8,resample=Image.BICUBIC,expand=True)
    im.alpha_composite(st,(w//2-st.width//2,h//2-st.height//2-2))
    return im
JOBS={'CARD':lambda im:card_like(im,'카드',50),'CODE':lambda im:stripe(im,'코드',25),'ISCAN':iscan,'MORE':more,'MISSION_UNVAILABLE':classified}
for f in glob.glob(os.path.join(R,'work','tex','*.tdx')):
    nm,h=os.path.basename(f)[:-4].rsplit('_',1); b=open(f,'rb').read()
    full=hashlib.md5(b).hexdigest()
    im=tdx.decode(b,True)[0]; im2=JOBS[nm](im.copy())
    nb=tdx.encode_like(b,im2)
    open(os.path.join(R,'trans','tex',full+'.tdx'),'wb').write(nb)
    tdx.decode(nb,True)[0].resize((im.width*4,im.height*4),0).save(os.path.join(R,'work','tex','ko_'+nm+'.png'))
    print(nm,full)

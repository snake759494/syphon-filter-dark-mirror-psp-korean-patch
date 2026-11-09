"""한글 글리프를 4개 FNT에 추가하고 TDX 페이지(4bpp 256x256 swizzled)를 생성.
코드: k번째 음절 -> lead=0xE0+k//80, trail=0x80+k%80 ; idx=(lead<<7)+trail-0x6FC0"""
import struct, sys, json, os
from PIL import Image, ImageFont, ImageDraw
sys.path.insert(0,os.path.dirname(__file__))
import fnt, tdx, hog
ROOT=os.path.join(os.path.dirname(__file__),'..')
TTF=os.path.join(ROOT,'work','fonts','ttf')
PAGE=256
def code_of(k): return bytes([0xE0+k//80, 0x80+k%80])
def idx_of(k):
    l,t=code_of(k); return (l<<7)+t-0x6FC0
# 폰트별 설정: ttf, size, shear(이탤릭 px/행), bold(가로 1px 덧칠), aa
CFG={
 'DEFAULT': dict(ttf=os.path.join(TTF,'Galmuri11.ttf'), size=12, shear=0, aa=False, adv_extra=0, lineh=13),
 'CALLOUT': dict(ttf=os.path.join(TTF,'Galmuri11.ttf'), size=12, shear=0, aa=False, adv_extra=0, lineh=13),
 'TINYFNT': dict(ttf=os.path.join(TTF,'Galmuri9.ttf'), size=10, shear=0, aa=False, adv_extra=0),
 'LARGEFNT':dict(ttf=os.path.join(ROOT,'NanumSquareNeo-cBd.ttf'), size=17, shear=0.2, aa=True, adv_extra=1),
}
def render_glyph(ch, c):
    ft=ImageFont.truetype(c['ttf'], c['size'])
    asc,desc=ft.getmetrics()
    W=c['size']*3; H=c['size']*3
    im=Image.new('L',(W,H),0); dr=ImageDraw.Draw(im)
    if not c['aa']: dr.fontmode='1'
    ox,oy=c['size'],c['size']
    dr.text((ox,oy),ch,font=ft,fill=255)
    if c['shear']:
        # 기준선(oy+asc) 기준 기울임: x' = x + shear*(base-y)
        base=oy+asc; sh=c['shear']
        im=im.transform(im.size, Image.AFFINE, (1, sh, -sh*base, 0,1,0), resample=Image.BILINEAR if c['aa'] else Image.NEAREST)
    bb=im.getbbox()
    adv=int(round(ft.getlength(ch)))+c['adv_extra']
    if bb is None: return None, 0,0, adv
    g=im.crop(bb)
    # 원점 기준 xoff, yoff(=기준선-윗변)
    xoff=bb[0]-ox; top=bb[1]; yoff=(oy+asc)-top
    return g, xoff, yoff, adv
def to4(g):
    return g.point(lambda v: (v*15+127)//255)
def build_font(name, orig_fnt, orig_page0, chars, out_dir):
    """returns (fnt bytes, {pagename: tdx bytes})"""
    c=CFG[name]; f=fnt.read(orig_fnt)
    gl=f['glyphs']
    base_y=f['hdr'][1]
    if 'lineh' in c: f['hdr'][0]=c['lineh']
    # 트레일 단독(0x80..0xCF -> idx 0x60..0xAF) 0폭, 0xC0까지 채움
    for i in range(0x60,0xB0):
        if i<len(gl): gl[i]=[0,0,0,0,0,0,0,0]
    while len(gl)<0xC0: gl.append([0,0,0,0,0,0,0,0])
    pages=[]; cur=None; x=y=0; rowh=0
    def newpage():
        nonlocal cur,x,y,rowh
        cur=Image.new('L',(PAGE,PAGE),0); pages.append(cur); x=y=0; rowh=0
    newpage()
    for k,ch in enumerate(chars):
        i=idx_of(k)
        while len(gl)<=i: gl.append([0,0,0,0,0,0,0,0])
        g,xoff,yoff,adv=render_glyph(ch,c)
        if g is None: gl[i]=[0,0,0,0,0,0,0,adv]; continue
        w,h=g.size; pw,ph=w+2,h+2   # 1px 투명 여백
        if x+pw>PAGE: x=0; y+=rowh; rowh=0
        if y+ph>PAGE: newpage()
        cur.paste(g,(x+1,y+1))
        pn=len(pages) # 1-based new page index (0 = 원본)
        gl[i]=[pn, x, y, pw, ph, xoff-1, yoff+1, adv]
        x+=pw; rowh=max(rowh,ph)
    names=[f['pages'][0]]+['%s_%d.TDX'%(name,i+1) for i in range(len(pages))]
    f['pages']=names
    tdxs={}
    tmpl=orig_page0 if name=='LARGEFNT' else None
    for i,p in enumerate(pages):
        tdxs[names[i+1]]=make_tdx(to4(p))
    return fnt.write(f), tdxs
TEMPLATE=None
def make_tdx(img4):
    """img4: L image with values 0..15, 256x256 -> 4bpp swizzled TDX (LARGEFNT_0 헤더 복제)"""
    h=bytearray(TEMPLATE[:0xa0])
    px=list(img4.getdata()); raw=bytearray(PAGE*PAGE//2)
    for i in range(0,len(px),2):
        a=px[i]; b=px[i+1]
        # 팔레트: idx 0..14 = 레벨(1..15)/15, idx 15 = 투명
        def pi(v): return 15 if v==0 else v-1
        raw[i//2]=pi(a)|(pi(b)<<4)
    raw=tdx.swizzle(bytes(raw),PAGE//2,PAGE)
    return bytes(h)+raw

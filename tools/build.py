"""전체 빌드: 원본 ISO -> 한글 ISO"""
import sys, os, json, glob, shutil, struct
sys.path.insert(0,os.path.dirname(__file__))
import hog, fnt, fontgen, kenc, strdat, eboot_patch, isobuild, gui, mrk, hashlib
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
W=os.path.join(ROOT,'work'); X=os.path.join(W,'iso')
ORIG=os.path.join(ROOT,'Syphon Filter - Dark Mirror (USA).iso')
OUT=os.path.join(ROOT,'Syphon Filter - Dark Mirror (Korean).iso')
G='PSP_GAME/USRDIR/GAMEDATA/'
def rd(p): return open(os.path.join(X,p),'rb').read()
def load_trans():
    T={}
    for p in sorted(glob.glob(os.path.join(ROOT,'trans','*.json'))):
        T[os.path.basename(p)[:-5]]=json.load(open(p,encoding='utf-8'))
    return T
def all_texts(T):
    for k,v in T.items():
        if isinstance(v,dict):
            for kk,vv in v.items():
                if isinstance(vv,str): yield vv
                elif isinstance(vv,(dict,list)):
                    for x in (vv.values() if isinstance(vv,dict) else vv):
                        if isinstance(x,str): yield x
def main(only=None):
    T=load_trans()
    chars=kenc.needed_chars(all_texts(T))
    E=kenc.Enc(chars)
    print('음절 수',len(chars))
    files={}
    # 1. EBOOT
    eb=eboot_patch.patch(os.path.join(X,'PSP_GAME/SYSDIR/BOOT.BIN'),os.path.join(W,'out','EBOOT.BIN'))
    eb=bytearray(eb)
    for o,t in T.get('boot',{}).items():
        o=int(o,16); e=eb.index(b'\0',o)
        while e+1<len(eb) and eb[e+1]==0 and (e+1)%4: e+=1
        b=E.enc(t); assert len(b)<=e-o,(hex(o),len(b),e-o)
        eb[o:e]=b+b'\0'*(e-o-len(b))
    eb=bytes(eb); files['PSP_GAME/SYSDIR/EBOOT.BIN']=eb
    # 자막
    import re
    for fn,lines in T.get('sub',{}).items():
        p='PSP_GAME/USRDIR/'+fn; t=rd(p); it=iter(lines)
        def rp(m):
            k=next(it); return m.group(1)+b'"'+E.enc(k)+b'"'+m.group(3)
        t2=re.sub(rb'(?m)^(\s*)"([^"\r\n]*)"?(\s*)$',rp,t)
        files[p]=t2
    # 2. 폰트
    fontgen.TEMPLATE=open(os.path.join(W,'fonts','LARGEFNT_0.TDX'),'rb').read()
    items,raw=hog.read(rd(G+'COMMON/FONTS.HOG'))
    d=dict(items); new={}
    for nm in ['CALLOUT','DEFAULT','LARGEFNT','TINYFNT']:
        fb,pages=fontgen.build_font(nm,d[nm+'.FNT'],d[nm+'_0.TDX'],chars,None)
        new[nm+'.FNT']=fb; new[nm+'_0.TDX']=d[nm+'_0.TDX']; new.update(pages)
    fitems=sorted(new.items())
    fh=hog.build(fitems)
    print('FONTS.HOG',len(fh))
    st=strdat.read(os.path.join(X,G+'COMMON/STRINGS.DAT'))
    tr=T.get('strings',{})
    st2=[(k,E.enc(tr[k]) if k in tr and tr[k] else v) for k,v in st]
    strdat.write(os.path.join(W,'out','STRINGS.DAT'),st2); sb=open(os.path.join(W,'out','STRINGS.DAT'),'rb').read()
    gtr={k.encode('latin-1'):E.enc(v) for k,v in T.get('gui',{}).items() if v}
    gstat={'files':0,'fields':0}
    gsrc=dict(st); gsb=dict(st2)
    entr={v.decode('latin-1'):tr[k] for k,v in st if tr.get(k)}
    lvtr={k:v for k,v in T.get('level',{}).items() if v}
    mshort=T.get('mrk_short',{}); mstat=[]
    # 텍스처 교체: trans/tex/<md5>.tdx
    tex_tr={}
    for f in glob.glob(os.path.join(ROOT,'trans','tex','*.tdx')):
        tex_tr[os.path.basename(f)[:-4]]=open(f,'rb').read()
    # PARAM.SFO 제목
    sfo=bytearray(rd('PSP_GAME/PARAM.SFO')); ttl=T.get('meta',{}).get('title')
    if ttl:
        tb=ttl.encode('utf-8')+b'\0'; assert len(tb)<=0x80
        ko,do=struct.unpack_from('<II',sfo,8); n=struct.unpack_from('<I',sfo,16)[0]
        for i in range(n):
            kof,fmt,ln,mx,dof=struct.unpack_from('<HHIII',sfo,20+16*i)
            if sfo[ko+kof:ko+kof+6]==b'TITLE\0':
                sfo[do+dof:do+dof+mx]=tb+bytes(mx-len(tb)); struct.pack_into('<I',sfo,20+16*i+4,len(tb))
        files['PSP_GAME/PARAM.SFO']=bytes(sfo)
    for nm in ('ICON0.PNG','PIC1.PNG'):
        f=os.path.join(ROOT,'trans',nm)
        if os.path.exists(f): files['PSP_GAME/'+nm]=open(f,'rb').read()
    def member(mp,n,b):
        u=n.upper()
        if u=='FONTS.HOG' or u=='FONTS_PSP.HOG': return fh
        if u=='STRINGS.DAT' and len(b)>0:
            it=strdat.parse(b)
            if len(it)==len(st): return sb
            out=[]
            for k,v in it:
                if v==gsrc.get(k) or (k not in gsrc and False): out.append((k,gsb[k])); continue
                t=lvtr.get(v.decode('latin-1')) or entr.get(v.decode('latin-1'))
                out.append((k,E.enc(t) if t else v))
            return strdat.dump(out)
        if b[:4]==b'SMRK' and b'<SCRIPT>' in b:
            ts=mrk.parse(b)
            cp=mrk.caps(b); nt=[]
            for t,c in zip(ts,cp):
                s=t.decode('latin-1'); e=E.enc(lvtr[s]) if s in lvtr else t
                if len(e)>c and s in mshort: e=E.enc(mshort[s])
                if len(e)>c: mstat.append(s)
                nt.append(e)
            return mrk.build_fixed(b,nt) if nt!=ts else None
        if u.endswith('.TDX') and tex_tr.get(hashlib.md5(b).hexdigest()):
            return tex_tr[hashlib.md5(b).hexdigest()]
        if u.endswith('.GUI') and b[:3]==b'GUI':
            m={t0:gtr[txt] for t0,txt,*_ in gui.extract(b) if txt in gtr}
            if m: gstat['files']+=1; gstat['fields']+=len(m); return gui.replace(b,m)
        return None
    # 루즈 파일 + 컨테이너
    files[G+'COMMON/FONTS.HOG']=fh; files[G+'COMMON/FONTS_PSP.HOG']=fh; files[G+'COMMON/FONTS.HGZ']=hog.hgz(fh)
    files[G+'COMMON/STRINGS.DAT']=sb
    for p in sorted(glob.glob(os.path.join(X,G,'**','*'),recursive=True)):
        if os.path.isdir(p) or not p.upper().endswith(('.HGZ','.HOG')): continue
        rel=os.path.relpath(p,X).replace(os.sep,'/')
        o=open(p,'rb').read()
        if o[:4]!=b'HGZ\0' and not hog.is_hog(o): continue
        n=hog.repack(o,member)
        if n is not o: files[rel]=n
    print('MRK 잘림',len(set(mstat)),list(set(mstat))[:5])
    print('GUI',gstat,'변경 컨테이너',len(files))
    # ISO
    if os.path.exists(OUT): os.remove(OUT)
    iso=isobuild.Iso(ORIG,OUT)
    for p,b in files.items():
        if only and not any(o in p for o in only): continue
        r=iso.replace(p,b)
    iso.close()
    print('완료',OUT)
if __name__=='__main__': main(sys.argv[1:] or None)

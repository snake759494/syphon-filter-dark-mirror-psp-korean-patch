"""BOOT.BIN(평문 PRX) -> 한글 2바이트 지원 EBOOT.BIN
인코딩: 리드 0xE0..0xFF, 트레일 0x80..0xCF  -> 글리프 idx = (lead<<7) + trail - 0x6FC0  (0xC0부터)
패치: cFont::GetWidth(0x2f2a4c) 재작성, cFont::Draw 디코드부(0x2f2d34..0x2f2dbc) 재작성"""
import struct, sys
from keystone import Ks, KS_ARCH_MIPS, KS_MODE_MIPS32, KS_MODE_LITTLE_ENDIAN
TOFF=0x80
ks=Ks(KS_ARCH_MIPS, KS_MODE_MIPS32+KS_MODE_LITTLE_ENDIAN)
REG={n:i for i,n in enumerate('zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp fp ra'.split())}
def _r(x): return REG[x.strip().lstrip('$')]
def asm(src, addr):
    """2패스: 라벨/절대주소 분기는 직접 인코딩, 나머지는 keystone"""
    lines=[l.split('#')[0].strip() for l in src.strip().splitlines()]
    lab={}; pc=addr; body=[]
    for l in lines:
        if not l: continue
        if l.endswith(':'): lab[l[:-1]]=pc; continue
        body.append((pc,l)); pc+=4
    out=b''
    for pc,l in body:
        op,_,args=l.partition(' '); a=[x.strip() for x in args.split(',')] if args.strip() else []
        def tgt(t):
            v=lab[t] if t in lab else int(t,0)
            off=(v-(pc+4))>>2; assert -0x8000<=off<0x8000; return off&0xffff
        if op in ('b','beq','bne','beqz','bnez','blez','bgtz'):
            if op=='b': w=(4<<26)|tgt(a[0])
            elif op=='beq': w=(4<<26)|(_r(a[0])<<21)|(_r(a[1])<<16)|tgt(a[2])
            elif op=='bne': w=(5<<26)|(_r(a[0])<<21)|(_r(a[1])<<16)|tgt(a[2])
            elif op=='beqz': w=(4<<26)|(_r(a[0])<<21)|tgt(a[1])
            elif op=='bnez': w=(5<<26)|(_r(a[0])<<21)|tgt(a[1])
            elif op=='blez': w=(6<<26)|(_r(a[0])<<21)|tgt(a[1])
            elif op=='bgtz': w=(7<<26)|(_r(a[0])<<21)|tgt(a[1])
            out+=struct.pack('<I',w)
        else:
            enc,_=ks.asm(".set noreorder; "+l, pc); assert len(enc)==4,(l,len(enc)); out+=bytes(enc)
    return out

WIDTH_ADDR=0x2f2a4c; WIDTH_END=0x2f2af8
WIDTH=r"""
    lw    $a3, 0x9c($a0)
    lw    $t0, 0xb0($a0)
    mtc1  $zero, $f0
loop:
    lbu   $t1, 0($a1)
    beqz  $t1, ret
    addiu $a1, $a1, 1
    blez  $a2, ret
    sltiu $t3, $t1, 0x21
    beqz  $t3, gl
    addiu $t2, $t1, -0x20
    bnez  $t2, loop
    nop
    mtc1  $a3, $f2
    cvt.s.w $f2, $f2
    addiu $a2, $a2, -1
    b     loop
    add.s $f0, $f0, $f2
gl:
    sltiu $t3, $t1, 0xe0
    bnez  $t3, g2
    lbu   $t3, 0($a1)
    beqz  $t3, g2
    sll   $t4, $t1, 7
    addu  $t2, $t4, $t3
    addiu $t2, $t2, -0x6fc0
    addiu $a1, $a1, 1
    addiu $a2, $a2, -1
g2:
    sll   $t2, $t2, 3
    addu  $t2, $t0, $t2
    lb    $t2, 7($t2)
    mtc1  $t2, $f2
    cvt.s.w $f2, $f2
    addiu $a2, $a2, -1
    b     loop
    add.s $f0, $f0, $f2
ret:
    jr    $ra
    nop
"""
DRAW_ADDR=0x2f2d34; DRAW_END=0x2f2dc0
DRAW=r"""
    ori   $a0, $zero, 0x20
    beq   $a1, $a0, space
    addiu $a0, $a1, -0x20
    sltiu $t0, $a1, 0xe0
    bnez  $t0, 0x2f2dc0
    lbu   $t0, 0($s3)
    beqz  $t0, 0x2f2dc0
    sll   $a3, $a1, 7
    addu  $a0, $a3, $t0
    addiu $s3, $s3, 1
    b     0x2f2dc0
    addiu $a0, $a0, -0x6fc0
space:
    lw    $a0, 0x9c($s2)
    mtc1  $a0, $f16
    cvt.s.w $f16, $f16
    b     next
    add.s $f28, $f28, $f16
ctrl:
    addiu $a0, $a1, -0x10
    sltiu $a0, $a0, 8
    beqz  $a0, next
    sll   $a0, $a1, 4
    addu  $a0, $s2, $a0
    lwc1  $f6, -0x100($a0)
    lwc1  $f5, -0xfc($a0)
    lwc1  $f4, -0xf8($a0)
    lw    $a1, 0xb0($sp)
    lwc1  $f3, 0xc($a1)
next:
    move  $a0, $s3
    b     0x2f3218
    lbu   $a1, 0($a0)
"""
CTRL_BRANCH=0x2f2d2c   # bnez a3, ctrl

def reloc_offsets(d):
    e_shoff=struct.unpack_from('<I',d,0x20)[0]; shnum,shstr=struct.unpack_from('<HH',d,0x30)
    out=[]
    for i in range(shnum):
        s=struct.unpack_from('<10I',d,e_shoff+i*40)
        if s[1]==0x700000a0:
            for j in range(s[5]//8):
                off,info=struct.unpack_from('<II',d,s[4]+j*8)
                out.append((off,info))
    return out

def patch(src,dst):
    d=bytearray(open(src,'rb').read())
    w=asm(WIDTH,WIDTH_ADDR); assert len(w)<=WIDTH_END-WIDTH_ADDR,len(w)
    w+=b'\0'*(WIDTH_END-WIDTH_ADDR-len(w))
    dr=asm(DRAW,DRAW_ADDR); assert len(dr)<=DRAW_END-DRAW_ADDR,(len(dr),DRAW_END-DRAW_ADDR)
    dr+=b'\0'*(DRAW_END-DRAW_ADDR-len(dr))
    ctrl=DRAW_ADDR+DRAW.split('ctrl:')[0].count('\n    ')*4
    # ctrl label address: assemble again to locate
    lines=[l for l in DRAW.strip().split('\n')]
    n=0
    for l in lines:
        if l.strip()=='ctrl:': break
        if not l.strip().endswith(':'): n+=1
    ctrl=DRAW_ADDR+4*n
    br=asm('bnez $a3, 0x%x'%ctrl, CTRL_BRANCH)
    # 재배치 엔트리 검사
    for off,info in reloc_offsets(d):
        for a,b in ((WIDTH_ADDR,WIDTH_END),(DRAW_ADDR,DRAW_END),(CTRL_BRANCH,CTRL_BRANCH+4)):
            assert not (a<=off<b), ('reloc inside patch', hex(off))
    assert d[TOFF+CTRL_BRANCH:TOFF+CTRL_BRANCH+4]==asm('bnez $a3, 0x2f2d48',CTRL_BRANCH)
    d[TOFF+WIDTH_ADDR:TOFF+WIDTH_END]=w
    d[TOFF+DRAW_ADDR:TOFF+DRAW_END]=dr
    d[TOFF+CTRL_BRANCH:TOFF+CTRL_BRANCH+4]=br
    # 동영상 자막(SUB) 줄의 UTF-8 변환(0x2facc0)이 한글 2바이트 코드를 깨뜨림 -> 변환 생략
    U8=0x2face0
    assert d[TOFF+U8:TOFF+U8+4]==asm('beqz $a1, 0x2fad60',U8)
    assert not any(a<=off<a+4 for off,_ in reloc_offsets(d) for a in (U8,))
    d[TOFF+U8:TOFF+U8+4]=asm('b 0x2fad60',U8)
    open(dst,'wb').write(d)
    print('width %d/%d, draw %d/%d, ctrl=0x%x'%(len(asm(WIDTH,WIDTH_ADDR)),WIDTH_END-WIDTH_ADDR,len(asm(DRAW,DRAW_ADDR)),DRAW_END-DRAW_ADDR,ctrl))
    return bytes(d)
if __name__=='__main__':
    patch(sys.argv[1],sys.argv[2])

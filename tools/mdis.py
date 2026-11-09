import capstone, struct, sys
D=open('work/iso/PSP_GAME/SYSDIR/BOOT.BIN','rb').read()
TOFF=0x80; TSIZE=0x5ab05c
md=capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS32+capstone.CS_MODE_LITTLE_ENDIAN)
def dis(addr,n):
    out=[]
    for i in md.disasm(D[TOFF+addr:TOFF+addr+4*n],addr):
        out.append('%06x: %s %s'%(i.address,i.mnemonic,i.op_str))
    return out
def all_ins():
    a=0
    while a<TSIZE:
        w=D[TOFF+a:TOFF+a+4]
        r=list(md.disasm(w,a))
        yield a,(r[0].mnemonic+' '+r[0].op_str if r else '?')
        a+=4
if __name__=='__main__':
    a=int(sys.argv[1],16); n=int(sys.argv[2]) if len(sys.argv)>2 else 40
    print('\n'.join(dis(a,n)))

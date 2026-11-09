"""find code computing an absolute vaddr via lui+addiu/ori/lw etc (window 12)"""
import re, sys
lines=open('work/text.asm').read().split('\n')
pat_lui=re.compile(r'^(\w+): lui \$(\w+), (0x[0-9a-f]+|\d+)$')
pat_imm=re.compile(r'^(\w+): (\w+) \$(\w+), (?:\$(\w+), (-?0x[0-9a-f]+|-?\d+)|(-?0x[0-9a-f]+|-?\d+)\(\$(\w+)\))$')
def build():
    refs={}
    last={}
    for i,l in enumerate(lines):
        m=pat_lui.match(l)
        if m:
            last[m.group(2)]=(i,int(m.group(3),0)); continue
        m=pat_imm.match(l)
        if m:
            a=int(m.group(1),16); op=m.group(2)
            if m.group(4) is not None: base=m.group(4); imm=int(m.group(5),0)
            else: base=m.group(7); imm=int(m.group(6),0)
            if base in last and i-last[base][0]<16:
                hi=last[base][1]
                v=((hi<<16)+imm)&0xffffffff if op!='ori' else (hi<<16)|(imm&0xffff)
                refs.setdefault(v,[]).append(a)
    return refs
if __name__=='__main__':
    import pickle
    r=build(); pickle.dump(r,open('work/xref.pkl','wb'))
    for a in sys.argv[1:]:
        v=int(a,16); print(hex(v),[hex(x) for x in r.get(v,[])])

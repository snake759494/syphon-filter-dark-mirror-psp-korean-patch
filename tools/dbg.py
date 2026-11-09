import sys,json,base64; sys.path.insert(0,'tools'); from ppsspp_rpc import Debugger
B=0x8804000
def regs(d):
    r=d.call('cpu.getAllRegs')['categories'][0]
    return dict(zip(r['registerNames'],r['uintValues']))
def mem(d,a,n): return base64.b64decode(d.call('memory.read',address=a,size=n)['base64'])
if __name__=='__main__':
    d=Debugger(); R=regs(d)
    print('pc',hex(R['pc']-B),' '.join('%s=%x'%(k,R[k]) for k in ['a0','a1','a2','a3','t0','t1','t2','t3','s1','s2','s3','ra']))
    for e in sys.argv[1:]:
        a=eval(e,{'R':R},R); print(e,hex(a),mem(d,a,32).hex(' '))
    d.close()

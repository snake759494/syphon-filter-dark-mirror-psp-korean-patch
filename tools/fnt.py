"""FNT: u8 ver(4), u8 0, u32 npages, npages*(u8 len, name), u32 lineh, u32 base, u32 ?, u32 spacew, u32 ?, u32 count, count*8 (page,x,y,w,h,xoff s8,yoff u8,adv s8), u32 0"""
import struct
def read(d):
    o=2; np_=struct.unpack_from('<I',d,o)[0]; o+=4; pages=[]
    for i in range(np_):
        l=d[o]; pages.append(d[o+1:o+1+l].decode()); o+=1+l
    hdr=list(struct.unpack_from('<5I',d,o)); o+=20
    n=struct.unpack_from('<I',d,o)[0]; o+=4
    gl=[list(struct.unpack_from('<BBBBBbBb',d,o+8*i)) for i in range(n)]; o+=8*n
    tail=d[o:]
    return dict(ver=d[:2],pages=pages,hdr=hdr,glyphs=gl,tail=tail)
def write(f):
    b=bytearray(f['ver'])+struct.pack('<I',len(f['pages']))
    for p in f['pages']: b+=bytes([len(p)])+p.encode()
    b+=struct.pack('<5I',*f['hdr'])+struct.pack('<I',len(f['glyphs']))
    for g in f['glyphs']: b+=struct.pack('<BBBBBbBb',*g)
    b+=f['tail']; return bytes(b)

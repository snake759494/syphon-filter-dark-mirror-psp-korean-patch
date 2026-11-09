"""한글 텍스트 -> 게임 바이트 인코딩 (charset.json: 음절 리스트)"""
import json, os, sys
sys.path.insert(0,os.path.dirname(__file__))
import fontgen
# 단일바이트로 그대로 쓰는 문자 (ASCII + 게임 고유)
SINGLE={'\u2122':0xD1,'\xd1':0xD1,'\x87':0x87,'\x8a':0x8a}
class Enc:
    def __init__(self, chars):
        self.chars=list(chars); self.map={c:fontgen.code_of(k) for k,c in enumerate(self.chars)}
    def enc(self, s):
        out=bytearray()
        for ch in s:
            o=ord(ch)
            if o<0x80: out.append(o)
            elif ch in SINGLE: out.append(SINGLE[ch])
            elif ch in self.map: out+=self.map[ch]
            else: raise KeyError('no glyph for %r in %r'%(ch,s))
        return bytes(out)
def needed_chars(texts):
    s=set()
    for t in texts:
        for ch in t:
            if ord(ch)>=0x80 and ch not in SINGLE: s.add(ch)
    return sorted(s)

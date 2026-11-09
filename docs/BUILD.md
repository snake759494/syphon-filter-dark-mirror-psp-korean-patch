# 빌드 방법

번역 대본·원문은 저장소에 없으므로, 아래는 자신이 가진 원본과 번역 파일로 다시 빌드하는 절차입니다.

## 준비물
- 원본 ISO `Syphon Filter - Dark Mirror (USA).iso` (MD5 `b5b58939cd1d4a764b2ae41f20d6e243`)
- Python 3.12+ : `pip install pillow numpy websocket-client`
- 글꼴: `NanumSquareNeo-cBd.ttf` (작업 폴더), `Galmuri11.ttf`·`Galmuri9.ttf` (`work/fonts/`)

## 폴더 구성
```
<작업 폴더>/
  Syphon Filter - Dark Mirror (USA).iso
  *.ttf
  tools/        (이 저장소의 tools)
  trans/        strings.json, gui.json, level.json, mrk_short.json, sub.json, boot.json, meta.json, ICON0.PNG, tex/  (번역 — 저장소 미포함)
  work/         iso/, fonts/, out/
```

## 순서
1. ISO 풀기: `python tools/extract_iso.py "Syphon Filter - Dark Mirror (USA).iso" work/iso`
2. 번역 파일 작성 (`docs/TRANSLATION_GUIDE.md`)
   - `strings.json`: 공통 STRINGS.DAT `{키: 번역}`
   - `level.json`: 레벨 STRINGS·MRK `{영어 원문: 번역}`, `mrk_short.json`: 길이를 넘는 대사의 줄인 번역
   - `gui.json`: `{영어: 번역}`, `sub.json`: `{파일: [줄 번역, ...]}`, `boot.json`: `{16진 오프셋: 번역}`, `meta.json`: `{"title": "..."}`
3. 그림 글자: `python tools/texko.py` → `trans/tex/`
4. 빌드: `mkdir -p work/out && python tools/build.py` → `Syphon Filter - Dark Mirror (Korean).iso`
5. 검사: `python tools/audit.py`
6. 차분: `xdelta3 -0 -f -e -s 원본.iso 한글.iso 패치.xdelta`

PPSSPP 원격 디버거로 자동 확인할 때는 `python tools/emu.py` 를 씁니다.

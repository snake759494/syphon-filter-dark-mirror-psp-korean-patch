# 기술 문서

## 실행 파일
- `PSP_GAME/SYSDIR/BOOT.BIN` 은 암호화되지 않은 PRX입니다. 이를 수정해 `EBOOT.BIN` 자리에 넣습니다(`tools/eboot_patch.py`).
- 글꼴 출력 루틴(cFont의 폭 계산·그리기)을 고쳐 리드 바이트 0xE0–0xFF + 트레일 바이트 0x80–0xCF 2바이트 코드를 한 글자로 처리합니다. 단일 바이트 특수 문자(™ 0xD1 등)는 그대로 둡니다.
- 실행 파일 안의 문자열 일부는 원래 자리에서 길이 안에 덮어씁니다(`trans/boot.json`, 오프셋 → 번역).

## 인코딩
- `tools/kenc.py`: 번역에 쓰인 음절만 모아 정렬하고 순서대로 2바이트 코드를 배정합니다. 같은 목록으로 글꼴 페이지를 만듭니다.

## 컨테이너
- **HOG**: `magic(4) n off_tbl(0x14) name_tbl data_base offsets[n+1] names...`. magic은 `iiii` 외에 다른 값도 있어서(LOADSCRN.HOG, MAP.HOG) 구조로 판별합니다(`hog.is_hog`).
- **HGZ**: `HGZ\0, 총크기, 원본크기` 다음 0x8000 블록 단위 zlib 청크. 청크 헤더는 `csize^0xBEEF8200`, `usize^0x3F80FEB1`.
- `hog.repack` 이 HGZ/HOG를 재귀로 풀어 바뀐 파일만 다시 묶습니다.

## 텍스트
- **STRINGS.DAT**(`tools/strdat.py`): 키→문자열 표. 공통 `COMMON/STRINGS.DAT` 는 키 기준으로 번역합니다. 레벨마다 `FREEDGUI*.HGZ` 안에 따로 있는 STRINGS.DAT는 키가 겹치므로 영어 원문 기준으로 번역합니다.
- **GUI**(`tools/gui.py`): 화면 레이아웃 파일 안의 텍스트 필드를 바꿉니다.
- **SMRK**(`tools/mrk.py`): 음성 대사 자막 스크립트. 게임이 대사를 **원래 바이트 오프셋**으로 찾기 때문에 레코드 위치를 옮기면 그 뒤 자막이 사라집니다. `build_fixed` 로 각 레코드를 원래 자리, 원래 크기 안에 덮어쓰고, 넘치는 대사는 `trans/mrk_short.json` 의 줄인 번역을 씁니다.
- **SUB**: 컷신 동영상 자막 텍스트. 따옴표 안 문자열을 순서대로 바꿉니다. 게임은 읽은 줄을 UTF-8로 디코딩(0x2facc0)하는데, 한글 리드 바이트 0xE0–0xEF가 UTF-8 3바이트 시퀀스로 해석돼 글자가 깨지므로 0x2face0의 분기를 무조건 분기로 바꿔 변환을 건너뜁니다. 같은 변환 본체(0x2fa8c0)를 직접 부르는 경로도 0x2fa8f8 분기를 무조건 분기로 바꿔 막습니다(`tools/eboot_patch.py`). 플래그(0x6134f8) 자체는 키 매핑 함수(0x2fac30)가 쓰므로 그대로 둡니다.

## 글꼴
- `tools/fnt.py`, `tools/fontgen.py`: 원본 FNT 메트릭을 유지하고 한글 글리프 페이지 TDX를 추가합니다.

## 텍스처
- **TDX**(`tools/tdx.py`): 팔레트 + 스위즐 텍스처. `encode_like` 로 원본 팔레트·스위즐을 그대로 써서 다시 인코딩합니다.
- `tools/texko.py` 가 그림 글자를 다시 그려 `trans/tex/<원본 md5>.tdx` 로 저장하고, 빌드할 때 md5가 같은 텍스처를 교체합니다.

## 기타
- PARAM.SFO의 TITLE을 UTF-8 한글 제목으로 바꾸고 ICON0.PNG를 교체합니다.
- `tools/isobuild.py` 가 원본 ISO 구조를 유지한 채 파일을 바꿔 넣습니다(커진 파일은 끝에 재배치).
- `tools/audit.py` 로 완성 ISO에서 남은 영어를 전수 검사합니다.

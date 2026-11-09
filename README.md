# 사이폰 필터: 다크 미러 (PSP) 비공식 한글패치

PSP 북미판 **Syphon Filter: Dark Mirror (사이폰 필터: 다크 미러, UCUS-98641)** 비공식 한국어 패치입니다. 이 저장소에는 제작 도구와 기술 문서만 있고, 패치 파일(xdelta)은 [Releases](../../releases)에서 받을 수 있습니다. 게임 원본·영어 원문·번역 대본은 포함하지 않습니다.

## 적용 방법
1. 아래 해시와 일치하는 **원본 `.iso`** 를 준비합니다. (CSO·CHD 등으로 변환한 이미지에는 적용할 수 없습니다.)
   - PowerShell: `Get-FileHash -Algorithm MD5 -LiteralPath '.\Syphon Filter - Dark Mirror (USA).iso'`
2. xdeltaUI 같은 도구로 원본 `.iso` 에 `SyphonFilter_DarkMirror_KO_v1.0.xdelta` 를 적용합니다. (Patch = xdelta, Source File = 원본 ISO, Output File = 새 파일명)
   - 명령줄: `xdelta3 -d -s "Syphon Filter - Dark Mirror (USA).iso" SyphonFilter_DarkMirror_KO_v1.0.xdelta "Syphon Filter - Dark Mirror (Korean).iso"`
3. 만들어진 ISO를 PPSSPP 또는 커스텀 펌웨어(PSP·PS Vita Adrenaline 등)에서 실행합니다.

| 항목 | 값 |
| --- | --- |
| 원본 ISO 크기 | 1,206,910,976 바이트 |
| 원본 ISO MD5 | `b5b58939cd1d4a764b2ae41f20d6e243` |
| 원본 ISO SHA-256 | `94f69aecb31c1af89d360be4ecf082949857aa0fcf6b429814a4c2627bd9735d` |
| xdelta SHA-256 | `715038e8b79ff074ca7fb9dc98d7564e07a23e375445d170cecf3c77484eb1af` |
| 결과 ISO 크기 | 1,278,019,584 바이트 |
| 결과 ISO SHA-256 | `1d11df9d6544afd96499d3ad259333b81c9928077b23a9f83c1c45db0ee95b67` |

## 주의
- 복호화한 실행 파일을 EBOOT로 넣었기 때문에 **PPSSPP·커스텀 펌웨어 전용**입니다. 정품 펌웨어에서는 부팅되지 않습니다.
- 원본에서 만든 **상태저장(세이브 스테이트)** 은 불러오지 마세요. 일반 세이브는 그대로 쓸 수 있습니다.
- 음성 자막은 기본값이 꺼져 있습니다. **옵션 → 오디오 → 자막** 을 켜면 무전·컷신 대사가 한국어 자막으로 나옵니다.
- xdelta는 압축하지 않은 형식(`-0`)입니다(약 96MB).

## 한글화 내용
- 메뉴·옵션·무기·장비·도움말 등 공통 문자열 1,987개와 실행 파일 문자열 직접 번역
- 레벨별 브리핑·목표·힌트·정보 문서와 음성 대사 자막(MRK) 전수 번역 — 3,768개 항목, 원문 길이를 넘는 대사 223개는 뜻을 살려 줄여 씀
- 훈련·튜토리얼 안내, 컷신 자막(SUB) 391줄
- 화면 레이아웃(GUI) 문자열 362종, 1,000여 곳
- 그림 글자 5장 — 카드, 코드, i-스캔, 더보기, 기밀
- 홈 메뉴 게임 이름 「사이폰 필터: 다크 미러」와 아이콘 한글화
- 게임 글꼴 4종(본문·말풍선·작은 글자·큰 글자)에 한글 글리프 추가, 실행 파일을 2바이트 한글 출력에 맞게 수정
- 글꼴: 본문 갈무리11, 아주 작은 글자 갈무리9, 큰 제목 나눔스퀘어네오

## 그대로 둔 것
- 음성, 실제 총기 모델명·코드명 같은 고유 표기, 개발용 자리표시 문자열, 법적 고지, 영문 로고 이미지

## 검증 범위
PPSSPP에서 타이틀, 메뉴, 옵션, 훈련 1, 스토리 에피소드 1 도입과 음성 자막을 확인했습니다. 모든 MRK·STRINGS·GUI·자막 파일을 전수 검사해 번역 대상 영어가 남지 않고 잘린 대사가 없는 것을 확인했습니다. 전체 플레이 검증은 하지 않았습니다. 문제를 발견하면 Issues에 알려 주세요.

## 문서
- [CHANGELOG.md](CHANGELOG.md) — 변경 기록
- [docs/TECHNICAL.md](docs/TECHNICAL.md) — 파일 형식과 한글화 방법
- [docs/BUILD.md](docs/BUILD.md) — 직접 빌드하는 방법
- [docs/TRANSLATION_GUIDE.md](docs/TRANSLATION_GUIDE.md) — 번역 지침
- [docs/FONT_CREDITS.md](docs/FONT_CREDITS.md) — 글꼴
- [RIGHTS.md](RIGHTS.md) — 권리 및 외부 자료

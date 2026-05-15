# Job Radar 🎯

> 신입 백엔드 개발자를 위한 **개인 맞춤형 채용공고 자동 모니터링 시스템**

매일 오전 9시, 사람인 + 워크넷에서 신입 백엔드 공고를 자동 수집하고, Claude AI가 본인 프로필과 매칭해 적합도 70점 이상만 Notion DB에 자동으로 정리해줍니다.

## 🎯 무엇이 다른가

이 시스템은 **수집·분석·정리까지만 자동화**하고, 실제 지원은 사람이 직접 결정합니다.

- ✅ 사람인 Open API + 워크넷 API (공식, 안정적)
- ✅ Claude API로 본인 프로필 기반 적합도 분석
- ✅ Notion DB 자동 저장 + 면접 전략 코멘트
- ❌ 자동 지원 안 함

## 🏗️ 아키텍처

```
GitHub Actions (매일 09:00 KST cron)
        ↓
src/collectors/ → 사람인·워크넷 API 호출
        ↓
src/dedup.py → URL 기준 중복 제거 (Notion DB 기존 항목과 비교)
        ↓
src/filter.py → 학력·경력 1차 필터
        ↓
src/analyzer.py → Claude API로 적합도 분석 (0~100점 + 코멘트)
        ↓
src/notion_writer.py → 70점 이상만 Notion DB에 저장
```

## 📂 파일 구조

```
job-radar/
├── .github/workflows/
│   └── daily-collect.yml      # GitHub Actions cron (매일 09:00 KST)
├── config/
│   └── profile.example.yaml    # 프로필 템플릿 (실제 profile.yaml은 Secrets로 관리)
├── src/
│   ├── collectors/
│   │   └── saramin.py          # 사람인 Open API 클라이언트
│   ├── dedup.py                # 중복 제거
│   ├── filter.py               # 학력·경력 자동 필터
│   ├── analyzer.py             # Claude API 적합도 분석
│   ├── notion_writer.py        # 노션 DB 저장
│   └── main.py                 # 전체 파이프라인
├── requirements.txt
├── SETUP.md                    # 셋업 가이드
└── README.md
```

## 🔐 환경변수 (GitHub Secrets)

```
PROFILE_YAML            # config/profile.yaml의 전체 내용 (개인정보 보호)
SARAMIN_ACCESS_KEY      # 사람인 Open API 인증키
WORKNET_API_KEY         # 공공데이터포털 워크넷 API 키 (선택)
ANTHROPIC_API_KEY       # Claude API 키
NOTION_API_KEY          # Notion Integration 토큰
NOTION_DATABASE_ID      # 결과 저장할 DB ID
```

## 💰 운영 비용

| 항목 | 비용 |
|---|---|
| GitHub Actions | $0 (public repo 무료) |
| 사람인 Open API | $0 |
| 워크넷 API | $0 |
| Claude API | ~$3-5/월 (Haiku 모델 기준) |
| Notion API | $0 |
| **합계** | **월 $3-5** |

## 🚀 시작하기

[SETUP.md](./SETUP.md) 파일의 셋업 가이드를 따라 진행하세요.

## 🔧 본인 환경에 맞게 사용하기

1. 이 레포를 fork 또는 clone
2. `config/profile.example.yaml`을 `config/profile.yaml`로 복사
3. 본인 프로필로 수정
4. GitHub Secrets에 `PROFILE_YAML`로 등록 (실제 파일은 .gitignore로 보호됨)

## 📊 기술 스택

- Python 3.14
- Claude API (Anthropic)
- Sarmin Open API, Worknet API
- Notion API
- GitHub Actions (스케줄링)

## 📝 라이선스

MIT License

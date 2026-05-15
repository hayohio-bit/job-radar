# 🚀 셋업 가이드

처음 한 번만 따라하면 됩니다. 약 30분 ~ 1시간 소요.

---

## 1단계: 본인 프로필 작성 (10분)

```bash
# 템플릿 복사
cp config/profile.example.yaml config/profile.yaml

# 본인 정보로 수정
vim config/profile.yaml  # 또는 원하는 에디터로
```

수정 항목:

- `basic`: 이름, 학력, 경력 연수, GitHub URL
- `tech_stack`: 주력/활용/입문/미보유 기술
- `domain_strengths`: 이전 경력의 도메인 강점
- `portfolio`: 본인의 프로젝트 목록
- `auto_filters`: 학력·경력 조건에 맞는 자동 필터

---

## 2단계: API 키 준비 (15~20분)

### 2-1. 사람인 Open API

1. <https://oapi.saramin.co.kr> 접속 → 회원가입
2. "My API" → "API 신청"
3. **승인 1~2일 소요** (영업일)
4. 승인 후 access-key 메모

### 2-2. 워크넷 API (선택)

1. <https://www.data.go.kr> 접속 → 회원가입
2. "한국고용정보원 워크넷 채용정보" 검색 → 활용신청
3. 즉시 승인, 인증키 메모

### 2-3. Anthropic Claude API

1. <https://console.anthropic.com> 접속 → 회원가입
2. Settings → Billing → 카드 등록 (최소 $5)
3. API Keys → Create Key → 메모 (`sk-ant-...`)

### 2-4. Notion Integration

1. <https://www.notion.so/profile/integrations>
2. "+ 신규 연결" → 이름 `Job Radar`, Type `Access token`
3. Internal Integration Secret 메모 (`ntn_...`)

---

## 3단계: Notion DB 생성 (10분)

Notion에서 다음 속성을 가진 데이터베이스 생성:

| 속성명 | 타입 |
|---|---|
| 회사명 | 제목 |
| 공고제목 | 텍스트 |
| 공고URL | URL |
| 적합도점수 | 숫자 |
| 분류 | 선택 (🔥 즉시지원, ⭐ 추천, 📝 검토, 💤 보류) |
| 출처 | 선택 (saramin, worknet) |
| 업종, 경력조건, 학력조건, 위치, 연봉 | 텍스트 |
| 마감일 | 날짜 |
| 도메인연결, 자소서힌트, 충족기술, 미충족기술, 리스크, 성장환경시그널 | 텍스트 |
| 지원여부 | 선택 (🔖 미지원, 📝 작성중, ✅ 지원완료, 📞 면접, 🎉 합격, ❌ 탈락, ⏭️ 패스) |

생성 후:

1. DB 우측 상단 `⋯` → `Connections` → `Job Radar` 연결
2. DB URL에서 ID 추출: `notion.so/workspace/DATABASE_ID?v=...`

---

## 4단계: GitHub 레포 + Secrets 등록 (10분)

### 4-1. 레포 생성

```bash
# 새 레포에 코드 푸시
cd job-radar
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/job-radar.git
git push -u origin main
```

### 4-2. Secrets 등록

레포 → Settings → Secrets and variables → Actions → New repository secret

| Name | Value |
|---|---|
| `PROFILE_YAML` | **config/profile.yaml 파일 전체 내용**을 복사해서 붙여넣기 |
| `SARAMIN_ACCESS_KEY` | 2-1에서 받은 키 |
| `WORKNET_API_KEY` | 2-2에서 받은 키 (없으면 빈 값) |
| `ANTHROPIC_API_KEY` | 2-3에서 받은 키 |
| `NOTION_API_KEY` | 2-4에서 받은 키 |
| `NOTION_DATABASE_ID` | 3단계에서 추출한 DB ID |

> 💡 **PROFILE_YAML 등록 방법**: 로컬의 `config/profile.yaml` 파일을 텍스트 에디터로 열어 **전체 내용을 복사** → GitHub Secret의 Value 칸에 그대로 붙여넣기

---

## 5단계: 첫 실행 테스트 (2분)

레포 → Actions 탭 → "Daily Job Collection" → "Run workflow" 클릭

성공하면 노션 DB에 첫 공고들이 채워집니다.

---

## 트러블슈팅

**Q. profile.yaml을 수정한 뒤 어떻게 반영하나요?**
→ 로컬 파일 수정 후 GitHub Secrets의 `PROFILE_YAML` 값도 같이 업데이트해야 합니다. 두 가지를 동기화하는 게 번거롭다면, 매번 GitHub Secrets에서 직접 수정하는 방법도 있어요.

**Q. 실수로 profile.yaml을 커밋했어요!**
→ `git rm --cached config/profile.yaml && git commit -m "Remove profile" && git push`. 이미 푸시했다면 GitHub 히스토리에서 완전 삭제 필요: `git filter-branch` 또는 BFG Repo-Cleaner 사용.

**Q. 사람인 API가 403/401 반환**
→ access-key 오타 확인. 승인 메일 못 받았으면 사람인에 문의.

**Q. Claude API 비용이 걱정됨**
→ profile.yaml의 `thresholds.notion_save_min_score`를 80으로 올리면 분석 후 저장 건수가 줄어 비용도 감소.

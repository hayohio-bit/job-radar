"""
Job Radar 메인 파이프라인

핵심 원칙: profile.yaml은 여기서만 읽고, 각 모듈에 파라미터로 전달한다.
어떤 모듈도 직접 profile.yaml을 읽거나 조건을 하드코딩하지 않는다.
"""
import sys
import logging
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collectors.saramin import SaraminCollector
from src.filter import apply_pre_filter
from src.analyzer import FitAnalyzer
from src.dedup import remove_duplicates
from src.notion_writer import NotionWriter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("job-radar")


def load_profile(path: str = "config/profile.yaml") -> dict:
    """profile.yaml을 파싱해서 반환. 이 함수만이 파일을 읽는 유일한 진입점."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"profile.yaml 없음: {path}\n"
            "GitHub Actions: PROFILE_YAML Secret이 설정되어 있는지 확인하세요.\n"
            "로컬: cp config/profile.example.yaml config/profile.yaml 후 수정하세요."
        )
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    log.info("=" * 60)
    log.info("Job Radar 파이프라인 시작")
    log.info("=" * 60)

    # ── profile.yaml 로드 (유일한 읽기 지점) ──────────
    log.info("[준비] profile.yaml 로드 중...")
    profile = load_profile()
    log.info(f"  대상자: {profile['basic'].get('name', '(이름 없음)')}")
    log.info(f"  검색 키워드: {profile['auto_filters'].get('preferred_job_keywords', [])}")
    log.info(f"  최대 경력: {profile['auto_filters'].get('max_required_experience_years', 2)}년")
    log.info(f"  저장 기준: {profile['thresholds'].get('notion_save_min_score', 70)}점 이상")

    # ── 1. 수집 ──────────────────────────────────────
    log.info("[1/5] 채용공고 수집 중...")
    saramin = SaraminCollector()

    # 검색 파라미터를 profile.yaml에서 읽어서 전달
    search_keywords = profile["auto_filters"].get("preferred_job_keywords", [])
    max_exp = profile["auto_filters"].get("max_required_experience_years", 2)

    saramin_jobs = saramin.search(
        keywords=search_keywords,
        experience_max=max_exp,
        count=110,
    )
    log.info(f"  사람인: {len(saramin_jobs)}건")

    all_jobs = saramin_jobs  # 향후 워크넷 등 추가 시 여기에 병합

    # ── 2. 중복 제거 ──────────────────────────────────
    log.info("[2/5] 중복 제거 중...")
    notion = NotionWriter()
    existing_urls = notion.get_existing_urls()
    fresh_jobs = remove_duplicates(all_jobs, existing_urls)
    log.info(f"  신규 공고: {len(fresh_jobs)}건 (기존 {len(existing_urls)}건 제외)")

    if not fresh_jobs:
        log.info("신규 공고 없음. 종료.")
        return

    # ── 3. 사전 필터 ──────────────────────────────────
    log.info("[3/5] 사전 필터링 중...")
    # profile.yaml의 auto_filters를 그대로 전달
    filtered = apply_pre_filter(fresh_jobs, profile["auto_filters"])
    log.info(f"  필터 통과: {len(filtered)}건")

    if not filtered:
        log.info("필터 통과 공고 없음. 종료.")
        return

    # ── 4. AI 적합도 분석 ────────────────────────────
    log.info(f"[4/5] Claude API 분석 중... ({len(filtered)}건)")
    # profile 전체를 analyzer에 전달 (기술스택, 도메인강점, 포트폴리오 등 활용)
    analyzer = FitAnalyzer(profile)
    min_score = profile["thresholds"].get("notion_save_min_score", 70)

    analyzed = []
    for i, job in enumerate(filtered, 1):
        log.info(f"  [{i}/{len(filtered)}] {job.get('company_name')} - {job.get('title', '')[:30]}")
        result = analyzer.analyze(job)
        if result:
            job["analysis"] = result
            analyzed.append(job)

    # ── 5. 노션 저장 (profile.yaml의 임계값 기준) ────
    log.info("[5/5] 노션 DB 저장 중...")
    saved = 0
    for job in analyzed:
        score = job["analysis"].get("score", 0)
        if score >= min_score:
            notion.save(job)
            saved += 1
            log.info(f"  ✓ [{score}점] {job['company_name']} - {job['title'][:40]}")
        else:
            log.info(f"  ✗ [{score}점] 기준 미달 스킵: {job['company_name']}")

    log.info("=" * 60)
    log.info(f"완료: 신규 {saved}건 저장 (기준: {min_score}점 이상)")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
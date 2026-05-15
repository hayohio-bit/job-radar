"""
중복 제거
- URL 기준으로 Notion DB 기존 항목과 비교해 새 공고만 통과
"""
from typing import List, Dict, Set


def remove_duplicates(jobs: List[Dict], existing_urls: Set[str]) -> List[Dict]:
    """이미 노션에 저장된 URL은 제외"""
    seen = set()
    result = []
    for job in jobs:
        url = job.get("url", "")
        if not url:
            continue
        # URL 정규화 (utm 등 쿼리 파라미터 제거)
        canonical = url.split("?")[0]
        if canonical in existing_urls or canonical in seen:
            continue
        seen.add(canonical)
        job["url"] = canonical  # 정규화된 URL로 교체
        result.append(job)
    return result

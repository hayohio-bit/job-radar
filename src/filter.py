"""
사전 필터링
- 모든 필터 조건은 profile.yaml의 auto_filters 섹션에서만 읽음
- 이 파일에 개인 조건 하드코딩 없음
"""
import re
from typing import List, Dict


def apply_pre_filter(jobs: List[Dict], filters: Dict) -> List[Dict]:
    """
    profile.yaml의 auto_filters를 받아 공고 필터링

    Args:
        jobs: 수집된 공고 리스트
        filters: profile.yaml['auto_filters'] 딕셔너리
    """
    exclude_job_kw = filters.get("exclude_job_keywords", [])
    prefer_job_kw = filters.get("preferred_job_keywords", [])
    exclude_req_kw = filters.get("exclude_keywords_in_requirement", [])
    max_exp = filters.get("max_required_experience_years", 2)

    result = []
    for job in jobs:
        title = job.get("title", "")
        keyword = job.get("keyword", "")
        exp = job.get("experience_level", "")
        edu = job.get("education_level", "")
        haystack = f"{title} {keyword} {exp} {edu}"

        # 1. 명시적 제외 직무 키워드
        if any(kw in haystack for kw in exclude_job_kw):
            continue

        # 2. 학력 필수 조건 제외 키워드
        if any(kw in haystack for kw in exclude_req_kw):
            continue

        # 3. 경력 조건 상한
        if "경력" in exp and not any(s in exp for s in ["무관", "신입"]):
            nums = re.findall(r"\d+", exp)
            if nums and int(nums[0]) > max_exp:
                continue

        # 4. 선호 직무 키워드 매칭 (하나라도 있어야 통과)
        if prefer_job_kw and not any(
            kw.lower() in haystack.lower() for kw in prefer_job_kw
        ):
            continue

        result.append(job)

    return result
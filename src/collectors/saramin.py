"""
사람인 Open API 클라이언트
- 검색 키워드, 경력 조건은 profile.yaml에서만 읽음
- 이 파일에 개인 조건 하드코딩 없음
"""
import os
import requests
from typing import List, Dict


class SaraminCollector:
    BASE_URL = "https://oapi.saramin.co.kr/job-search"

    def __init__(self, access_key: str = None):
        self.access_key = access_key or os.getenv("SARAMIN_ACCESS_KEY")
        if not self.access_key:
            raise ValueError("SARAMIN_ACCESS_KEY가 설정되지 않았습니다")

    def search(self, keywords: List[str], experience_max: int, count: int = 110) -> List[Dict]:
        """
        키워드 기반 채용공고 검색
        - keywords, experience_max는 모두 profile.yaml에서 전달받음
        - 이 함수 내부에서 어떤 조건도 직접 정의하지 않음
        """
        params = {
            "access-key": self.access_key,
            "keywords": " ".join(keywords),
            "exp_min": 0,
            "exp_max": experience_max,
            "count": min(count, 110),
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"[Saramin] API 호출 실패: {e}")
            return []

        jobs = data.get("jobs", {}).get("job", [])
        if not isinstance(jobs, list):
            jobs = [jobs] if jobs else []

        return [self._normalize(job) for job in jobs]

    def _normalize(self, raw: Dict) -> Dict:
        position = raw.get("position", {})
        company = raw.get("company", {}).get("detail", {})
        return {
            "source": "saramin",
            "url": raw.get("url", ""),
            "company_name": company.get("name", ""),
            "title": position.get("title", ""),
            "industry": position.get("industry", {}).get("name", ""),
            "location": position.get("location", {}).get("name", ""),
            "job_category": position.get("job-code", {}).get("name", ""),
            "experience_level": position.get("experience-level", {}).get("name", ""),
            "education_level": position.get("required-education-level", {}).get("name", ""),
            "salary": raw.get("salary", {}).get("name", ""),
            "keyword": raw.get("keyword", ""),
            "posting_date": raw.get("posting-date", ""),
            "expiration_date": raw.get("expiration-date", ""),
        }
"""
Notion DB 클라이언트
- 신규 공고 저장
- 기존 URL 조회 (중복 방지용)
"""
import os
from typing import Dict, Set, List
from notion_client import Client


class NotionWriter:
    def __init__(self):
        self.client = Client(auth=os.getenv("NOTION_API_KEY"))
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        if not self.database_id:
            raise ValueError("NOTION_DATABASE_ID 환경변수가 없습니다")

    def get_existing_urls(self) -> Set[str]:
        """DB에 이미 저장된 모든 공고 URL 조회 (중복 방지용)"""
        urls = set()
        cursor = None
        while True:
            kwargs = {"database_id": self.database_id, "page_size": 100}
            if cursor:
                kwargs["start_cursor"] = cursor
            try:
                response = self.client.databases.query(**kwargs)
            except Exception as e:
                print(f"[Notion] DB 조회 실패: {e}")
                return urls

            for page in response.get("results", []):
                props = page.get("properties", {})
                url_prop = props.get("공고URL", {}).get("url")
                if url_prop:
                    urls.add(url_prop.split("?")[0])

            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")
        return urls

    def save(self, job: Dict):
        """공고 1건을 Notion DB에 저장"""
        analysis = job.get("analysis", {})
        score = analysis.get("score", 0)
        recommend = analysis.get("recommend", False)

        # 적합도 라벨 (셀렉트 옵션)
        if score >= 90:
            tier = "🔥 즉시지원"
        elif score >= 80:
            tier = "⭐ 추천"
        elif score >= 70:
            tier = "📝 검토"
        else:
            tier = "💤 보류"

        properties = {
            "회사명": {"title": [{"text": {"content": job.get("company_name", "")[:200]}}]},
            "공고제목": {"rich_text": [{"text": {"content": job.get("title", "")[:200]}}]},
            "공고URL": {"url": job.get("url", "")},
            "적합도점수": {"number": score},
            "분류": {"select": {"name": tier}},
            "출처": {"select": {"name": job.get("source", "saramin")}},
            "업종": {"rich_text": [{"text": {"content": job.get("industry", "")[:200]}}]},
            "경력조건": {"rich_text": [{"text": {"content": job.get("experience_level", "")[:100]}}]},
            "학력조건": {"rich_text": [{"text": {"content": job.get("education_level", "")[:100]}}]},
            "위치": {"rich_text": [{"text": {"content": job.get("location", "")[:200]}}]},
            "마감일": (
                {"date": {"start": job.get("expiration_date")}}
                if job.get("expiration_date") else {"date": None}
            ),
            "도메인연결": {"rich_text": [{"text": {"content": analysis.get("domain_connection", "")[:500]}}]},
            "자소서힌트": {"rich_text": [{"text": {"content": analysis.get("cover_letter_hint", "")[:500]}}]},
            "충족기술": {"rich_text": [{"text": {"content": ", ".join(analysis.get("matched_tech", []))[:500]}}]},
            "미충족기술": {"rich_text": [{"text": {"content": ", ".join(analysis.get("missing_tech", []))[:500]}}]},
            "리스크": {"rich_text": [{"text": {"content": ", ".join(analysis.get("risk_factors", []))[:500]}}]},
            "지원여부": {"select": {"name": "🔖 미지원"}},
        }

        try:
            self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
            )
        except Exception as e:
            print(f"[Notion] 저장 실패: {e}")

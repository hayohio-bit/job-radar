"""
Claude API 적합도 분석기
- 분석에 필요한 모든 개인 정보는 profile.yaml에서 읽음
- 이 파일에 개인 조건 하드코딩 없음
"""
import os
import json
from anthropic import Anthropic
from typing import Dict, Optional


class FitAnalyzer:
    def __init__(self, profile: Dict):
        """
        Args:
            profile: profile.yaml 전체를 파싱한 딕셔너리 (main.py에서 전달)
        """
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.profile = profile
        self.model = "claude-haiku-4-5-20251001"  # 비용 최적화
        self.min_score = profile.get("thresholds", {}).get("notion_save_min_score", 70)

    def analyze(self, job: Dict) -> Optional[Dict]:
        prompt = self._build_prompt(job)
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}],
            )
            return self._parse(response.content[0].text)
        except Exception as e:
            print(f"[Analyzer] 분석 실패 ({job.get('title', '')}): {e}")
            return None

    def _build_prompt(self, job: Dict) -> str:
        # profile.yaml에서 필요한 부분만 추출해서 프롬프트 구성
        profile_for_prompt = {
            "기본정보": self.profile.get("basic", {}),
            "보유기술": self.profile.get("tech_stack", {}),
            "도메인강점": self.profile.get("domain_strengths", []),
            "포트폴리오": self.profile.get("portfolio", []),
            "점수가중치": self.profile.get("scoring_weights", {}),
        }

        return f"""당신은 한국 IT 채용 시장 전문 컨설턴트입니다.
아래 지원자 프로필과 채용공고를 비교 분석해주세요.

## 지원자 프로필
{json.dumps(profile_for_prompt, ensure_ascii=False, indent=2)}

## 분석 대상 채용공고
- 회사: {job.get('company_name', '')}
- 직무: {job.get('title', '')}
- 업종: {job.get('industry', '')}
- 경력 조건: {job.get('experience_level', '')}
- 학력 조건: {job.get('education_level', '')}
- 위치: {job.get('location', '')}
- 키워드: {job.get('keyword', '')}
- 연봉: {job.get('salary', '')}

## 요청
아래 형식의 JSON으로만 응답하세요. 마크다운 없이 순수 JSON만.

{{
  "score": 0~100 정수,
  "recommend": true/false,
  "matched_tech": ["보유 기술 중 공고 요구사항과 일치하는 것"],
  "missing_tech": ["공고 요구사항 중 보유하지 못한 기술"],
  "domain_connection": "지원자 경력 도메인과 이 회사 도메인의 연결 포인트 1~2문장 (없으면 빈 문자열)",
  "cover_letter_hint": "이 공고 자소서에서 강조할 경험 1~2문장",
  "risk_factors": ["서류 탈락 가능성 있는 요소 (학력, 경력 부족 등)"],
  "growth_signal": "코드리뷰, DDD, TDD, 시니어 멘토링 등 언급 여부"
}}

점수 기준:
90+ → 즉시 지원 강력 추천
80~89 → 지원 추천
70~79 → 검토 후 지원
70 미만 → 비추천"""

    def _parse(self, text: str) -> Dict:
        text = text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            return {
                "score": 0, "recommend": False,
                "matched_tech": [], "missing_tech": [],
                "domain_connection": "", "cover_letter_hint": "AI 분석 실패",
                "risk_factors": ["분석 오류"], "growth_signal": "",
            }
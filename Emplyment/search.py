from __future__ import annotations

from dataclasses import dataclass

import requests

from .config import EmploymentConfig
from .models import EmploymentRequest, EmploymentSearchResult


@dataclass(slots=True)
class SearchPlan:
    queries: list[str]
    tool_name: str


class EmploymentSearchAgency:
    """Lightweight search layer inspired by BettaFish QueryEngine tools."""

    TAVILY_URL = "https://api.tavily.com/search"

    def __init__(self, config: EmploymentConfig):
        self.config = config

    def build_search_plan(self, request: EmploymentRequest, mode: str) -> SearchPlan:
        base = request.query.strip()
        queries = [base]
        lower = base.lower()

        if mode == "market":
            queries.extend(
                [
                    f"{base} 招聘 趋势",
                    f"{base} 技能 要求",
                    f"{base} 薪资 城市 公司",
                ]
            )
        else:
            queries.extend(
                [
                    f"{base} 求职 建议",
                    f"{base} 技能 要求 简历 面试",
                    f"{base} 岗位 城市 公司 机会",
                ]
            )

        skills = request.profile.get("skills")
        if isinstance(skills, list) and skills:
            joined = " ".join(str(item) for item in skills[:4])
            queries.append(f"{base} {joined} 岗位 匹配")

        if "校招" in lower or "应届" in base:
            queries.append(f"{base} 校招 应届 岗位 要求")

        deduped = []
        for item in queries:
            if item not in deduped:
                deduped.append(item)
        return SearchPlan(queries=deduped[:4], tool_name="tavily_search")

    def search(self, request: EmploymentRequest, mode: str) -> list[EmploymentSearchResult]:
        plan = self.build_search_plan(request, mode)
        if self.config.search_enabled and self.config.search_provider == "tavily":
            try:
                results = self._search_with_tavily(plan)
                if results:
                    return results
            except Exception:
                pass
        return self._fallback_results(plan.queries, request, mode)

    def _search_with_tavily(self, plan: SearchPlan) -> list[EmploymentSearchResult]:
        merged: list[EmploymentSearchResult] = []
        seen: set[str] = set()

        for query in plan.queries:
            payload = {
                "api_key": self.config.search_api_key,
                "query": query,
                "topic": "general",
                "search_depth": "basic",
                "max_results": self.config.max_search_results,
                "include_answer": False,
            }
            response = requests.post(
                self.TAVILY_URL,
                json=payload,
                timeout=self.config.search_timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
            for item in data.get("results", []):
                url = item.get("url") or ""
                if not url or url in seen:
                    continue
                seen.add(url)
                merged.append(
                    EmploymentSearchResult(
                        title=item.get("title") or query,
                        url=url,
                        snippet=item.get("content") or "",
                        query=query,
                        source="tavily",
                        published_date=item.get("published_date"),
                    )
                )
        return merged[: self.config.max_search_results]

    def _fallback_results(
        self,
        queries: list[str],
        request: EmploymentRequest,
        mode: str,
    ) -> list[EmploymentSearchResult]:
        seeds: list[EmploymentSearchResult] = []
        question = request.query
        synthetic_snippets = self._build_synthetic_snippets(question, mode, request.profile)
        for idx, snippet in enumerate(synthetic_snippets, start=1):
            query = queries[min(idx - 1, len(queries) - 1)]
            seeds.append(
                EmploymentSearchResult(
                    title=f"本地推断证据 {idx}",
                    url=f"local://employment-evidence/{idx}",
                    snippet=snippet,
                    query=query,
                    source="local_fallback",
                    published_date=None,
                )
            )
        return seeds

    def _build_synthetic_snippets(self, question: str, mode: str, profile: dict[str, object]) -> list[str]:
        snippets = [
            "就业分析至少应同时观察岗位需求、技能门槛、城市机会和企业稳定性，不能只看社交平台热度。",
            "真实岗位判断更适合从持续招聘、JD 高频技能、业务场景和对经验的要求四个维度切入。",
            "如果用户问题涉及具体城市，应重点比较城市中的行业密度、公司类型分布和竞争强度。",
        ]
        if "算法" in question or "AI" in question or "ai" in question.lower():
            snippets.append("AI/算法方向常见要求包括 Python、机器学习基础、模型调参、工程落地和业务场景理解。")
        if "数据分析" in question:
            snippets.append("数据分析岗位通常看重 SQL、Python、统计学基础、指标体系、业务分析和可视化表达能力。")
        if "产品" in question:
            snippets.append("产品岗位往往强调行业理解、需求拆解、跨团队协作、数据意识和推动项目落地的能力。")
        if mode == "guidance":
            snippets.append("求职指导不只是判断行情，更要判断候选人的现有能力能否被岗位快速验证。")
        if profile:
            snippets.append(f"当前已提供的用户画像字段包括：{', '.join(sorted(profile.keys()))}，这些信息可以帮助缩小建议范围。")
        return snippets[: self.config.max_search_results]

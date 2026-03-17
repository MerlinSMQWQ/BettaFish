from __future__ import annotations

from .agents import AdvisorAgent, AnalystAgent, ResearcherAgent
from .config import get_config
from .llm_client import EmploymentLLMClient
from .models import AgentNote, EmploymentReport, EmploymentRequest
from .report_writer import save_markdown
from .search import EmploymentSearchAgency


GUIDANCE_HINTS = ("我", "适合", "怎么找", "怎么准备", "简历", "转行", "面试", "求职")
MARKET_HINTS = ("行情", "趋势", "前景", "需求", "薪资", "岗位", "城市", "行业")


class EmploymentAdvisor:
    def __init__(self) -> None:
        self.config = get_config()
        self.llm_client = EmploymentLLMClient(self.config)
        self.search_agency = EmploymentSearchAgency(self.config)
        self.researcher = ResearcherAgent(self.llm_client)
        self.analyst = AnalystAgent(self.llm_client)
        self.advisor = AdvisorAgent(self.llm_client)

    def analyze(self, request: EmploymentRequest) -> EmploymentReport:
        mode = self._resolve_mode(request)
        search_results = self.search_agency.search(request, mode)
        researcher_note, researcher_used_llm = self.researcher.run(request, mode, search_results)
        analyst_note, analyst_used_llm = self.analyst.run(request, mode, researcher_note, search_results)
        markdown, advisor_used_llm = self.advisor.run(request, mode, researcher_note, analyst_note, search_results)

        title = self._build_title(request, mode)
        output_path = save_markdown(self.config.report_dir, request.query, markdown) if request.save else None
        agent_notes = [
            AgentNote(role="researcher", content=researcher_note),
            AgentNote(role="analyst", content=analyst_note),
        ]
        return EmploymentReport(
            title=title,
            mode=mode,
            markdown=markdown,
            used_llm=researcher_used_llm or analyst_used_llm or advisor_used_llm,
            used_search=bool(search_results),
            search_results=search_results,
            agent_notes=agent_notes,
            output_path=output_path,
        )

    def _resolve_mode(self, request: EmploymentRequest) -> str:
        if request.mode in {"market", "guidance"}:
            return request.mode
        query = request.query
        if any(token in query for token in GUIDANCE_HINTS):
            return "guidance"
        if any(token in query for token in MARKET_HINTS):
            return "market"
        return "market"

    def _build_title(self, request: EmploymentRequest, mode: str) -> str:
        suffix = "就业指导报告" if mode == "guidance" else "就业行情分析报告"
        return f"{request.query} - {suffix}"

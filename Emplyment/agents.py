from __future__ import annotations

from .llm_client import EmploymentLLMClient
from .models import EmploymentRequest, EmploymentSearchResult
from .prompts import (
    ADVISOR_SYSTEM_PROMPT,
    ANALYST_SYSTEM_PROMPT,
    RESEARCHER_SYSTEM_PROMPT,
    build_advisor_prompt,
    build_analyst_prompt,
    build_researcher_prompt,
)


class ResearcherAgent:
    def __init__(self, llm_client: EmploymentLLMClient):
        self.llm_client = llm_client

    def run(self, request: EmploymentRequest, mode: str, results: list[EmploymentSearchResult]) -> tuple[str, bool]:
        try:
            return (
                self.llm_client.generate_text(
                    RESEARCHER_SYSTEM_PROMPT,
                    build_researcher_prompt(request, mode, results),
                    temperature=0.2,
                ),
                True,
            )
        except Exception:
            return self._fallback(request, mode, results), False

    def _fallback(self, request: EmploymentRequest, mode: str, results: list[EmploymentSearchResult]) -> str:
        lines = [
            "## 研究员笔记",
            "",
            f"- 场景模式：{mode}",
            f"- 检索证据数：{len(results)}",
        ]
        if results:
            lines.append("- 当前证据主要集中在以下主题：")
            for item in results[:5]:
                lines.append(f"  - {item.title}: {item.snippet}")
        else:
            lines.append("- 当前没有外部检索证据，只能基于问题本身做初步判断。")
        if request.profile:
            lines.append(f"- 已提供用户画像字段：{', '.join(sorted(request.profile.keys()))}")
        lines.append("- 仍需重点核实：岗位持续招聘情况、技能要求是否一致、企业稳定性。")
        return "\n".join(lines)


class AnalystAgent:
    def __init__(self, llm_client: EmploymentLLMClient):
        self.llm_client = llm_client

    def run(
        self,
        request: EmploymentRequest,
        mode: str,
        researcher_note: str,
        results: list[EmploymentSearchResult],
    ) -> tuple[str, bool]:
        try:
            return (
                self.llm_client.generate_text(
                    ANALYST_SYSTEM_PROMPT,
                    build_analyst_prompt(request, mode, researcher_note, results),
                    temperature=0.25,
                ),
                True,
            )
        except Exception:
            return self._fallback(request, mode, researcher_note, results), False

    def _fallback(
        self,
        request: EmploymentRequest,
        mode: str,
        researcher_note: str,
        results: list[EmploymentSearchResult],
    ) -> str:
        demand = "中等"
        competition = "中等"
        if any(token in request.query for token in ("AI", "ai", "算法", "大模型", "产品")):
            competition = "较高"
        if any(token in request.query for token in ("深圳", "上海", "杭州", "北京")):
            demand = "较高"
        lines = [
            "## 分析师判断",
            "",
            f"- 总体判断：围绕“{request.query}”的就业判断需要把需求热度和个人匹配度分开看。",
            f"- 需求热度：{demand}",
            f"- 竞争强度：{competition}",
            "- 技能门槛：建议优先以真实 JD 高频技能为准，而不是只看经验帖。",
            "- 风险信号：热门方向容易出现叙事过热、岗位名称泛化、经验要求上移等问题。",
        ]
        if mode == "guidance":
            lines.append("- 指导补充：应优先确定主投岗位，再围绕该岗位准备简历、项目和面试故事。")
        if results:
            lines.append(f"- 证据基础：本轮共参考 {len(results)} 条检索结果。")
        else:
            lines.append("- 证据基础：当前主要依赖本地规则推断，结论置信度有限。")
        lines.append("")
        lines.append("### 研究员原始笔记摘要")
        lines.append(researcher_note)
        return "\n".join(lines)


class AdvisorAgent:
    def __init__(self, llm_client: EmploymentLLMClient):
        self.llm_client = llm_client

    def run(
        self,
        request: EmploymentRequest,
        mode: str,
        researcher_note: str,
        analyst_note: str,
        results: list[EmploymentSearchResult],
    ) -> tuple[str, bool]:
        try:
            return (
                self.llm_client.generate_markdown(
                    ADVISOR_SYSTEM_PROMPT,
                    build_advisor_prompt(request, mode, researcher_note, analyst_note, results),
                ),
                True,
            )
        except Exception:
            return self._fallback(request, mode, researcher_note, analyst_note, results), False

    def _fallback(
        self,
        request: EmploymentRequest,
        mode: str,
        researcher_note: str,
        analyst_note: str,
        results: list[EmploymentSearchResult],
    ) -> str:
        title = f"{request.query} - {'就业指导报告' if mode == 'guidance' else '就业行情分析报告'}"
        lines = [
            f"# {title}",
            "",
            "> 说明：当前报告由轻量三角色流程生成。若外部搜索或 LLM 不可用，部分内容会退回本地规则推断。",
            "",
            "## 一、摘要结论",
            "",
            f"- 本次问题归类为：{mode}",
            "- 当前建议不要只看单一岗位热度，而要同时判断岗位需求、个人匹配和企业稳定性。",
            "",
            "## 二、Researcher 检索摘要",
            "",
            researcher_note,
            "",
            "## 三、Analyst 结构化判断",
            "",
            analyst_note,
            "",
            "## 四、Advisor 建议",
            "",
        ]
        if mode == "guidance":
            lines.extend(
                [
                    "- 先把目标岗位收敛到 1 到 2 类，再围绕这两类岗位重写简历。",
                    "- 用真实 JD 倒推能力缺口，优先补最常见、最可证明的技能。",
                    "- 每周复盘投递反馈，及时调整岗位、城市和简历版本。",
                ]
            )
        else:
            lines.extend(
                [
                    "- 判断行情时优先看持续招聘、技能要求稳定性和企业业务方向。",
                    "- 比较城市时不要只看薪资，还要看岗位密度、企业质量和竞争人数。",
                    "- 对热门岗位保持警惕，很多热度来自内容平台讨论，不一定对应真实需求。",
                ]
            )
        lines.extend(
            [
                "",
                "## 五、30 天行动计划",
                "",
                "- 第 1 周：收集 20 到 30 个真实 JD，统计高频技能和经验要求。",
                "- 第 2 周：根据 JD 调整简历和项目表达，补齐最关键的 2 到 3 个能力缺口。",
                "- 第 3 周：集中投递一轮，并记录反馈、面试题和拒绝原因。",
                "- 第 4 周：根据反馈优化岗位选择和投递策略。",
                "",
                "## 六、参考证据",
                "",
            ]
        )
        if results:
            for idx, item in enumerate(results[:8], start=1):
                lines.append(f"- {idx}. [{item.title}]({item.url})")
                lines.append(f"  - 查询：{item.query}")
                lines.append(f"  - 摘要：{item.snippet}")
        else:
            lines.append("- 当前无外部检索结果，报告主要基于本地规则推断。")
        return "\n".join(lines)

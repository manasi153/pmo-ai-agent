# from __future__ import annotations

# from dataclasses import dataclass
# from typing import Any, Literal

# from . import governance_agent, portfolio_agent, staffing_agent, template_agent
# from .staffing_agent import StaffingRequest
# from .template_agent import TemplateRequest


# AgentName = Literal["STAFFING", "TEMPLATE", "PORTFOLIO", "GOVERNANCE"]


# @dataclass
# class OrchestratorResult:
#     agent: AgentName
#     payload: Any


# def handle_query(user_query: str) -> OrchestratorResult:

#     q = user_query.lower()

#     # =====================================================
#     # STAFFING – Employee Profile / Talent / Bench
#     # =====================================================
#     if any(k in q for k in [
#         "employee",
#         "profile",
#         "talent",
#         "bench",
#         "onboarding",
#         "offboarding",
#         "available resource",
#         "resource status",
#     ]):

#         req = StaffingRequest()

#         suggestions = staffing_agent.suggest_candidates(req, top_n=50)

#         return OrchestratorResult(
#             agent="STAFFING",
#             payload=[s.__dict__ for s in suggestions]
#         )

#     # =====================================================
#     # PROJECT TEAM LOOKUP
#     # =====================================================
#     if "who is working on" in q:

#         from ..data_loader import load_resource_allocation_master

#         df = load_resource_allocation_master()

#         project_name = user_query.split("on")[-1].strip()

#         team = df[
#             df["Project Name"]
#             .astype(str)
#             .str.contains(project_name, case=False, na=False)
#         ]

#         return OrchestratorResult(
#             agent="PORTFOLIO",
#             payload=team.to_dict(orient="records")
#         )

#     # =====================================================
#     # PORTFOLIO / KPI / UTILIZATION
#     # =====================================================
#     if any(k in q for k in [
#         "utilization",
#         "kpi",
#         "csat",
#         "project count",
#         "billing",
#         "invoice",
#         "portfolio",
#     ]):

#         result = portfolio_agent.answer_portfolio_question(user_query)

#         return OrchestratorResult(
#             agent="PORTFOLIO",
#             payload=result
#         )

#     # =====================================================
#     # GOVERNANCE
#     # =====================================================
#     if any(k in q for k in [
#         "governance",
#         "risk",
#         "escalation",
#         "rca",
#         "red",
#         "amber",
#         "health status",
#     ]):

#         items = governance_agent.get_checklist_for_phase("Initiation")

#         return OrchestratorResult(
#             agent="GOVERNANCE",
#             payload=[item.__dict__ for item in items]
#         )

#     # =====================================================
#     # DOCUMENT / TEMPLATE
#     # =====================================================
#     if any(k in q for k in [
#         "brd",
#         "tdd",
#         "mom",
#         "document",
#         "draft",
#         "template",
#         "format cv",
#     ]):

#         req = TemplateRequest(
#             template_type="BRD",
#             context={"summary": user_query}
#         )

#         doc = template_agent.generate_document(req)

#         return OrchestratorResult(
#             agent="TEMPLATE",
#             payload=doc
#         )

#     # =====================================================
#     # DEFAULT → Assume Staffing (Safer Default)
#     # =====================================================
#     req = StaffingRequest()
#     suggestions = staffing_agent.suggest_candidates(req, top_n=50)

#     return OrchestratorResult(
#         agent="STAFFING",
#         payload=[s.__dict__ for s in suggestions]
#     )


from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal
import re

from . import governance_agent, portfolio_agent, staffing_agent, template_agent
from .staffing_agent import StaffingRequest
from .template_agent import TemplateRequest

from ..data_loader import (
    load_talent_pool,
    load_resource_allocation_master,
)

AgentName = Literal["STAFFING", "TEMPLATE", "PORTFOLIO", "GOVERNANCE"]


@dataclass
class OrchestratorResult:
    agent: AgentName
    payload: Any

from ..llm import get_llm

llm = get_llm()
def handle_query(user_query: str) -> OrchestratorResult:

    q = user_query.lower()

    # =====================================================
    # EMPLOYEE PROFILE LOOKUP (NAME OR EMPLOYEE ID)
    # =====================================================
    if any(k in q for k in ["profile", "employee", "emp_id"]):

        df = load_talent_pool()

        # Normalize column just in case
        df["Employee Name"] = (
            df["Employee Name"]
            .astype(str)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

        # ---------------------------------------------
        # 1️⃣ SEARCH BY EMPLOYEE ID
        # ---------------------------------------------
        id_match = re.search(r"\b\d{4,}\b", user_query)

        if id_match:

            emp_id = id_match.group()

            emp = df[
                df["Employee Code"]
                .astype(str)
                .str.contains(emp_id, case=False, na=False)
            ]

            if not emp.empty:
                return OrchestratorResult(
                    agent="STAFFING",
                    payload=emp.to_dict(orient="records")
                )

        # ---------------------------------------------
        # 2️⃣ SEARCH BY EMPLOYEE NAME
        # ---------------------------------------------
        stop_words = [
            "show", "share", "profile", "employee",
            "details", "of", "the", "detailed"
        ]

        name_tokens = [
            word for word in user_query.split()
            if word.lower() not in stop_words
        ]

        search_name = " ".join(name_tokens).strip()

        emp = df[
            df["Employee Name"]
            .str.lower()
            .str.contains(search_name.lower(), na=False)
        ]

        if emp.empty:
            return OrchestratorResult(
                agent="STAFFING",
                payload="Employee not found in talent pool."
            )

        return OrchestratorResult(
            agent="STAFFING",
            payload=emp.to_dict(orient="records")
        )

    # =====================================================
    # TALENT POOL / BENCH / AVAILABLE RESOURCES
    # =====================================================
    if any(k in q for k in [
        "talent pool",
        "available resources",
        "bench",
        "available employees",
    ]):

        req = StaffingRequest()

        suggestions = staffing_agent.suggest_candidates(req, top_n=20)

        return OrchestratorResult(
            agent="STAFFING",
            payload=[s.__dict__ for s in suggestions]
        )

    # =====================================================
    # PROJECT TEAM LOOKUP
    # =====================================================
    if "who is working on" in q:

        df = load_resource_allocation_master()

        project_name = user_query.split("on")[-1].strip()

        team = df[
            df["Project Name"]
            .astype(str)
            .str.contains(project_name, case=False, na=False)
        ]

        return OrchestratorResult(
            agent="PORTFOLIO",
            payload=team.to_dict(orient="records")
        )

    # =====================================================
    # PORTFOLIO / UTILIZATION / KPI / BILLING
    # =====================================================
    if any(k in q for k in [
        "utilization",
        "bench strength",
        "project count",
        "kpi",
        "csat",
        "billing",
        "invoice",
        "timesheet",
        "portfolio",
    ]):

        result = portfolio_agent.answer_portfolio_question(user_query)

        return OrchestratorResult(
            agent="PORTFOLIO",
            payload=result
        )

    # =====================================================
    # GOVERNANCE / RISKS / ESCALATIONS
    # =====================================================
    if any(k in q for k in [
        "governance",
        "risk",
        "escalation",
        "health",
        "rca",
        "red",
        "amber",
    ]):

        items = governance_agent.get_checklist_for_phase("Execution")

        return OrchestratorResult(
            agent="GOVERNANCE",
            payload=[item.__dict__ for item in items]
        )

    # =====================================================
    # DOCUMENT / TEMPLATE GENERATION
    # =====================================================
    if any(k in q for k in [
        "brd",
        "tdd",
        "mom",
        "document",
        "draft",
        "template",
        "cv",
    ]):

        req = TemplateRequest(
            template_type="BRD",
            context={"summary": user_query}
        )

        doc = template_agent.generate_document(req)

        return OrchestratorResult(
            agent="TEMPLATE",
            payload=doc
        )

    # =====================================================
    # DEFAULT → SHOW TALENT POOL
    # =====================================================
    req = StaffingRequest()

    suggestions = staffing_agent.suggest_candidates(req, top_n=20)

    return OrchestratorResult(
        agent="STAFFING",
        payload=[s.__dict__ for s in suggestions]
    )

def detect_intent(llm, query: str):

    prompt = f"""
        You are an AI router for a PMO assistant.

        Classify the user's question into one of the following agents:

        STAFFING
        PORTFOLIO
        GOVERNANCE
        TEMPLATE

        Return ONLY the agent name.

        Examples:

        Show employee profile of Aakash → STAFFING
        Show available resources → STAFFING
        Track onboarding status → PORTFOLIO
        Show project health risks → GOVERNANCE
        Generate BRD document → TEMPLATE

        User question:
        {query}
        """

    return llm.complete(
        system_prompt="You are an AI router.",
        user_content=prompt,
        max_tokens=20,
    ).strip().upper()
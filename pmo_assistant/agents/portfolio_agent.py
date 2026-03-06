from __future__ import annotations

from typing import Dict
import pandas as pd

from ..data_loader import (
    load_csat_data,
    load_resource_allocation_master,
    load_resource_utilization_master,
)
from ..llm import get_llm


# ---------------------------------------------------
# KPI Computation Layer
# ---------------------------------------------------

def _compute_kpis() -> Dict[str, float]:

    util_df = load_resource_utilization_master()
    alloc_df = load_resource_allocation_master()
    csat_df = load_csat_data()

    kpis: Dict[str, float] = {}

    # Utilization KPI
    if {"Billable Hours", "Total Hours"}.issubset(util_df.columns):
        total = util_df["Total Hours"].sum()
        billable = util_df["Billable Hours"].sum()

        kpis["overall_utilization_pct"] = round((billable / total) * 100, 2) if total else 0.0
        kpis["billable_hours"] = int(billable)
        kpis["total_hours"] = int(total)

    # CSAT KPI
    if "CSAT Score" in csat_df.columns:
        kpis["average_csat"] = round(csat_df["CSAT Score"].mean(), 2)

    # Active Projects KPI
    if "Project ID" in alloc_df.columns:
        kpis["active_projects"] = alloc_df["Project ID"].nunique()

    # Bench %
    if "Bench %" in alloc_df.columns:
        kpis["average_bench_pct"] = round(alloc_df["Bench %"].mean() * 100, 2)

    return kpis


# ---------------------------------------------------
# Portfolio Question Answering
# ---------------------------------------------------

def answer_portfolio_question(question: str) -> str:

    llm = get_llm()

    util_df = load_resource_utilization_master()
    alloc_df = load_resource_allocation_master()
    csat_df = load_csat_data()

    kpis = _compute_kpis()

    summary = f"""
    Portfolio KPI Summary

    Overall Utilization: {kpis.get("overall_utilization_pct","NA")}%
    Average Bench %: {kpis.get("average_bench_pct","NA")}%
    Average CSAT: {kpis.get("average_csat","NA")}
    Active Projects: {kpis.get("active_projects","NA")}

    Resource Records: {len(util_df)}
    Allocation Records: {len(alloc_df)}
    CSAT Records: {len(csat_df)}
    """

    system_prompt = """
        You are PMO Exponent AI Agent.

        ROLE:
        You are a virtual PMO Assistant for Project Managers and Delivery Managers.
        You provide structured, data-driven, executive-level responses.

        You help with:
        • Utilization analytics
        • Bench strength
        • Resource allocation
        • Project portfolio insights
        • CSAT analysis
        • Onboarding / Offboarding tracking
        • PMO risk and governance insights

        STRICT RESPONSE RULES:

        1. Always return structured output.
        2. Never return a long paragraph.
        3. Use sections and bullet points.
        4. If tables help readability, include tables.
        5. Be concise and executive friendly.
        6. Never invent numbers not present in data.

        OUTPUT FORMAT:

        ### Utilization
        - Overall Utilization: %
        - Billable Hours: number
        - Total Hours: number

        ### Bench Strength
        - Average Bench %: %

        ### Portfolio Overview
        | Metric | Value |
        |------|------|
        | Active Projects | number |
        | Average CSAT | number |

        ### PMO Insight
        Short decision-focused insight for leadership.

        """

    user_content = f"""
        PORTFOLIO DATA SUMMARY

        {summary}

        USER QUESTION:
        {question}

        Answer using the structured PMO format described above.
        """

    response = llm.complete(
        system_prompt=system_prompt,
        user_content=user_content,
        max_tokens=600,
    )

    return response
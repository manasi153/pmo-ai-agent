# from __future__ import annotations

# from typing import Dict
# import pandas as pd

# from ..data_loader import (
#     load_csat_data,
#     load_resource_allocation_master,
#     load_resource_utilization_master,
# )
# from ..llm import get_llm


# # ---------------------------------------------------
# # KPI Computation Layer
# # ---------------------------------------------------

# def _compute_kpis() -> Dict[str, float]:

#     util_df = load_resource_utilization_master()
#     alloc_df = load_resource_allocation_master()
#     csat_df = load_csat_data()

#     kpis: Dict[str, float] = {}

#     # Utilization KPI
#     if {"Billable Hours", "Total Hours"}.issubset(util_df.columns):
#         total = util_df["Total Hours"].sum()
#         billable = util_df["Billable Hours"].sum()

#         kpis["overall_utilization_pct"] = round((billable / total) * 100, 2) if total else 0.0
#         kpis["billable_hours"] = int(billable)
#         kpis["total_hours"] = int(total)

#     # CSAT KPI
#     if "CSAT Score" in csat_df.columns:
#         kpis["average_csat"] = round(csat_df["CSAT Score"].mean(), 2)

#     # Active Projects KPI
#     if "Project ID" in alloc_df.columns:
#         kpis["active_projects"] = alloc_df["Project ID"].nunique()

#     # Bench %
#     if "Bench %" in alloc_df.columns:
#         kpis["average_bench_pct"] = round(alloc_df["Bench %"].mean() * 100, 2)

#     return kpis



# def answer_portfolio_question(question: str) -> str:

#     llm = get_llm()

#     kpis = _compute_kpis()

#     data_summary = f"""
#         Portfolio KPI Data:

#         Overall Utilization: {kpis.get("overall_utilization_pct", "N/A")} %
#         Average Bench Strength: {kpis.get("average_bench_pct", "N/A")} %
#         Active Projects: {kpis.get("active_projects", "N/A")}
#         Average CSAT Score: {kpis.get("average_csat", "N/A")}
#         """

#     system_prompt = """
#         You are a PMO Portfolio Intelligence Assistant.
        
#         You analyze PMO portfolio data and provide executive insights.
        
#         Rules:
#         - Use ONLY the provided KPI data.
#         - Do not invent numbers.
#         - Provide structured answers.
#         - Focus on utilization, capacity, project load, and client satisfaction.
#         """

#     user_prompt = f"""
#     Portfolio Data:
#     {data_summary}

#     Question:
#     {question}

#     Provide a clear PMO-level answer with insights.
#     """

#     return llm.complete(system_prompt, user_prompt)



from __future__ import annotations

from typing import Dict
import pandas as pd

from ..data_loader import (
    load_csat_data,
    load_resource_allocation_master,
    load_resource_utilization_master,
    load_talent_pool
)

from ..llm import get_llm


# ---------------------------------------------------
# Utility Functions
# ---------------------------------------------------

def _safe_numeric(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


def _find_column(df, keywords):

    for col in df.columns:
        name = col.lower().replace(" ", "").replace("_", "")
        if all(k in name for k in keywords):
            return col

    return None


# ---------------------------------------------------
# KPI Computation
# ---------------------------------------------------

def compute_kpis():

    util_df = load_resource_utilization_master()
    alloc_df = load_resource_allocation_master()
    csat_df = load_csat_data()
    talent_df = load_talent_pool()

    kpis = {}

    # --------------------------
    # UTILIZATION
    # --------------------------

    util_df.columns = util_df.columns.str.strip()

    total_col = _find_column(util_df, ["total"])
    billable_col = _find_column(util_df, ["billable"])

    if total_col and billable_col:

        total_hours = _safe_numeric(util_df[total_col]).sum()
        billable_hours = _safe_numeric(util_df[billable_col]).sum()

        utilization = (billable_hours / total_hours) * 100 if total_hours else 0

        kpis["total_hours"] = round(total_hours, 2)
        kpis["billable_hours"] = round(billable_hours, 2)
        kpis["utilization_pct"] = round(utilization, 2)

    # --------------------------
    # BENCH STRENGTH
    # --------------------------

    talent_df.columns = talent_df.columns.str.strip()

    bench_col = _find_column(talent_df, ["bench"])

    if bench_col:

        bench_series = _safe_numeric(talent_df[bench_col])
        avg_bench = bench_series.mean()

        kpis["bench_strength_pct"] = round(avg_bench, 2)

    # --------------------------
    # ACTIVE PROJECTS
    # --------------------------

    alloc_df.columns = alloc_df.columns.str.strip()

    project_col = _find_column(alloc_df, ["project"])

    if project_col:

        kpis["active_projects"] = int(alloc_df[project_col].nunique())

    # --------------------------
    # CSAT
    # --------------------------

    csat_df.columns = csat_df.columns.str.strip()

    csat_col = _find_column(csat_df, ["csat"])

    if csat_col:

        avg_csat = _safe_numeric(csat_df[csat_col]).mean()

        kpis["average_csat"] = round(avg_csat, 2)

    return kpis


# ---------------------------------------------------
# MAIN QUESTION ANSWERING
# ---------------------------------------------------

def answer_portfolio_question(question: str):

    llm = get_llm()

    kpis = compute_kpis()

    data_context = f"""
      
        Portfolio metrics calculated from Excel data:

        Total Hours: {kpis.get("total_hours")}
        Billable Hours: {kpis.get("billable_hours")}
        Utilization %: {kpis.get("utilization_pct")}

        Bench Strength %: {kpis.get("bench_strength_pct")}

        Active Projects: {kpis.get("active_projects")}

        Average CSAT: {kpis.get("average_csat")}

        User Question:
        {question}

        Answer the question using the metrics above.
        """

    system_prompt = """
        You are a PMO Portfolio Data Assistant.

        Your responsibility:
        Answer questions using ONLY the calculated data provided from Excel sheets.

        STRICT RULES:
        1. NEVER assume values.
        2. NEVER say "data not available" if a metric exists.
        3. Use the numbers exactly as provided.
        4. Answer ONLY the question asked.
        5. Do not add unrelated insights.

        Response format must always follow:

        Answer

        Metric Summary:
        - Utilization: <value> %
        - Bench Strength: <value> %
        - Active Projects: <value>
        - Average CSAT: <value>

        Explanation:
        Provide a short PMO explanation based strictly on the metrics.
        """

    user_prompt = f"""
        Portfolio Data:
        {data_context}

        User Question:
        {question}

        Provide a structured answer.
        """

    return llm.complete(system_prompt, user_prompt)
# from __future__ import annotations

# from dataclasses import dataclass
# from datetime import date
# from typing import List, Optional

# import pandas as pd

# from ..data_loader import (
#     load_resource_allocation_master,
#     load_talent_pool,
# )


# @dataclass
# class StaffingRequest:
#     role: Optional[str] = None
#     core_skill: Optional[str] = None
#     location: Optional[str] = None
#     primary_skills: Optional[str] = None  # free-text comma-separated
#     min_experience_years: Optional[float] = None
#     min_bench_pct: float = 0.5
#     start_date: Optional[date] = None
#     end_date: Optional[date] = None


# @dataclass
# class CandidateSuggestion:
#     emp_id: str
#     name: str
#     role: Optional[str]
#     core_skill: Optional[str]
#     location: Optional[str]
#     bench_pct: Optional[float]
#     status: Optional[str]
#     score: float
#     comments: str


# def _normalize_str(value: Optional[str]) -> str:
#     return (value or "").strip().lower()


# def _string_contains(haystack: Optional[str], needle: Optional[str]) -> bool:
#     if not haystack or not needle:
#         return True  # treat as pass-through if no filter
#     return _normalize_str(needle) in _normalize_str(haystack)


# def _skills_match(row_skills: Optional[str], requested: Optional[str]) -> float:
#     """
#     Very simple overlap score between two comma-separated skill lists.
#     """
#     if not requested:
#         return 1.0
#     if not row_skills:
#         return 0.0

#     req = {s.strip().lower() for s in requested.split(",") if s.strip()}
#     have = {s.strip().lower() for s in row_skills.split(",") if s.strip()}
#     if not req:
#         return 1.0
#     overlap = req & have
#     return len(overlap) / len(req)


# def _basic_filter(df: pd.DataFrame, req: StaffingRequest) -> pd.DataFrame:
#     """
#     Apply basic filters (role, core skill, location, bench %, status).
#     """
#     filtered = df.copy()

#     # Bench % and availability
#     if "Bench %" in filtered.columns:
#         filtered["Bench_num"] = pd.to_numeric(filtered["Bench %"], errors="coerce").fillna(0.0)
#         filtered = filtered[filtered["Bench_num"] >= req.min_bench_pct]

#     if "Status" in filtered.columns:
#         filtered = filtered[filtered["Status"].fillna("").str.contains("available", case=False)]

#     # Role / core skill / location filters (fuzzy contains)
#     if req.role:
#         filtered = filtered[
#             filtered["Role"].fillna("").str.contains(req.role, case=False, na=False)
#         ]
#     if req.core_skill:
#         filtered = filtered[
#             filtered["Core Skill"].fillna("").str.contains(req.core_skill, case=False, na=False)
#         ]
#     if req.location:
#         # Some rows use "Location", some might store in comments; start with Location col
#         if "Location" in filtered.columns:
#             mask = filtered["Location"].fillna("").str.contains(req.location, case=False, na=False)
#             filtered = filtered[mask]

#     # Experience filter (if present)
#     if req.min_experience_years is not None and "Overall Exp" in filtered.columns:
#         filtered["Exp_num"] = pd.to_numeric(filtered["Overall Exp"], errors="coerce").fillna(0.0)
#         filtered = filtered[filtered["Exp_num"] >= req.min_experience_years]

#     return filtered


# # def _add_simple_scores(df: pd.DataFrame, req: StaffingRequest) -> pd.DataFrame:
# #     """
# #     Compute a basic fit score based on skills, bench %, and experience.
# #     """
# #     df = df.copy()
# #     skills_col = "Technology" if "Technology" in df.columns else "Core Skill"

# #     scores = []
# #     for _, row in df.iterrows():
# #         skill_score = _skills_match(str(row.get(skills_col, "")), req.primary_skills)
# #         bench = float(row.get("Bench_num", 0.0))
# #         exp = float(row.get("Exp_num", 0.0))

# #         # Simple weighted score
# #         score = 0.5 * skill_score + 0.3 * (bench / 1.0) + 0.2 * min(exp / 10.0, 1.0)
# #         scores.append(score)

# #     df["FitScore"] = scores
# #     df = df.sort_values("FitScore", ascending=False)
# #     return df

# def _add_simple_scores(df: pd.DataFrame, req: StaffingRequest) -> pd.DataFrame:

#     df = df.copy()
#     skills_col = "Technology" if "Technology" in df.columns else "Core Skill"

#     scores = []
#     comments_list = []

#     for _, row in df.iterrows():

#         skill_score = _skills_match(str(row.get(skills_col, "")), req.primary_skills)
#         bench = float(row.get("Bench_num", 0.0))
#         exp = float(row.get("Exp_num", 0.0))

#         score = (
#             0.5 * skill_score +
#             0.3 * bench +
#             0.2 * min(exp / 10.0, 1.0)
#         )

#         comments = []
#         if skill_score > 0.7:
#             comments.append("Strong skill match")
#         if bench > 0.6:
#             comments.append("High bench availability")
#         if exp > 5:
#             comments.append("Experienced resource")

#         scores.append(score)
#         comments_list.append(" | ".join(comments))

#     df["FitScore"] = scores
#     df["FitComments"] = comments_list
#     df = df.sort_values("FitScore", ascending=False)

#     return df

# def suggest_candidates(req: StaffingRequest, top_n: int = 10) -> List[CandidateSuggestion]:
#     """
#     Main entrypoint for the Staffing Agent.

#     - Loads talent pool data.
#     - Applies filters.
#     - Computes a simple fit score.
#     - (Optionally) could be extended to cross-check allocations over the requested dates.
#     """
#     talent_df = load_talent_pool()
#     filtered = _basic_filter(talent_df, req)

#     if filtered.empty:
#         return []

#     scored = _add_simple_scores(filtered, req)
#     rows = scored.head(top_n).to_dict(orient="records")

#     suggestions: List[CandidateSuggestion] = []
#     for row in rows:
#         emp_id = str(row.get("Employee Code") or row.get("Emp ID") or "")
#         bench_pct = row.get("Bench_num", None)
#         suggestions.append(
#             CandidateSuggestion(
#                 emp_id=emp_id,
#                 name=str(row.get("Employee Name") or ""),
#                 role=row.get("Role"),
#                 core_skill=row.get("Core Skill"),
#                 location=row.get("Location"),
#                 bench_pct=float(bench_pct) if bench_pct is not None else None,
#                 status=row.get("Status"),
#                 score=float(row.get("FitScore", 0.0)),
#                 comments=str(row.get("FitComments") or ""),
#             )
#         )

#     return suggestions



from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import pandas as pd
import streamlit as st

from ..data_loader import (
    load_talent_pool,
    load_resource_allocation_master,
)


# -------------------------------------------------
# Data Models
# -------------------------------------------------

@dataclass
class StaffingRequest:
    role: Optional[str] = None
    core_skill: Optional[str] = None
    location: Optional[str] = None
    primary_skills: Optional[List[str]] = None
    min_bench_pct: float = 0.0
    min_experience_years: Optional[float] = None
    client_name: Optional[str] = None  # NEW


@dataclass
class CandidateSuggestion:
    emp_id: str
    name: str
    role: Optional[str]
    core_skill: Optional[str]
    location: Optional[str]
    bench_pct: float
    score: float
    status: Optional[str] = None
    comments: Optional[str] = None


# -------------------------------------------------
# Cached Load
# -------------------------------------------------

@st.cache_resource
def get_talent_df() -> pd.DataFrame:
    df = load_talent_pool()
    df.columns = df.columns.str.strip()
    if "Bench %" in df.columns:
        df["Bench %"] = pd.to_numeric(df["Bench %"], errors="coerce").fillna(0)
    return df


@st.cache_resource
def get_allocation_df() -> pd.DataFrame:
    df = load_resource_allocation_master()
    df.columns = df.columns.str.strip()
    return df


# -------------------------------------------------
# Main Suggestion Logic
# -------------------------------------------------

def suggest_candidates(req: StaffingRequest, top_n: int = 10) -> List[CandidateSuggestion]:

    talent_df = get_talent_df()
    alloc_df = get_allocation_df()

    working_df = talent_df.copy()

    # -------------------------------------------------
    # 1️⃣ CLIENT FILTER (Join Allocation + Talent)
    # -------------------------------------------------
    if req.client_name and "Client Name" in alloc_df.columns:

        client_alloc = alloc_df[
            alloc_df["Client Name"].astype(str)
            .str.contains(req.client_name, case=False, na=False)
        ]

        if not client_alloc.empty and "Employee Code" in client_alloc.columns:
            emp_ids = set(client_alloc["Employee Code"].astype(str))
            working_df = working_df[
                working_df["Employee Code"].astype(str).isin(emp_ids)
            ]

    # -------------------------------------------------
    # 2️⃣ Standard Filters
    # -------------------------------------------------
    if req.role and "Role" in working_df.columns:
        working_df = working_df[
            working_df["Role"].astype(str)
            .str.contains(req.role, case=False, na=False)
        ]

    if req.core_skill and "Core Skill" in working_df.columns:
        working_df = working_df[
            working_df["Core Skill"].astype(str)
            .str.contains(req.core_skill, case=False, na=False)
        ]

    if req.location and "Location" in working_df.columns:
        working_df = working_df[
            working_df["Location"].astype(str)
            .str.contains(req.location, case=False, na=False)
        ]

    if req.min_bench_pct > 0 and "Bench %" in working_df.columns:
        working_df = working_df[
            working_df["Bench %"] >= req.min_bench_pct
        ]

    if working_df.empty:
        return []

    # -------------------------------------------------
    # 3️⃣ Scoring (simple availability-based)
    # -------------------------------------------------
    working_df = working_df.copy()
    working_df["score"] = working_df.get("Bench %", 0)

    working_df = working_df.sort_values(
        by="score",
        ascending=False
    ).head(top_n)

    suggestions: List[CandidateSuggestion] = []

    for _, row in working_df.iterrows():
        suggestions.append(
            CandidateSuggestion(
                emp_id=str(row.get("Employee Code") or ""),
                name=str(row.get("Employee Name") or ""),
                role=row.get("Role"),
                core_skill=row.get("Core Skill"),
                location=row.get("Location"),
                bench_pct=float(row.get("Bench %", 0)),
                score=float(row.get("score", 0)),
                status=row.get("Status"),
            )
        )

    return suggestions

from ..llm import get_llm

llm = get_llm()


def extract_employee_name(query):

    prompt = f"""
Extract the employee name from the query.

Query:
{query}

Return ONLY the employee name.
If none present return NONE.
"""

    name = llm.complete(
        system_prompt="You extract entities from text.",
        user_content=prompt,
        max_tokens=20,
    )

    return name.strip()
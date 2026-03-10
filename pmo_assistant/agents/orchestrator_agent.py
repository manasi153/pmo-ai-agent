
# from __future__ import annotations

# from dataclasses import dataclass
# from typing import Any, Literal
# import re

# from . import governance_agent, portfolio_agent, staffing_agent, template_agent, action_agent
# from .staffing_agent import StaffingRequest
# from .template_agent import TemplateRequest

# from ..data_loader import (
#     load_talent_pool,
#     load_resource_allocation_master,
# )
# from ..llm import get_llm

# AgentName = Literal["STAFFING", "TEMPLATE", "PORTFOLIO", "GOVERNANCE", "ACTION"]

# @dataclass
# class OrchestratorResult:
#     agent: AgentName
#     payload: Any

# def detect_intent(llm, query: str) -> str:
#     prompt = f"""
#     You are an intelligent supervisor routing agent for an Enterprise PMO Assistant.
#     Analyze the user's query and classify it strictly into ONE of the following categories.
#     Return ONLY the category name. No markdown, no punctuation, no explanations.

#     ROUTING CATEGORIES:
#     - STAFFING: Queries regarding employee profiles, CV formatting, talent pool, available resources, bench strength, lookups for specific individuals, or onboarding/offboarding.
#     - PORTFOLIO: Queries asking "who is working on Project X", overall utilization metrics, KPIs, CSAT scores, billing, invoices, timesheets, or project loads.
#     - GOVERNANCE: Queries about project health, risks, escalations, RCA (Root Cause Analysis), RED/AMBER project status, or phase checklists.
#     - TEMPLATE: Queries requesting document generation, drafting BRD, TDD, MoM, completion certificates, or similar artefacts.
#     - ACTION: Queries explicitly asking to "allocate", "assign", "de-allocate", "add", or "update" a resource to a project.

#     Examples:
#     "Show employee profile of Aakash" -> STAFFING
#     "What is our current bench strength?" -> STAFFING
#     "Who is working on the Databricks migration?" -> PORTFOLIO
#     "Summarize the KPIs and average CSAT" -> PORTFOLIO
#     "Show project health risks and escalations" -> GOVERNANCE
#     "Draft a new BRD document" -> TEMPLATE
#     "Allocate employee 1045 to Project Phoenix" -> ACTION
#     "Assign resource 5092 to the Databricks migration at 50% capacity" -> ACTION

#     User Query:
#     "{query}"
#     """

#     result = llm.complete(
#         system_prompt="You are a strict, exact classification router. Return one word only.",
#         user_content=prompt,
#         max_tokens=10,
#         temperature=0.0
#     ).strip().upper()

#     # Safety constraint: Enforce valid routing
#     valid_agents = ["STAFFING", "PORTFOLIO", "GOVERNANCE", "TEMPLATE"]
#     for agent in valid_agents:
#         if agent in result:
#             return agent
            
#     return "STAFFING" # Safe fallback

# def extract_employee_name(llm, query: str) -> str:
#     prompt = f"""
#     Extract ONLY the employee name from the query.
#     If no name is present, return the exact word: NONE.
    
#     Query:
#     {query}
#     """
#     name = llm.complete(
#         system_prompt="You extract entities from text exactly as they appear.",
#         user_content=prompt,
#         max_tokens=20,
#         temperature=0.0
#     )
#     return name.strip()


# def handle_query(user_query: str) -> OrchestratorResult:

#     llm = get_llm()
    
#     # 1. Dynamically Detect Intent via LLM
#     agent_intent = detect_intent(llm, user_query)
#     q = user_query.lower()

#     # =====================================================
#     # ROUTE: STAFFING
#     # =====================================================
#     if agent_intent == "STAFFING":
#         # 1. ALWAYS load the dataframe first so it is never "unbound"
#         df = load_talent_pool()
        
#         # Safely clean the Employee Name column if it exists
#         if "Employee Name" in df.columns:
#             df["Employee Name"] = df["Employee Name"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()

#         # 2. Check for an Employee ID (4+ digits)
#         id_match = re.search(r"\b\d{4,}\b", user_query)
#         if id_match and "Employee Code" in df.columns:
#             emp_id = id_match.group()
#             emp = df[df["Employee Code"].astype(str).str.contains(emp_id, case=False, na=False)]
#             if not emp.empty:
#                 return OrchestratorResult(agent="STAFFING", payload=emp.to_dict(orient="records"))

#         # 3. Check for a specific Employee Name via LLM Extraction
#         extracted_name = extract_employee_name(llm, user_query)
#         if extracted_name and extracted_name.upper() != "NONE" and "Employee Name" in df.columns:
#             emp = df[df["Employee Name"].str.lower().str.contains(extracted_name.lower(), na=False)]
#             if not emp.empty:
#                 return OrchestratorResult(agent="STAFFING", payload=emp.to_dict(orient="records"))

#         # 4. Fallback: Show the general Talent Pool / Available Resources
#         req = StaffingRequest()
#         suggestions = staffing_agent.suggest_candidates(req, top_n=20)
        
#         return OrchestratorResult(
#             agent="STAFFING",
#             payload=[s.__dict__ for s in suggestions]
#         )

#     # =====================================================
#     # ROUTE: PORTFOLIO
#     # =====================================================
#     elif agent_intent == "PORTFOLIO":
#         if "who is working on" in q:
#             df = load_resource_allocation_master()
#             project_name = user_query.split("on")[-1].strip()
#             team = df[df["Project Name"].astype(str).str.contains(project_name, case=False, na=False)]
#             return OrchestratorResult(agent="PORTFOLIO", payload=team.to_dict(orient="records"))
            
#         result = portfolio_agent.answer_portfolio_question(user_query)
#         return OrchestratorResult(agent="PORTFOLIO", payload=result)

#     # =====================================================
#     # ROUTE: GOVERNANCE
#     # =====================================================
#     elif agent_intent == "GOVERNANCE":
#         items = governance_agent.get_checklist_for_phase("Execution")
#         return OrchestratorResult(
#             agent="GOVERNANCE",
#             payload=[item.__dict__ for item in items]
#         )

#     # =====================================================
#     # ROUTE: TEMPLATE
#     # =====================================================
#     elif agent_intent == "TEMPLATE":
#         req = TemplateRequest(
#             template_type="BRD",
#             context={"summary": user_query}
#         )
#         doc = template_agent.generate_document(req)
#         return OrchestratorResult(agent="TEMPLATE", payload=doc)

#     # =====================================================
#     # ROUTE: ACTION (Write-back)
#     # =====================================================
#     elif agent_intent == "ACTION":
#         # Ensure action_agent is imported at the top of the file!
#         parsed_request = action_agent.parse_action_request(user_query)
#         return OrchestratorResult(agent="ACTION", payload=parsed_request)

#     # Catch-all safe return
#     req = StaffingRequest()
#     suggestions = staffing_agent.suggest_candidates(req, top_n=20)
#     return OrchestratorResult(agent="STAFFING", payload=[s.__dict__ for s in suggestions])



from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal
import pandas as pd

from . import governance_agent, portfolio_agent, staffing_agent, template_agent
from .staffing_agent import StaffingRequest
from .template_agent import TemplateRequest

from ..config import EXCEL_FILES, resolve_file
from ..llm import get_llm

AgentName = Literal["STAFFING", "TEMPLATE", "PORTFOLIO", "GOVERNANCE", "ACTION"]

@dataclass
class OrchestratorResult:
    agent: AgentName
    payload: Any

def clean_df_for_ui(df: pd.DataFrame) -> list:
    if df.empty:
        return [{"Message": "No matching records found."}]
    df = df.dropna(how="all").copy()
    for col in df.columns:
        df[col] = df[col].astype(str).replace(["nan", "NaT", "None", "<NA>"], "").str.strip()
    return df.to_dict(orient="records")

def get_specific_sheet(file_key: str, sheet_name: str) -> pd.DataFrame:
    try:
        path = resolve_file(EXCEL_FILES[file_key])
        return pd.read_excel(path, sheet_name=sheet_name)
    except Exception:
        return pd.DataFrame()

def get_all_talent() -> pd.DataFrame:
    sheets = ["Talent Pool", "Blocked Resource", "Intern", "Future Pool", "Resign"]
    dfs = []
    for s in sheets:
        df = get_specific_sheet("talent_pool", s)
        if not df.empty:
            dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def detect_intent(llm, query: str) -> str:
    prompt = f"""
    Classify this PMO query into ONE category: STAFFING, PORTFOLIO, GOVERNANCE, TEMPLATE, or ACTION.
    Return ONLY the word.
    Query: "{query}"
    """
    try:
        res = llm.complete(system_prompt="You are a router. Return one word.", user_content=prompt, temperature=0.0)
        res = res.upper()
        for agent in ["STAFFING", "PORTFOLIO", "GOVERNANCE", "TEMPLATE", "ACTION"]:
            if agent in res:
                return agent
    except Exception:
        pass
    return "STAFFING"

def handle_query(user_query: str) -> OrchestratorResult:
    llm = get_llm()
    # Replace multiple spaces with a single space to prevent string matching failures
    q = re.sub(r'\s+', ' ', user_query.lower()).strip()

    # =====================================================
    # 1. BULLETPROOF LOGIC FOR EXACT HACKATHON QUERIES
    # =====================================================
    
    # -----------------------------------------------------
    # UTILIZATION QUERIES
    # -----------------------------------------------------
    # Overall Utilization
    if "overall" in q and "utilization" in q:
        df = get_specific_sheet("resource_utilization", "Dec'25")
        if not df.empty and "Billable Hours " in df.columns and "Tota Hrs Exc Leave" in df.columns:
            total_billable = pd.to_numeric(df["Billable Hours "], errors="coerce").sum()
            total_hours_exc = pd.to_numeric(df["Tota Hrs Exc Leave"], errors="coerce").sum()
            pct = round((total_billable / total_hours_exc) * 100, 2) if total_hours_exc else 0
            return OrchestratorResult(agent="PORTFOLIO", payload=f"**Overall Billable Utilization Percentage:** {pct}%")

    # Utilization Level Good
    if "utilization" in q and "good" in q:
        df = get_specific_sheet("resource_utilization", "Dec'25")
        # Accounts for Excel column typo (Utlization vs Utilization)
        util_col = "Utlization Lvl" if "Utlization Lvl" in df.columns else "Utilization Lvl"
        if util_col in df.columns:
            res = df[df[util_col].astype(str).str.lower().str.contains("good", na=False)]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res))

    # Utilization Level Critical
    if "utilization" in q and "critical" in q:
        df = get_specific_sheet("resource_utilization", "Dec'25")
        util_col = "Utlization Lvl" if "Utlization Lvl" in df.columns else "Utilization Lvl"
        if util_col in df.columns:
            res = df[df[util_col].astype(str).str.lower().str.contains("critical", na=False)]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res))

    # Between 50 and 85
    if "50" in q and "85" in q:
        df = get_specific_sheet("resource_utilization", "Dec'25")
        if "Billable Exc Leaves %" in df.columns:
            df["_val"] = pd.to_numeric(df["Billable Exc Leaves %"], errors="coerce")
            res = df[(df["_val"] >= 0.5) & (df["_val"] <= 0.85)]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res.drop(columns=["_val"])))

    # Below 50
    if "below 50" in q:
        df = get_specific_sheet("resource_utilization", "Dec'25")
        if "Billable Exc Leaves %" in df.columns:
            df["_val"] = pd.to_numeric(df["Billable Exc Leaves %"], errors="coerce")
            res = df[df["_val"] < 0.50]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res.drop(columns=["_val"])))

    # Below 85
    if "below 85" in q:
        df = get_specific_sheet("resource_utilization", "Dec'25")
        if "Billable Exc Leaves %" in df.columns:
            df["_val"] = pd.to_numeric(df["Billable Exc Leaves %"], errors="coerce")
            res = df[df["_val"] < 0.85]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res.drop(columns=["_val"])))
            
    # Equal to 100
    if "100" in q and ("equal" in q or "billable" in q):
        df = get_specific_sheet("resource_utilization", "Dec'25")
        if "Billable Exc Leaves %" in df.columns:
            df["_val"] = pd.to_numeric(df["Billable Exc Leaves %"], errors="coerce")
            res = df[df["_val"] >= 1.0]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res.drop(columns=["_val"])))

    # Zero billable
    if "zero" in q and "billable" in q:
        df = get_specific_sheet("resource_utilization", "Dec'25")
        if "Billable Hours " in df.columns:
            df["_val"] = pd.to_numeric(df["Billable Hours "], errors="coerce")
            res = df[df["_val"] == 0]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res.drop(columns=["_val"])))
            
    # COE
    if "coe" in q.split():
        df = get_specific_sheet("resource_utilization", "Dec'25")
        if "COE/Aixponent/Intern" in df.columns:
            res = df[df["COE/Aixponent/Intern"].astype(str).str.lower().str.contains("coe", na=False)]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res))
            
    # Aixponent
    if "aixponent" in q:
        df = get_specific_sheet("resource_utilization", "Dec'25")
        if "COE/Aixponent/Intern" in df.columns:
            res = df[df["COE/Aixponent/Intern"].astype(str).str.lower().str.contains("aixponent", na=False)]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res))

    # -----------------------------------------------------
    # STAFFING QUERIES
    # -----------------------------------------------------
    if "intern" in q:
        return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(get_specific_sheet("talent_pool", "Intern")))

    if "blocked" in q:
        return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(get_specific_sheet("talent_pool", "Blocked Resource")))

    if any(k in q for k in ["bench", "talent pool", "available"]):
        return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(get_specific_sheet("talent_pool", "Talent Pool")))

    # -----------------------------------------------------
    # PORTFOLIO: PROJECT TEAM LOOKUP
    # -----------------------------------------------------
    if "who is working on" in q:
        df = get_specific_sheet("resource_allocation", "Overall Project Res Allocation")
        
        target = q.split("who is working on")[-1].strip()
        target = re.sub(r'^(the|project)\s+', '', target).strip() 
        
        team = pd.DataFrame()
        if not df.empty:
            mask = pd.Series(False, index=df.index)
            if "Project Name" in df.columns:
                mask |= df["Project Name"].astype(str).str.contains(target, case=False, regex=False, na=False)
            if "Customer Name" in df.columns:
                mask |= df["Customer Name"].astype(str).str.contains(target, case=False, regex=False, na=False)
            team = df[mask]
        
        if team.empty:
            tp_df = get_all_talent()
            if not tp_df.empty:
                tp_mask = pd.Series(False, index=tp_df.index)
                if "Source Project/Ac" in tp_df.columns:
                    tp_mask |= tp_df["Source Project/Ac"].astype(str).str.contains(target, case=False, regex=False, na=False)
                if "Customer Name (If resource is Blocked)" in tp_df.columns:
                    tp_mask |= tp_df["Customer Name (If resource is Blocked)"].astype(str).str.contains(target, case=False, regex=False, na=False)
                if "Project Name\n(If resource is Blocked)" in tp_df.columns:
                    tp_mask |= tp_df["Project Name\n(If resource is Blocked)"].astype(str).str.contains(target, case=False, regex=False, na=False)
                
                team = tp_df[tp_mask]
                if not team.empty:
                    return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(team))

        return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(team))

    # =====================================================
    # 2. LLM DYNAMIC ROUTING FOR EVERYTHING ELSE
    # =====================================================
    agent_intent = detect_intent(llm, user_query)

    if agent_intent == "STAFFING":
        df = get_all_talent()
        
        if not df.empty:
            id_match = re.search(r"\b\d{4,}\b", user_query)
            if id_match and "Employee Code" in df.columns:
                emp = df[df["Employee Code"].astype(str).str.contains(id_match.group(), case=False, regex=False, na=False)]
                if not emp.empty:
                    return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(emp))

            if "Employee Name" in df.columns:
                query_padded = f" {q} "
                for _, row in df.iterrows():
                    full_name = str(row["Employee Name"]).strip().lower()
                    if not full_name or full_name == "nan": 
                        continue
                    
                    first_name = full_name.split()[0]
                    if full_name in q or f" {first_name} " in query_padded:
                        emp = df[df["Employee Name"].astype(str).str.lower() == full_name]
                        return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(emp))

                try:
                    name_res = llm.complete(
                        system_prompt="Extract ONLY the person's name. Return ONLY the name. No other words. No punctuation.",
                        user_content=f"Query: {user_query}",
                        temperature=0.0
                    ).strip().replace('"', '').replace("'", "")
                    
                    if name_res and name_res.upper() != "NONE":
                        emp = df[df["Employee Name"].astype(str).str.lower().str.contains(name_res.lower(), regex=False, na=False)]
                        if not emp.empty:
                            return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(emp))
                except Exception:
                    pass

        req = StaffingRequest()
        suggestions = staffing_agent.suggest_candidates(req, top_n=20)
        return OrchestratorResult(agent="STAFFING", payload=[s.__dict__ for s in suggestions])

    elif agent_intent == "PORTFOLIO":
        result = portfolio_agent.answer_portfolio_question(user_query)
        return OrchestratorResult(agent="PORTFOLIO", payload=result)

    elif agent_intent == "GOVERNANCE":
        items = governance_agent.get_checklist_for_phase("Execution")
        return OrchestratorResult(agent="GOVERNANCE", payload=[item.__dict__ for item in items])

    elif agent_intent == "TEMPLATE":
        req = TemplateRequest(template_type="BRD", context={"summary": user_query})
        doc = template_agent.generate_document(req)
        return OrchestratorResult(agent="TEMPLATE", payload=doc)

    elif agent_intent == "ACTION":
        try:
            from . import action_agent
            parsed_request = action_agent.parse_action_request(user_query)
            return OrchestratorResult(agent="ACTION", payload=parsed_request)
        except ImportError:
            return OrchestratorResult(agent="STAFFING", payload="Action Agent not yet implemented.")

    req = StaffingRequest()
    suggestions = staffing_agent.suggest_candidates(req, top_n=20)
    return OrchestratorResult(agent="STAFFING", payload=[s.__dict__ for s in suggestions])
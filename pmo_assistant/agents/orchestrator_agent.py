# from __future__ import annotations

# import re
# from dataclasses import dataclass
# from typing import Any, Literal
# import pandas as pd

# from . import governance_agent, portfolio_agent, staffing_agent, template_agent
# from .staffing_agent import StaffingRequest
# from .template_agent import TemplateRequest

# from ..config import EXCEL_FILES, resolve_file
# from ..llm import get_llm

# AgentName = Literal["STAFFING", "TEMPLATE", "PORTFOLIO", "GOVERNANCE", "ACTION", "GREETING", "DOC_QA"]

# @dataclass
# class OrchestratorResult:
#     agent: AgentName
#     payload: Any

# def clean_df_for_ui(df: pd.DataFrame) -> list:
#     if df.empty:
#         return [{"Message": "No matching records found."}]
#     df = df.dropna(how="all").copy()
#     for col in df.columns:
#         df[col] = df[col].astype(str).replace(["nan", "NaT", "None", "<NA>"], "").str.strip()
#     return df.to_dict(orient="records")

# def get_specific_sheet(file_key: str, sheet_name: str) -> pd.DataFrame:
#     try:
#         path = resolve_file(EXCEL_FILES[file_key])
#         return pd.read_excel(path, sheet_name=sheet_name)
#     except Exception:
#         return pd.DataFrame()

# def get_all_talent() -> pd.DataFrame:
#     sheets = ["Talent Pool", "Blocked Resource", "Intern", "Future Pool", "Resign"]
#     dfs = []
#     for s in sheets:
#         df = get_specific_sheet("talent_pool", s)
#         if not df.empty:
#             dfs.append(df)
#     return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

# def detect_intent(llm, query: str) -> str:
#     short_query = query[:1000] 
#     prompt = f"""
#     Classify this PMO query into ONE category: STAFFING, PORTFOLIO, GOVERNANCE, TEMPLATE, ACTION, or DOC_QA.
#     Return ONLY the word.
#     - DOC_QA: User asks to summarize, analyze, read, or review an uploaded document.
#     - TEMPLATE: User asks to create, draft, format, or generate a PMO document/CV.
#     - ACTION: User asks to allocate, assign, or execute a change for a resource.
#     - PORTFOLIO: Questions about project status, utilization %, or billing.
#     - STAFFING: Questions about bench, talent pool, interns, onboarding/offboarding lists, or employee search.
#     - GOVERNANCE: Questions about checklists or RCA.
    
#     Query: "{short_query}"
#     """
#     try:
#         res = llm.complete(system_prompt="You are a router. Return one word.", user_content=prompt, temperature=0.0)
#         res = res.upper()
#         for agent in ["STAFFING", "PORTFOLIO", "GOVERNANCE", "TEMPLATE", "ACTION", "DOC_QA"]:
#             if agent in res:
#                 return agent
#     except Exception:
#         pass
#     return "STAFFING"

# def handle_query(user_query: str) -> OrchestratorResult:
#     llm = get_llm()
#     q = re.sub(r'\s+', ' ', user_query.lower()).strip()
#     clean_q = q.strip("!.,?")

#     # =====================================================
#     # 0. GREETINGS INTERCEPT
#     # =====================================================
#     if clean_q in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "greetings", "hi there"]:
#         return OrchestratorResult(
#             agent="GREETING", 
#             payload="Hello! 👋 I am your PMO Exponent AI Assistant. How can I help you today? You can ask me about resource allocation, bench strength, project health, or ask me to summarize a document!"
#         )

#     # =====================================================
#     # 0.5 SMART CHATGPT-STYLE DOCUMENT SUMMARIZATION
#     # =====================================================
#     if "[attached document text]" in q and any(word in q for word in ["summar", "explain", "review", "details", "key points", "read", "analyze", "what"]):
#         parts = user_query.split("[ATTACHED DOCUMENT TEXT]:")
#         actual_query = parts[0].strip()
#         doc_text = parts[1].strip() if len(parts) > 1 else ""
        
#         if not doc_text:
#             return OrchestratorResult(agent="DOC_QA", payload="The uploaded document appears to be empty or unreadable. Please ensure it is a valid PDF, Word, or TXT file.")
            
#         if len(doc_text) > 14000:
#             doc_text = doc_text[:14000] + "\n\n...[DOCUMENT TRUNCATED TO FIT API LIMITS]..."
            
#         sys_prompt = """
#         You are an intelligent PMO AI Assistant, acting like ChatGPT. 
#         The user has uploaded a document for you to analyze. 
        
#         YOUR GOAL:
#         1. Automatically identify the document type (e.g., CV/Resume, BRD, MoM, Project Plan, Statement of Work).
#         2. Provide a highly structured, beautiful, and detailed summary tailored to that document type.
        
#         FORMATTING RULES:
#         - If it's a CV/Resume: Extract the candidate's Name, Total Experience, Core Skills/Tech Stack, and a brief Professional Summary.
#         - If it's a BRD/Project Doc: Extract the Project Goals, Scope, Key Requirements, and Deliverables.
#         - If it's an MoM/Meeting Note: Extract Key Discussions, Decisions Made, and Action Items.
#         - Otherwise: Provide a clear Executive Summary with bullet points covering the main themes.
        
#         Base your answer ONLY on the provided text. Do not invent details. Keep it professional and visually clean using Markdown.
#         """
        
#         user_msg = f"User Request: {actual_query}\n\nDocument Content:\n{doc_text}"
        
#         response = llm.complete(system_prompt=sys_prompt, user_content=user_msg, temperature=0.2)
#         return OrchestratorResult(agent="DOC_QA", payload=response)


#     # =====================================================
#     # 1. BULLETPROOF LOGIC FOR EXACT HACKATHON QUERIES
#     # =====================================================
    
#     # -----------------------------------------------------
#     # UTILIZATION QUERIES
#     # -----------------------------------------------------
#     if "overall" in q and "utilization" in q:
#         df = get_specific_sheet("resource_utilization", "Dec'25")
#         if not df.empty and "Billable Hours " in df.columns and "Tota Hrs Exc Leave" in df.columns:
#             total_billable = pd.to_numeric(df["Billable Hours "], errors="coerce").sum()
#             total_hours_exc = pd.to_numeric(df["Tota Hrs Exc Leave"], errors="coerce").sum()
#             pct = round((total_billable / total_hours_exc) * 100, 2) if total_hours_exc else 0
#             return OrchestratorResult(agent="PORTFOLIO", payload=f"**Overall Billable Utilization Percentage:** {pct}%")

#     if "utilization" in q and "good" in q:
#         df = get_specific_sheet("resource_utilization", "Dec'25")
#         util_col = "Utlization Lvl" if "Utlization Lvl" in df.columns else "Utilization Lvl"
#         if util_col in df.columns:
#             res = df[df[util_col].astype(str).str.lower().str.contains("good", na=False)]
#             return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res))

#     if "utilization" in q and "critical" in q:
#         df = get_specific_sheet("resource_utilization", "Dec'25")
#         util_col = "Utlization Lvl" if "Utlization Lvl" in df.columns else "Utilization Lvl"
#         if util_col in df.columns:
#             res = df[df[util_col].astype(str).str.lower().str.contains("critical", na=False)]
#             return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res))

#     if "50" in q and "85" in q:
#         df = get_specific_sheet("resource_utilization", "Dec'25")
#         if "Billable Exc Leaves %" in df.columns:
#             df["_val"] = pd.to_numeric(df["Billable Exc Leaves %"], errors="coerce")
#             res = df[(df["_val"] >= 0.5) & (df["_val"] <= 0.85)]
#             return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res.drop(columns=["_val"])))

#     if "below 50" in q:
#         df = get_specific_sheet("resource_utilization", "Dec'25")
#         if "Billable Exc Leaves %" in df.columns:
#             df["_val"] = pd.to_numeric(df["Billable Exc Leaves %"], errors="coerce")
#             res = df[df["_val"] < 0.50]
#             return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res.drop(columns=["_val"])))

#     if "below 85" in q:
#         df = get_specific_sheet("resource_utilization", "Dec'25")
#         if "Billable Exc Leaves %" in df.columns:
#             df["_val"] = pd.to_numeric(df["Billable Exc Leaves %"], errors="coerce")
#             res = df[df["_val"] < 0.85]
#             return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res.drop(columns=["_val"])))
            
#     if "100" in q and ("equal" in q or "billable" in q):
#         df = get_specific_sheet("resource_utilization", "Dec'25")
#         if "Billable Exc Leaves %" in df.columns:
#             df["_val"] = pd.to_numeric(df["Billable Exc Leaves %"], errors="coerce")
#             res = df[df["_val"] >= 1.0]
#             return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res.drop(columns=["_val"])))

#     if "zero" in q and "billable" in q:
#         df = get_specific_sheet("resource_utilization", "Dec'25")
#         if "Billable Hours " in df.columns:
#             df["_val"] = pd.to_numeric(df["Billable Hours "], errors="coerce")
#             res = df[df["_val"] == 0]
#             return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res.drop(columns=["_val"])))
            
#     if "coe" in q.split():
#         df = get_specific_sheet("resource_utilization", "Dec'25")
#         if "COE/Aixponent/Intern" in df.columns:
#             res = df[df["COE/Aixponent/Intern"].astype(str).str.lower().str.contains("coe", na=False)]
#             return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res))
            
#     if "aixponent" in q:
#         df = get_specific_sheet("resource_utilization", "Dec'25")
#         if "COE/Aixponent/Intern" in df.columns:
#             res = df[df["COE/Aixponent/Intern"].astype(str).str.lower().str.contains("aixponent", na=False)]
#             return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res))

#     # -----------------------------------------------------
#     # STAFFING: EMPLOYEE ID SMART SCANNER
#     # -----------------------------------------------------
#     emp_id_match = re.search(r"\b\d{4,6}\b", q)
#     if emp_id_match and not re.search(r"\b(202[0-9])\b", emp_id_match.group()):
#         target_id = emp_id_match.group()
#         df = get_all_talent()
#         if not df.empty and "Employee Code" in df.columns:
#             emp = df[df["Employee Code"].astype(str) == target_id]
#             if not emp.empty:
#                 return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(emp))
#             emp_contains = df[df["Employee Code"].astype(str).str.contains(target_id, na=False)]
#             if not emp_contains.empty:
#                 return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(emp_contains))

#     # -----------------------------------------------------
#     # STAFFING: EXPERIENCE SMART SCANNER
#     # -----------------------------------------------------
#     if any(kw in q for kw in ["experience", "exp", "years"]):
#         nums = re.findall(r'\b\d+(?:\.\d+)?\b', q)
#         valid_nums = [float(n) for n in nums if float(n) < 50]
        
#         if valid_nums:
#             df = get_all_talent()
#             if not df.empty and "Overall Exp" in df.columns:
#                 df["_val"] = pd.to_numeric(df["Overall Exp"], errors="coerce")
                
#                 if "between" in q and len(valid_nums) >= 2:
#                     val1, val2 = valid_nums[0], valid_nums[1]
#                     res = df[(df["_val"] >= min(val1, val2)) & (df["_val"] <= max(val1, val2))]
#                 elif any(kw in q for kw in ["more than", "greater than", "above", "over", "minimum", "at least", ">"]):
#                     res = df[df["_val"] >= valid_nums[0]]
#                 elif any(kw in q for kw in ["less than", "below", "under", "maximum", "<"]):
#                     res = df[df["_val"] <= valid_nums[0]]
#                 else:
#                     res = df[(df["_val"] >= valid_nums[0]) & (df["_val"] < valid_nums[0] + 1)]
                    
#                 if not res.empty:
#                     return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(res.drop(columns=["_val"])))
#                 else:
#                     return OrchestratorResult(agent="STAFFING", payload=f"No resources found matching the specified experience criteria.")

#     # -----------------------------------------------------
#     # STAFFING: GENERAL BENCH & STATUS QUERIES (NEW)
#     # -----------------------------------------------------
#     # 1. Onboarding / Joining Status (Reads from "Future Pool")
#     if any(kw in q for kw in ["onboard", "joining", "future pool", "to be hired", "new hire"]):
#         return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(get_specific_sheet("talent_pool", "Future Pool")))

#     # 2. Offboarding / Resigned Status (Reads from "Resign")
#     if any(kw in q for kw in ["offboard", "resign", "notice period", "leaving", "left"]):
#         return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(get_specific_sheet("talent_pool", "Resign")))

#     # 3. Interns
#     if "intern" in q:
#         return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(get_specific_sheet("talent_pool", "Intern")))

#     # 4. Blocked
#     if "blocked" in q:
#         return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(get_specific_sheet("talent_pool", "Blocked Resource")))

#     # 5. Bench / Available
#     if any(k in q for k in ["bench", "talent pool", "available"]):
#         return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(get_specific_sheet("talent_pool", "Talent Pool")))


#     # -----------------------------------------------------
#     # PORTFOLIO: PROJECT TEAM LOOKUP (SMART MATCHER)
#     # -----------------------------------------------------
#     if any(kw in q for kw in ["who is working", "assigned to", "team for", "resources for"]):
#         target = ""
#         for kw in ["who is working on", "who is working in", "who is assigned to", "team for", "resources for", "who is working"]:
#             if kw in q:
#                 target = q.split(kw)[-1].strip()
#                 break
                
#         target = re.sub(r'\s+and\s+in\s+what\s+capacity.*', '', target) 
#         target = re.sub(r'\bproject\b', '', target) 
#         target = re.sub(r'^the\s+', '', target) 
#         target = target.strip(" ?.") 
        
#         team = pd.DataFrame()
        
#         if target:
#             df = get_specific_sheet("resource_allocation", "Overall Project Res Allocation")
#             if not df.empty:
#                 mask = pd.Series(False, index=df.index)
#                 if "Project Name" in df.columns:
#                     mask |= df["Project Name"].astype(str).str.contains(target, case=False, regex=False, na=False)
#                 if "Customer Name" in df.columns:
#                     mask |= df["Customer Name"].astype(str).str.contains(target, case=False, regex=False, na=False)
#                 team = df[mask]
            
#             if team.empty:
#                 tp_df = get_all_talent()
#                 if not tp_df.empty:
#                     tp_mask = pd.Series(False, index=tp_df.index)
#                     if "Source Project/Ac" in tp_df.columns:
#                         tp_mask |= tp_df["Source Project/Ac"].astype(str).str.contains(target, case=False, regex=False, na=False)
#                     if "Customer Name (If resource is Blocked)" in tp_df.columns:
#                         tp_mask |= tp_df["Customer Name (If resource is Blocked)"].astype(str).str.contains(target, case=False, regex=False, na=False)
#                     if "Project Name\n(If resource is Blocked)" in tp_df.columns:
#                         tp_mask |= tp_df["Project Name\n(If resource is Blocked)"].astype(str).str.contains(target, case=False, regex=False, na=False)
                    
#                     team = tp_df[tp_mask]
#                     if not team.empty:
#                         return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(team))

#         if not team.empty:
#             return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(team))
#         elif target:
#             return OrchestratorResult(agent="PORTFOLIO", payload=f"Could not find any active or benched resources working on a project matching '{target}'.")

#     # =====================================================
#     # 2. LLM DYNAMIC ROUTING FOR EVERYTHING ELSE
#     # =====================================================
#     agent_intent = detect_intent(llm, user_query)

#     if agent_intent == "DOC_QA":
#         if "[ATTACHED DOCUMENT TEXT]:" in user_query:
#             parts = user_query.split("[ATTACHED DOCUMENT TEXT]:")
#             actual_query = parts[0].strip()
#             doc_text = parts[1].strip() if len(parts) > 1 else ""
            
#             if not doc_text:
#                 return OrchestratorResult(agent="DOC_QA", payload="The uploaded document appears to be empty or unreadable.")
                
#             if len(doc_text) > 12000:
#                 doc_text = doc_text[:12000] + "\n\n...[DOCUMENT TRUNCATED TO FIT API LIMITS]..."
                
#             sys_prompt = "You are a PMO AI Assistant. Answer the user's request based ONLY on the provided document."
#             user_msg = f"User Request: {actual_query}\n\nDocument Content:\n{doc_text}"
            
#             response = llm.complete(system_prompt=sys_prompt, user_content=user_msg, temperature=0.2)
#             return OrchestratorResult(agent="DOC_QA", payload=response)
#         else:
#             return OrchestratorResult(agent="DOC_QA", payload="Please upload a document using the sidebar first so I can review or summarize it for you.")

#     if agent_intent == "STAFFING":
#         df = get_all_talent()
        
#         if not df.empty:
#             if "Employee Name" in df.columns:
#                 query_padded = f" {q} "
#                 for _, row in df.iterrows():
#                     full_name = str(row["Employee Name"]).strip().lower()
#                     if not full_name or full_name == "nan": 
#                         continue
                    
#                     first_name = full_name.split()[0]
#                     if full_name in q or f" {first_name} " in query_padded:
#                         emp = df[df["Employee Name"].astype(str).str.lower() == full_name]
#                         return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(emp))

#                 try:
#                     name_res = llm.complete(
#                         system_prompt="Extract ONLY the person's name. Return ONLY the name. No other words. No punctuation.",
#                         user_content=f"Query: {user_query}",
#                         temperature=0.0
#                     ).strip().replace('"', '').replace("'", "")
                    
#                     if name_res and name_res.upper() != "NONE":
#                         emp = df[df["Employee Name"].astype(str).str.lower().str.contains(name_res.lower(), regex=False, na=False)]
#                         if not emp.empty:
#                             return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(emp))
#                 except Exception:
#                     pass

#         req = StaffingRequest()
#         suggestions = staffing_agent.suggest_candidates(req, top_n=20)
#         return OrchestratorResult(agent="STAFFING", payload=[s.__dict__ for s in suggestions])

#     elif agent_intent == "PORTFOLIO":
#         result = portfolio_agent.answer_portfolio_question(user_query)
#         return OrchestratorResult(agent="PORTFOLIO", payload=result)

#     elif agent_intent == "GOVERNANCE":
#         items = governance_agent.get_checklist_for_phase("Execution")
#         return OrchestratorResult(agent="GOVERNANCE", payload=[item.__dict__ for item in items])

#     elif agent_intent == "TEMPLATE":
#         req = TemplateRequest(template_type="BRD", context={"summary": user_query})
#         doc = template_agent.generate_document(req)
#         return OrchestratorResult(agent="TEMPLATE", payload=doc)

#     elif agent_intent == "ACTION":
#         try:
#             from . import action_agent
#             parsed_request = action_agent.parse_action_request(user_query)
#             return OrchestratorResult(agent="ACTION", payload=parsed_request)
#         except ImportError:
#             return OrchestratorResult(agent="STAFFING", payload="Action Agent not yet implemented.")

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

AgentName = Literal["STAFFING", "TEMPLATE", "PORTFOLIO", "GOVERNANCE", "ACTION", "GREETING", "DOC_QA"]

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
    short_query = query[:1000] 
    prompt = f"""
    Classify this PMO query into ONE category: STAFFING, PORTFOLIO, GOVERNANCE, TEMPLATE, ACTION, or DOC_QA.
    Return ONLY the word.
    - DOC_QA: User asks to summarize, analyze, read, or review an uploaded document.
    - TEMPLATE: User asks to create, draft, format, or generate a PMO document/CV/Resume.
    - ACTION: User asks to allocate, assign, or execute a change for a resource.
    - PORTFOLIO: Questions about project status, utilization %, or billing.
    - STAFFING: Questions about bench, talent pool, interns, onboarding/offboarding lists, or employee search.
    - GOVERNANCE: Questions about checklists or RCA.
    
    Query: "{short_query}"
    """
    try:
        res = llm.complete(system_prompt="You are a router. Return one word.", user_content=prompt, temperature=0.0)
        res = res.upper()
        for agent in ["STAFFING", "PORTFOLIO", "GOVERNANCE", "TEMPLATE", "ACTION", "DOC_QA"]:
            if agent in res:
                return agent
    except Exception:
        pass
    return "STAFFING"

def handle_query(user_query: str) -> OrchestratorResult:
    llm = get_llm()
    q = re.sub(r'\s+', ' ', user_query.lower()).strip()
    clean_q = q.strip("!.,?")

    # =====================================================
    # 0. GREETINGS INTERCEPT
    # =====================================================
    if clean_q in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "greetings", "hi there"]:
        return OrchestratorResult(
            agent="GREETING", 
            payload="Hello! 👋 I am your PMO Exponent AI Assistant. How can I help you today? You can ask me about resource allocation, bench strength, project health, or ask me to summarize a document!"
        )

    # =====================================================
    # 0.5 SMART CHATGPT-STYLE DOCUMENT SUMMARIZATION
    # =====================================================
    if "[attached document text]" in q and any(word in q for word in ["summar", "explain", "review", "details", "key points", "read", "analyze", "what"]):
        parts = user_query.split("[ATTACHED DOCUMENT TEXT]:")
        actual_query = parts[0].strip()
        doc_text = parts[1].strip() if len(parts) > 1 else ""
        
        if not doc_text:
            return OrchestratorResult(agent="DOC_QA", payload="The uploaded document appears to be empty or unreadable. Please ensure it is a valid PDF, Word, or TXT file.")
            
        if len(doc_text) > 14000:
            doc_text = doc_text[:14000] + "\n\n...[DOCUMENT TRUNCATED TO FIT API LIMITS]..."
            
        sys_prompt = """
        You are an intelligent PMO AI Assistant, acting like ChatGPT. 
        The user has uploaded a document for you to analyze. 
        
        YOUR GOAL:
        1. Automatically identify the document type (e.g., CV/Resume, BRD, MoM, Project Plan, Statement of Work).
        2. Provide a highly structured, beautiful, and detailed summary tailored to that document type.
        
        FORMATTING RULES:
        - If it's a CV/Resume: Extract the candidate's Name, Total Experience, Core Skills/Tech Stack, and a brief Professional Summary.
        - If it's a BRD/Project Doc: Extract the Project Goals, Scope, Key Requirements, and Deliverables.
        - If it's an MoM/Meeting Note: Extract Key Discussions, Decisions Made, and Action Items.
        - Otherwise: Provide a clear Executive Summary with bullet points covering the main themes.
        
        Base your answer ONLY on the provided text. Do not invent details. Keep it professional and visually clean using Markdown.
        """
        
        user_msg = f"User Request: {actual_query}\n\nDocument Content:\n{doc_text}"
        
        response = llm.complete(system_prompt=sys_prompt, user_content=user_msg, temperature=0.2)
        return OrchestratorResult(agent="DOC_QA", payload=response)


    # =====================================================
    # 1. BULLETPROOF LOGIC FOR EXACT HACKATHON QUERIES
    # =====================================================
    
    # -----------------------------------------------------
    # UTILIZATION QUERIES
    # -----------------------------------------------------
    if "overall" in q and "utilization" in q:
        df = get_specific_sheet("resource_utilization", "Dec'25")
        if not df.empty and "Billable Hours " in df.columns and "Tota Hrs Exc Leave" in df.columns:
            total_billable = pd.to_numeric(df["Billable Hours "], errors="coerce").sum()
            total_hours_exc = pd.to_numeric(df["Tota Hrs Exc Leave"], errors="coerce").sum()
            pct = round((total_billable / total_hours_exc) * 100, 2) if total_hours_exc else 0
            return OrchestratorResult(agent="PORTFOLIO", payload=f"**Overall Billable Utilization Percentage:** {pct}%")

    if "utilization" in q and "good" in q:
        df = get_specific_sheet("resource_utilization", "Dec'25")
        util_col = "Utlization Lvl" if "Utlization Lvl" in df.columns else "Utilization Lvl"
        if util_col in df.columns:
            res = df[df[util_col].astype(str).str.lower().str.contains("good", na=False)]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res))

    if "utilization" in q and "critical" in q:
        df = get_specific_sheet("resource_utilization", "Dec'25")
        util_col = "Utlization Lvl" if "Utlization Lvl" in df.columns else "Utilization Lvl"
        if util_col in df.columns:
            res = df[df[util_col].astype(str).str.lower().str.contains("critical", na=False)]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res))

    if "50" in q and "85" in q:
        df = get_specific_sheet("resource_utilization", "Dec'25")
        if "Billable Exc Leaves %" in df.columns:
            df["_val"] = pd.to_numeric(df["Billable Exc Leaves %"], errors="coerce")
            res = df[(df["_val"] >= 0.5) & (df["_val"] <= 0.85)]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res.drop(columns=["_val"])))

    if "below 50" in q:
        df = get_specific_sheet("resource_utilization", "Dec'25")
        if "Billable Exc Leaves %" in df.columns:
            df["_val"] = pd.to_numeric(df["Billable Exc Leaves %"], errors="coerce")
            res = df[df["_val"] < 0.50]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res.drop(columns=["_val"])))

    if "below 85" in q:
        df = get_specific_sheet("resource_utilization", "Dec'25")
        if "Billable Exc Leaves %" in df.columns:
            df["_val"] = pd.to_numeric(df["Billable Exc Leaves %"], errors="coerce")
            res = df[df["_val"] < 0.85]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res.drop(columns=["_val"])))
            
    if "100" in q and ("equal" in q or "billable" in q):
        df = get_specific_sheet("resource_utilization", "Dec'25")
        if "Billable Exc Leaves %" in df.columns:
            df["_val"] = pd.to_numeric(df["Billable Exc Leaves %"], errors="coerce")
            res = df[df["_val"] >= 1.0]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res.drop(columns=["_val"])))

    if "zero" in q and "billable" in q:
        df = get_specific_sheet("resource_utilization", "Dec'25")
        if "Billable Hours " in df.columns:
            df["_val"] = pd.to_numeric(df["Billable Hours "], errors="coerce")
            res = df[df["_val"] == 0]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res.drop(columns=["_val"])))
            
    if "coe" in q.split():
        df = get_specific_sheet("resource_utilization", "Dec'25")
        if "COE/Aixponent/Intern" in df.columns:
            res = df[df["COE/Aixponent/Intern"].astype(str).str.lower().str.contains("coe", na=False)]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res))
            
    if "aixponent" in q:
        df = get_specific_sheet("resource_utilization", "Dec'25")
        if "COE/Aixponent/Intern" in df.columns:
            res = df[df["COE/Aixponent/Intern"].astype(str).str.lower().str.contains("aixponent", na=False)]
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(res))

    # -----------------------------------------------------
    # STAFFING: EMPLOYEE ID SMART SCANNER
    # -----------------------------------------------------
    emp_id_match = re.search(r"\b\d{4,6}\b", q)
    if emp_id_match and not re.search(r"\b(202[0-9])\b", emp_id_match.group()):
        target_id = emp_id_match.group()
        df = get_all_talent()
        if not df.empty and "Employee Code" in df.columns:
            emp = df[df["Employee Code"].astype(str) == target_id]
            if not emp.empty:
                return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(emp))
            emp_contains = df[df["Employee Code"].astype(str).str.contains(target_id, na=False)]
            if not emp_contains.empty:
                return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(emp_contains))

    # -----------------------------------------------------
    # STAFFING: EXPERIENCE SMART SCANNER
    # -----------------------------------------------------
    if any(kw in q for kw in ["experience", "exp", "years"]):
        nums = re.findall(r'\b\d+(?:\.\d+)?\b', q)
        valid_nums = [float(n) for n in nums if float(n) < 50]
        
        if valid_nums:
            df = get_all_talent()
            if not df.empty and "Overall Exp" in df.columns:
                df["_val"] = pd.to_numeric(df["Overall Exp"], errors="coerce")
                
                if "between" in q and len(valid_nums) >= 2:
                    val1, val2 = valid_nums[0], valid_nums[1]
                    res = df[(df["_val"] >= min(val1, val2)) & (df["_val"] <= max(val1, val2))]
                elif any(kw in q for kw in ["more than", "greater than", "above", "over", "minimum", "at least", ">"]):
                    res = df[df["_val"] >= valid_nums[0]]
                elif any(kw in q for kw in ["less than", "below", "under", "maximum", "<"]):
                    res = df[df["_val"] <= valid_nums[0]]
                else:
                    res = df[(df["_val"] >= valid_nums[0]) & (df["_val"] < valid_nums[0] + 1)]
                    
                if not res.empty:
                    return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(res.drop(columns=["_val"])))
                else:
                    return OrchestratorResult(agent="STAFFING", payload=f"No resources found matching the specified experience criteria.")

    # -----------------------------------------------------
    # STAFFING: GENERAL BENCH & STATUS QUERIES
    # -----------------------------------------------------
    if any(kw in q for kw in ["onboard", "joining", "future pool", "to be hired", "new hire"]):
        return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(get_specific_sheet("talent_pool", "Future Pool")))

    if any(kw in q for kw in ["offboard", "resign", "notice period", "leaving", "left"]):
        return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(get_specific_sheet("talent_pool", "Resign")))

    if "intern" in q:
        return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(get_specific_sheet("talent_pool", "Intern")))

    if "blocked" in q:
        return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(get_specific_sheet("talent_pool", "Blocked Resource")))

    if any(k in q for k in ["bench", "talent pool", "available"]):
        return OrchestratorResult(agent="STAFFING", payload=clean_df_for_ui(get_specific_sheet("talent_pool", "Talent Pool")))


    # -----------------------------------------------------
    # PORTFOLIO: PROJECT TEAM LOOKUP (SMART MATCHER)
    # -----------------------------------------------------
    if any(kw in q for kw in ["who is working", "assigned to", "team for", "resources for"]):
        target = ""
        for kw in ["who is working on", "who is working in", "who is assigned to", "team for", "resources for", "who is working"]:
            if kw in q:
                target = q.split(kw)[-1].strip()
                break
                
        target = re.sub(r'\s+and\s+in\s+what\s+capacity.*', '', target) 
        target = re.sub(r'\bproject\b', '', target) 
        target = re.sub(r'^the\s+', '', target) 
        target = target.strip(" ?.") 
        
        team = pd.DataFrame()
        
        if target:
            df = get_specific_sheet("resource_allocation", "Overall Project Res Allocation")
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

        if not team.empty:
            return OrchestratorResult(agent="PORTFOLIO", payload=clean_df_for_ui(team))
        elif target:
            return OrchestratorResult(agent="PORTFOLIO", payload=f"Could not find any active or benched resources working on a project matching '{target}'.")

    # =====================================================
    # 2. LLM DYNAMIC ROUTING FOR EVERYTHING ELSE
    # =====================================================
    agent_intent = detect_intent(llm, user_query)

    if agent_intent == "DOC_QA":
        if "[ATTACHED DOCUMENT TEXT]:" in user_query:
            parts = user_query.split("[ATTACHED DOCUMENT TEXT]:")
            actual_query = parts[0].strip()
            doc_text = parts[1].strip() if len(parts) > 1 else ""
            
            if not doc_text:
                return OrchestratorResult(agent="DOC_QA", payload="The uploaded document appears to be empty or unreadable.")
                
            if len(doc_text) > 12000:
                doc_text = doc_text[:12000] + "\n\n...[DOCUMENT TRUNCATED TO FIT API LIMITS]..."
                
            sys_prompt = "You are a PMO AI Assistant. Answer the user's request based ONLY on the provided document."
            user_msg = f"User Request: {actual_query}\n\nDocument Content:\n{doc_text}"
            
            response = llm.complete(system_prompt=sys_prompt, user_content=user_msg, temperature=0.2)
            return OrchestratorResult(agent="DOC_QA", payload=response)
        else:
            return OrchestratorResult(agent="DOC_QA", payload="Please upload a document using the sidebar first so I can review or summarize it for you.")

    # -----------------------------------------------------
    # NEW: SMART TEMPLATE GENERATOR
    # -----------------------------------------------------
    elif agent_intent == "TEMPLATE":
        parts = user_query.split("[ATTACHED DOCUMENT TEXT]:")
        actual_query = parts[0].strip()
        doc_text = parts[1].strip() if len(parts) > 1 else ""
        
        q_lower = actual_query.lower()
        
        # Determine the target template based on keywords
        target_template = "BRD" # Default
        if any(word in q_lower for word in ["cv", "resume", "profile", "exponent format", "exponent standard"]):
            target_template = "CV"
        elif any(word in q_lower for word in ["mom", "minutes", "meeting"]):
            target_template = "MoM"
        elif any(word in q_lower for word in ["weekly", "status"]):
            target_template = "WeeklyStatus"
            
        # Structure the context for the agent
        if doc_text:
            context_data = {"User Instructions": actual_query, "Uploaded Document Data": doc_text}
        else:
            context_data = {"User Request": actual_query}
            
        req = TemplateRequest(template_type=target_template, context=context_data)
        
        try:
            doc = template_agent.generate_document(req)
            return OrchestratorResult(agent="TEMPLATE", payload=doc)
        except Exception as e:
            return OrchestratorResult(agent="TEMPLATE", payload=f"Failed to generate template: {str(e)}")


    elif agent_intent == "STAFFING":
        df = get_all_talent()
        
        if not df.empty:
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
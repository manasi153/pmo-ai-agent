# from __future__ import annotations


# import sys
# import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# from datetime import date

# import streamlit as st

# from pmo_assistant.agents import governance_agent, orchestrator_agent, portfolio_agent, staffing_agent, template_agent
# from pmo_assistant.agents.staffing_agent import StaffingRequest
# from pmo_assistant.agents.template_agent import TemplateRequest, TemplateType
# from pmo_assistant.data_loader import build_employee_summaries, load_talent_pool


# st.set_page_config(page_title="PMO Assistant", layout="wide")


# def staffing_page() -> None:
#     st.header("Staffing Assistant")
#     st.write("Find best-fit resources from the talent pool for a project.")

#     # Build a dropdown of distinct roles from the talent pool for convenience.
#     # Fallback: if the Role column is missing or empty, we keep a free-text input.
#     roles = []
#     try:
#         df_roles = load_talent_pool()
#         if "Role" in df_roles.columns:
#             roles = sorted({str(r).strip() for r in df_roles["Role"].dropna() if str(r).strip()})
#     except Exception:
#         roles = []

#     with st.form("staffing_form"):
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             if roles:
#                 role_options = ["Any"] + roles
#                 role = st.selectbox("Role", role_options)
#                 if role == "Any":
#                     role = ""
#             else:
#                 role = st.text_input("Role (e.g. Data Engineer, PM)")
#             core_skill = st.text_input("Core Skill / Domain (e.g. Qlik, Databricks)")
#         with col2:
#             location = st.text_input("Preferred Location (city / region / remote)")
#             primary_skills = st.text_input("Primary Skills (comma-separated)")
#         with col3:
#             min_exp = st.number_input("Minimum Experience (years)", min_value=0.0, max_value=40.0, value=0.0, step=0.5)
#             min_bench = st.slider("Minimum Bench %", min_value=0.0, max_value=1.0, value=0.5, step=0.05)

#         submitted = st.form_submit_button("Suggest Candidates")

#     if submitted:
#         req = StaffingRequest(
#             role=role or None,
#             core_skill=core_skill or None,
#             location=location or None,
#             primary_skills=primary_skills or None,
#             min_experience_years=min_exp if min_exp > 0 else None,
#             min_bench_pct=min_bench,
#         )
#         suggestions = staffing_agent.suggest_candidates(req=req, top_n=20)

#         if not suggestions:
#             st.warning("No candidates found with the given filters. Try relaxing some criteria.")
#             return

#         data = [
#             {
#                 "Emp ID": s.emp_id,
#                 "Name": s.name,
#                 "Role": s.role,
#                 "Core Skill": s.core_skill,
#                 "Location": s.location,
#                 "Bench %": s.bench_pct,
#                 "Status": s.status,
#                 "Fit Score": round(s.score, 3),
#                 "Comments": s.comments,
                
#             }
#             for s in suggestions
#         ]
#         st.subheader("Suggested Candidates")
#         # Older Streamlit versions do not support use_container_width argument
#         st.dataframe(data)


# # def template_page() -> None:
# #     st.header("Document / Template Assistant")
# #     st.write("Generate BRD, TDD, MoM, Weekly Status, RCA, Completion Certificate and more.")

# #     template_map = {
# #         "Business Requirement Document (BRD)": "BRD",
# #         "Technical Design Document (TDD)": "TDD",
# #         "Minutes of Meeting (MoM)": "MoM",
# #         "Weekly Status Deck (text draft)": "WeeklyStatus",
# #         "Project Plan – high level summary": "ProjectPlanSummary",
# #         "Root Cause Analysis (RCA) narrative": "RCA",
# #         "Project Completion Certificate": "CompletionCertificate",
# #     }

# #     choice_label = st.selectbox("Template Type", list(template_map.keys()))
# #     template_type_str = template_map[choice_label]
# #     template_type: TemplateType = template_type_str  # type: ignore[assignment]

# #     st.markdown("#### Provide context for this artefact")
# #     with st.form("template_form"):
# #         project_name = st.text_input("Project Name")
# #         customer_name = st.text_input("Customer / Client Name")
# #         business_goal = st.text_area("Business Goal / Problem Statement")
# #         scope = st.text_area("Scope (and optionally out-of-scope)")
# #         risks = st.text_area("Key Risks / Dependencies (optional)")
# #         stakeholders = st.text_area("Key Stakeholders (optional)")
# #         tech_stack = st.text_area("High-level Technology / Platform (optional)")
# #         additional_notes = st.text_area("Any additional notes (optional)")

# #         submitted = st.form_submit_button("Generate Draft Document")

# #     if submitted:
# #         context = {
# #             "Project Name": project_name,
# #             "Customer Name": customer_name,
# #             "Business Goal": business_goal,
# #             "Scope": scope,
# #             "Risks and Dependencies": risks,
# #             "Stakeholders": stakeholders,
# #             "Tech Stack": tech_stack,
# #             "Additional Notes": additional_notes,
# #         }
# #         req = TemplateRequest(template_type=template_type, context=context)
# #         draft = template_agent.generate_document(req)

# #         st.subheader("Draft Document")
# #         st.write(draft)
# #         st.download_button(
# #             "Download as .txt",
# #             data=draft.encode("utf-8"),
# #             file_name=f"{template_type_str}_draft.txt",
# #             mime="text/plain",
# #         )

# def template_page() -> None:
#     st.header("Document / Template Assistant")
#     st.write("Generate BRD, TDD, MoM, Weekly Status, RCA, Completion Certificate, and format CVs.")

#     template_map = {
#         "Business Requirement Document (BRD)": "BRD",
#         "Technical Design Document (TDD)": "TDD",
#         "Minutes of Meeting (MoM)": "MoM",
#         "Weekly Status Deck (text draft)": "WeeklyStatus",
#         "Project Plan – high level summary": "ProjectPlanSummary",
#         "Root Cause Analysis (RCA) narrative": "RCA",
#         "Project Completion Certificate": "CompletionCertificate",
#         "Exponent Standard CV Formatting": "CV",  # <-- Added CV here
#     }

#     choice_label = st.selectbox("Template Type", list(template_map.keys()))
#     template_type_str = template_map[choice_label]
#     template_type: TemplateType = template_type_str  # type: ignore[assignment]

#     st.markdown("#### Provide context or raw data for this artefact")
    
#     with st.form("template_form"):
#         # If the user selects CV, provide a large text area for raw resume dumping
#         if template_type == "CV":
#             st.info("Paste the employee's unstructured resume, LinkedIn profile text, or raw experience notes below.")
#             raw_resume_text = st.text_area("Raw Resume Data", height=300)
#             submitted = st.form_submit_button("Format CV")
            
#             if submitted:
#                 context = {"Raw Resume Content": raw_resume_text}
                
#         # Otherwise, show the standard project documentation fields
#         else:
#             project_name = st.text_input("Project Name")
#             customer_name = st.text_input("Customer / Client Name")
#             business_goal = st.text_area("Business Goal / Problem Statement")
#             scope = st.text_area("Scope (and optionally out-of-scope)")
#             risks = st.text_area("Key Risks / Dependencies (optional)")
#             stakeholders = st.text_area("Key Stakeholders (optional)")
#             tech_stack = st.text_area("High-level Technology / Platform (optional)")
#             additional_notes = st.text_area("Any additional notes (optional)")

#             submitted = st.form_submit_button("Generate Draft Document")
            
#             if submitted:
#                 context = {
#                     "Project Name": project_name,
#                     "Customer Name": customer_name,
#                     "Business Goal": business_goal,
#                     "Scope": scope,
#                     "Risks and Dependencies": risks,
#                     "Stakeholders": stakeholders,
#                     "Tech Stack": tech_stack,
#                     "Additional Notes": additional_notes,
#                 }

#     if submitted:
#         req = TemplateRequest(template_type=template_type, context=context)
        
#         with st.spinner("Generating document..."):
#             draft = template_agent.generate_document(req)

#         st.subheader("Draft Document")
#         st.write(draft)
#         st.download_button(
#             "Download as .txt",
#             data=draft.encode("utf-8"),
#             file_name=f"{template_type_str}_draft.txt",
#             mime="text/plain",
#         )
# def portfolio_page() -> None:
#     st.header("Portfolio & KPI Assistant")
#     st.write("Ask questions about CSAT, utilization, allocations, and portfolio trends.")
#     question = st.text_area("Question", height=120)
#     # question = st.text_area(
#     #     "Question",
#     #     value="Summarize key portfolio highlights for the last year using CSAT, utilization and allocations.",
#     #     height=120,
#     # )

#     if st.button("Answer"):
#         answer = portfolio_agent.answer_portfolio_question(question)
#         st.subheader("Answer")
#         st.write(answer)


# def governance_page() -> None:
#     st.header("Governance & Artefacts")
#     st.write("See which artefacts are expected per phase, and use the Document Assistant to generate them.")

#     phase = st.selectbox("Project Phase", ["Initiation", "Planning", "Execution", "Closure"])
#     items = governance_agent.get_checklist_for_phase(phase=phase)  # type: ignore[arg-type]

#     rows = [
#         {
#             "Artefact": item.artefact,
#             "Mandatory": "Yes" if item.mandatory else "Optional",
#             "Description": item.description,
#         }
#         for item in items
#     ]
#     st.subheader(f"Expected Artefacts for {phase}")
#     # Older Streamlit versions do not support use_container_width argument
#     st.dataframe(rows)

#     st.info("Use the Document / Template Assistant tab to generate drafts for any missing artefacts.")


# def chat_page() -> None:
#     st.header("Chat – Agentic PMO Assistant")
#     st.write("Ask anything; the orchestrator will route your query to the right agent.")

#     user_query = st.text_area("Your question", height=150)
#     if st.button("Ask"):
#         if not user_query.strip():
#             st.warning("Please type a question.")
#             return
#     import pandas as pd

#     result = orchestrator_agent.handle_query(user_query)
#     st.subheader(f"Routed to: {result.agent}")

#     # ------------------------------
#     # STAFFING → Table
#     # ------------------------------
#     if result.agent == "STAFFING" and isinstance(result.payload, list):
#         if result.payload:
#             if isinstance(result.payload, list):
#                 st.dataframe(result.payload)
#         else:
#             st.write(result.payload)

#     # ------------------------------
#     # GOVERNANCE → Table
#     # ------------------------------
#     elif result.agent == "GOVERNANCE" and isinstance(result.payload, list):
#         if result.payload:
#             df = pd.DataFrame(result.payload)
#             st.dataframe(df, use_container_width=True)
#         else:
#             st.warning("No checklist items found.")

#     # ------------------------------
#     # PORTFOLIO → Table (if structured)
#     # ------------------------------
#     elif result.agent == "PORTFOLIO":
#         if isinstance(result.payload, list):
#             df = pd.DataFrame(result.payload)
#             st.dataframe(df, use_container_width=True)
#         else:
#             st.write(result.payload)
#     # ------------------------------
#     # ACTION → Write Confirmation Form
#     # ------------------------------
#     elif result.agent == "ACTION":
#         st.info("I detected a request to modify resource allocations. Please review the details below:")
        
#         req = result.payload # This is the ActionRequest dataclass
        
#         with st.form("action_confirmation_form"):
#             st.subheader("Allocation Request Details")
#             col1, col2 = st.columns(2)
#             with col1:
#                 emp_id = st.text_input("Employee ID", value=req.emp_id)
#                 start_date = st.text_input("Start Date", value=req.start_date)
#             with col2:
#                 project_name = st.text_input("Project Name", value=req.project_name)
#                 alloc_pct = st.text_input("Allocation %", value=req.allocation_pct)
                
#             notes = st.text_input("Notes", value=req.notes)
            
#             confirm = st.form_submit_button("Confirm & Execute Allocation")
            
#         if confirm:
#             # Update the request object with any manual edits the user made in the form
#             req.emp_id = emp_id
#             req.project_name = project_name
#             req.allocation_pct = alloc_pct
#             req.start_date = start_date
#             req.notes = notes
            
#             from pmo_assistant.agents import action_agent
#             with st.spinner("Writing to Excel database..."):
#                 status_msg = action_agent.execute_allocation(req)
                
#             if "✅" in status_msg:
#                 st.success(status_msg)
#             else:
#                 st.error(status_msg)
#     # ------------------------------
#     # TEMPLATE / GENERAL → Text
#     # ------------------------------
#     else:
#         st.write(result.payload)
#         # result = orchestrator_agent.handle_query(user_query)
#         # st.subheader(f"Routed to: {result.agent}")
#         # st.write(result.payload)


# def main() -> None:
#     st.sidebar.title("PMO Assistant")
#     page = st.sidebar.radio(
#         "Select mode",
#         ["Staffing", "Documents", "Portfolio / KPIs", "Governance", "Chat (Agentic)"],
#     )

#     if page == "Staffing":
#         staffing_page()
#     elif page == "Documents":
#         template_page()
#     elif page == "Portfolio / KPIs":
#         portfolio_page()
#     elif page == "Governance":
#         governance_page()
#     else:
#         chat_page()


# if __name__ == "__main__":
#     main()


from __future__ import annotations

import sys
import os

# Ensure the app can find the pmo_assistant package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from pmo_assistant.agents import orchestrator_agent

st.set_page_config(page_title="PMO Exponent AI Agent", page_icon="🤖", layout="wide")

def main() -> None:
    st.title("🤖 PMO Exponent AI Agent")
    st.markdown("""
    Welcome to your virtual PMO assistant. You can ask me to:
    * *Show me the current talent pool and available resources*
    * *Who is working on Project X?*
    * *Draft a BRD for the Databricks migration project*
    * *Show me the list of Blocked resources*
    """)
    st.divider()

    # 1. Initialize Chat History in Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 2. Render Existing Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            content = message["content"]
            # If the content is a DataFrame (like Staffing or Portfolio tables)
            if isinstance(content, pd.DataFrame):
                st.dataframe(content, use_container_width=True)
            # If the content is text (like Templates or Governance rules)
            else:
                st.markdown(content)

    # 3. Handle New User Input
    if prompt := st.chat_input("Ask the PMO Assistant a question..."):
        
        # Add user message to history and render it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 4. Generate and Render Assistant Response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing PMO data..."):
                try:
                    # Send the query to the backend orchestrator
                    result = orchestrator_agent.handle_query(prompt)
                    payload = result.payload

                    # Determine how to render the payload based on what the agent returned
                    if isinstance(payload, list) and len(payload) > 0 and isinstance(payload[0], dict):
                        # It's a list of dictionaries (Table Data) -> Convert to DataFrame
                        df = pd.DataFrame(payload)
                        st.dataframe(df, use_container_width=True)
                        st.session_state.messages.append({"role": "assistant", "content": df})
                    
                    elif isinstance(payload, str):
                        # It's a text response or generated document
                        st.markdown(payload)
                        st.session_state.messages.append({"role": "assistant", "content": payload})
                        
                        # Add a download button if it's a large generated document
                        if result.agent == "TEMPLATE" and len(payload) > 100:
                            st.download_button(
                                label="📥 Download Document",
                                data=payload,
                                file_name="Generated_Artefact.txt",
                                mime="text/plain"
                            )
                    
                    elif result.agent == "ACTION":
                        # If it's the parsed ActionRequest object
                        st.info("Action Request Detected:")
                        st.write(payload)
                        st.session_state.messages.append({"role": "assistant", "content": f"Action parsed: {payload}"})
                        
                    else:
                        # Fallback for empty tables or unknown formats
                        st.write(payload)
                        st.session_state.messages.append({"role": "assistant", "content": "No data returned."})

                except Exception as e:
                    error_msg = f"**Error:** Could not process the request. \n\n`{str(e)}`"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()
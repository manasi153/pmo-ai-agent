# from __future__ import annotations

# import sys
# import os

# # Ensure the app can find the pmo_assistant package
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# import streamlit as st
# import pandas as pd
# from pmo_assistant.agents import orchestrator_agent

# st.set_page_config(page_title="PMO Exponent AI Agent", page_icon="🤖", layout="wide")

# def main() -> None:
#     st.title("🤖 PMO Exponent AI Agent")
#     st.markdown("""
#     Welcome to your virtual PMO assistant. You can ask me to:
#     * *Show me the current talent pool and available resources*
#     * *Who is working on Project X?*
#     * *Draft a BRD for the Databricks migration project*
#     * *Show me the list of Blocked resources*
#     """)
#     st.divider()

#     # 1. Initialize Chat History in Session State
#     if "messages" not in st.session_state:
#         st.session_state.messages = []

#     # 2. Render Existing Chat History
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             content = message["content"]
#             # If the content is a DataFrame (like Staffing or Portfolio tables)
#             if isinstance(content, pd.DataFrame):
#                 st.dataframe(content, use_container_width=True)
#             # If the content is text (like Templates or Governance rules)
#             else:
#                 st.markdown(content)

#     # 3. Handle New User Input
#     if prompt := st.chat_input("Ask the PMO Assistant a question..."):
        
#         # Add user message to history and render it
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         with st.chat_message("user"):
#             st.markdown(prompt)

#         # 4. Generate and Render Assistant Response
#         with st.chat_message("assistant"):
#             with st.spinner("Analyzing PMO data..."):
#                 try:
#                     # Send the query to the backend orchestrator
#                     result = orchestrator_agent.handle_query(prompt)
#                     payload = result.payload

#                     # Determine how to render the payload based on what the agent returned
#                     if isinstance(payload, list) and len(payload) > 0 and isinstance(payload[0], dict):
#                         # It's a list of dictionaries (Table Data) -> Convert to DataFrame
#                         df = pd.DataFrame(payload)
#                         st.dataframe(df, use_container_width=True)
#                         st.session_state.messages.append({"role": "assistant", "content": df})
                    
#                     elif isinstance(payload, str):
#                         # It's a text response or generated document
#                         st.markdown(payload)
#                         st.session_state.messages.append({"role": "assistant", "content": payload})
                        
#                         # Add a download button if it's a large generated document
#                         if result.agent == "TEMPLATE" and len(payload) > 100:
#                             st.download_button(
#                                 label="📥 Download Document",
#                                 data=payload,
#                                 file_name="Generated_Artefact.txt",
#                                 mime="text/plain"
#                             )
                    
#                     elif result.agent == "ACTION":
#                         # If it's the parsed ActionRequest object
#                         st.info("Action Request Detected:")
#                         st.write(payload)
#                         st.session_state.messages.append({"role": "assistant", "content": f"Action parsed: {payload}"})
                        
#                     else:
#                         # Fallback for empty tables or unknown formats
#                         st.write(payload)
#                         st.session_state.messages.append({"role": "assistant", "content": "No data returned."})

#                 except Exception as e:
#                     error_msg = f"**Error:** Could not process the request. \n\n`{str(e)}`"
#                     st.error(error_msg)
#                     st.session_state.messages.append({"role": "assistant", "content": error_msg})

# if __name__ == "__main__":
#     main()


from __future__ import annotations

import sys
import os
import io

# Ensure the app can find the pmo_assistant package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import PyPDF2
from docx import Document
from pmo_assistant.agents import orchestrator_agent

st.set_page_config(page_title="PMO Exponent AI Agent", page_icon="🤖", layout="wide")

def extract_text_from_upload(uploaded_file) -> str:
    """Helper function to extract text from PDF, DOCX, or TXT files."""
    text = ""
    try:
        if uploaded_file.name.endswith(".pdf"):
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif uploaded_file.name.endswith(".docx"):
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif uploaded_file.name.endswith(".txt"):
            text = uploaded_file.getvalue().decode("utf-8")
    except Exception as e:
        return f"Error extracting text: {str(e)}"
    return text

def main() -> None:
    # ==========================================
    # HIDE STREAMLIT BRANDING & GITHUB ICONS
    # ==========================================
    hide_streamlit_style = """
        <style>
        /* Hide the default Streamlit footer */
        footer {visibility: hidden;}
        
        /* Hide the top right hamburger menu */
        #MainMenu {visibility: hidden;}
        
        /* Hide the Streamlit Cloud Deploy button */
        .stDeployButton {display: none;}
        
        /* Hide the bottom right GitHub and Streamlit Viewer Badges */
        .viewerBadge_container__1QSob {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        
        /* Aggressive catch-all for bottom right floating elements */
        div[class^="viewerBadge"] {display: none !important;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    # ==========================================
    # 0. INITIALIZE SESSION STATE VARIABLES
    # ==========================================
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_text" not in st.session_state:
        st.session_state.uploaded_text = ""
    if "current_file" not in st.session_state:
        st.session_state.current_file = None
        
    # NEW: A key to forcefully reset the file uploader widget
    if "file_uploader_key" not in st.session_state:
        st.session_state.file_uploader_key = 0 

    # ==========================================
    # SIDEBAR: NEW CHAT & FILE UPLOAD
    # ==========================================
    with st.sidebar:
        st.title("PMO Assistant")
        
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            # 1. Wipe all memory
            st.session_state.messages = []
            st.session_state.current_file = None
            st.session_state.uploaded_text = ""
            # 2. Change the key to completely destroy and recreate the file uploader box
            st.session_state.file_uploader_key += 1 
            st.rerun()
            
        st.divider()
        
        # --- FILE UPLOAD MODULE ---
        st.markdown("### 📎 Context Document")
        st.caption("Upload a raw CV, meeting notes, or project summary.")
        
        # Notice we are passing the dynamic key here!
        uploaded_doc = st.file_uploader(
            "Upload File", 
            type=["pdf", "docx", "txt"], 
            label_visibility="collapsed",
            key=str(st.session_state.file_uploader_key)
        )
        
        # --- AUTO-SUMMARIZE LOGIC ---
        if uploaded_doc is not None:
            if st.session_state.current_file != uploaded_doc.name:
                
                st.session_state.current_file = uploaded_doc.name
                st.session_state.uploaded_text = extract_text_from_upload(uploaded_doc)
                
                st.session_state.messages.append({
                    "role": "user", 
                    "content": f"📎 **Uploaded:** `{uploaded_doc.name}`. Please analyze and summarize it."
                })
                
                with st.spinner(f"Reading {uploaded_doc.name}..."):
                    backend_query = f"Summarize this document in detail.\n\n[ATTACHED DOCUMENT TEXT]:\n{st.session_state.uploaded_text}"
                    try:
                        result = orchestrator_agent.handle_query(backend_query)
                        st.session_state.messages.append({"role": "assistant", "content": result.payload})
                    except Exception as e:
                        st.session_state.messages.append({"role": "assistant", "content": f"Failed to read document: {str(e)}"})
                
                st.rerun()
                
        else:
            if st.session_state.current_file is not None:
                st.session_state.current_file = None
                st.session_state.uploaded_text = ""
            
        st.divider()
        st.markdown("""
        **Try asking about:**
        * *Show me the current talent pool*
        * *Who is working on project Mankind POC?*
        * *Format the uploaded CV to Exponent standards*
        * *Draft a BRD from the uploaded meeting notes*
        """)

    # ==========================================
    # MAIN CHAT INTERFACE
    # ==========================================
    st.title("🤖 PMO Exponent AI Agent")

    if len(st.session_state.messages) == 0:
        st.markdown("Welcome! I am your virtual PMO assistant. Type your question below or **upload a document in the sidebar** to get an instant summary.")
        st.divider()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            content = message["content"]
            if isinstance(content, pd.DataFrame):
                st.dataframe(content, use_container_width=True)
            else:
                st.markdown(content)

    # ==========================================
    # HANDLE FOLLOW-UP QUESTIONS / COMMANDS
    # ==========================================
    if prompt := st.chat_input("Ask a question or request a template..."):
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing PMO data..."):
                try:
                    backend_query = prompt
                    if st.session_state.uploaded_text:
                        backend_query = f"{prompt}\n\n[ATTACHED DOCUMENT TEXT]:\n{st.session_state.uploaded_text}"

                    result = orchestrator_agent.handle_query(backend_query)
                    payload = result.payload

                    if isinstance(payload, list) and len(payload) > 0 and isinstance(payload[0], dict):
                        df = pd.DataFrame(payload)
                        st.dataframe(df, use_container_width=True)
                        st.session_state.messages.append({"role": "assistant", "content": df})
                    
                    elif isinstance(payload, str):
                        st.markdown(payload)
                        st.session_state.messages.append({"role": "assistant", "content": payload})
                        
                        if result.agent == "TEMPLATE" and len(payload) > 100:
                            st.download_button(
                                label="📥 Download Document",
                                data=payload,
                                file_name="Generated_Artefact.txt",
                                mime="text/plain"
                            )
                    
                    elif result.agent == "ACTION":
                        st.info("Action Request Detected:")
                        st.write(payload)
                        st.session_state.messages.append({"role": "assistant", "content": f"Action parsed: {payload}"})
                        
                    else:
                        st.write(payload)
                        st.session_state.messages.append({"role": "assistant", "content": "No data returned."})

                except Exception as e:
                    error_msg = f"**Error:** Could not process the request. \n\n`{str(e)}`"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()
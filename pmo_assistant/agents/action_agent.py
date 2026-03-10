from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import date
import pandas as pd
import streamlit as st

from ..data_loader import resolve_file
from ..config import EXCEL_FILES
from ..llm import get_llm

@dataclass
class ActionRequest:
    action_type: str  # e.g., "ALLOCATE", "DEALLOCATE", "UPDATE"
    emp_id: str
    project_name: str
    allocation_pct: str
    start_date: str
    notes: str

def parse_action_request(query: str) -> ActionRequest:
    """
    Uses the LLM to extract allocation details into a structured JSON format.
    """
    llm = get_llm()
    
    system_prompt = """
    You are an AI data extraction agent for a PMO Assistant.
    Extract the resource allocation details from the user's query and output ONLY a valid JSON object.
    Do not add markdown formatting, explanations, or commentary.
    
    Required JSON schema:
    {
      "action_type": "ALLOCATE or DEALLOCATE",
      "emp_id": "Employee ID (if missing, output 'UNKNOWN')",
      "project_name": "Project Name (if missing, output 'UNKNOWN')",
      "allocation_pct": "Percentage number as string (e.g. '100', '50'. Default to '100' if missing)",
      "start_date": "Start date if mentioned, otherwise 'TBD'",
      "notes": "Any other context or notes"
    }
    """
    
    response = llm.complete(system_prompt=system_prompt, user_content=query, temperature=0.0)
    
    try:
        # Strip potential markdown blocks if the LLM accidentally adds them
        clean_json = response.strip().strip("```json").strip("```").strip()
        data = json.loads(clean_json)
        return ActionRequest(
            action_type=data.get("action_type", "ALLOCATE").upper(),
            emp_id=data.get("emp_id", "UNKNOWN"),
            project_name=data.get("project_name", "UNKNOWN"),
            allocation_pct=str(data.get("allocation_pct", "100")),
            start_date=data.get("start_date", "TBD"),
            notes=data.get("notes", "")
        )
    except Exception as e:
        # Fallback if parsing fails
        return ActionRequest("ALLOCATE", "UNKNOWN", "UNKNOWN", "100", "TBD", "Failed to parse query.")

def execute_allocation(request: ActionRequest) -> str:
    """
    Safely writes the new allocation row back to the Excel file.
    It reads all sheets, appends to the target sheet, and rewrites the workbook.
    """
    if request.emp_id == "UNKNOWN" or request.project_name == "UNKNOWN":
        return "Error: Could not identify Employee ID or Project Name from your query. Please be more specific."

    try:
        file_path = resolve_file(EXCEL_FILES["resource_allocation"])
        
        # 1. Read all sheets to preserve the entire workbook
        all_sheets = pd.read_excel(file_path, sheet_name=None)
        
        # 2. Find the correct target sheet (using the fuzzy logic from your data_loader)
        target_sheet_name = None
        keywords = ["overall", "project", "res"]
        for sheet_name in all_sheets.keys():
            norm = sheet_name.replace(" ", "").lower()
            if all(k in norm for k in keywords):
                target_sheet_name = sheet_name
                break
                
        if not target_sheet_name:
            return "Error: Could not locate the Master Allocation sheet in the Excel file."

        # 3. Append the new allocation row
        df = all_sheets[target_sheet_name]
        
        new_row = {
            "Employee Code": request.emp_id,
            "Project Name": request.project_name,
            "Allocation %": request.allocation_pct,
            "Start Date": request.start_date,
            "Remarks / Notes": request.notes
        }
        
        # Append using pandas concat
        new_df = pd.DataFrame([new_row])
        df = pd.concat([df, new_df], ignore_index=True)
        all_sheets[target_sheet_name] = df
        
        # 4. Write everything back to the Excel file
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            for sheet_name, sheet_df in all_sheets.items():
                sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
        # 5. Clear Streamlit cache so the next query reads the fresh data!
        st.cache_data.clear()
        
        return f"✅ Successfully allocated Employee **{request.emp_id}** to **{request.project_name}** at {request.allocation_pct}% capacity."

    except Exception as e:
        return f"Failed to execute allocation: {str(e)}"
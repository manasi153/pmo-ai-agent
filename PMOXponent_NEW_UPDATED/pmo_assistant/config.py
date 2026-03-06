
# # LangChain's HF endpoint embeddings read token from HUGGINGFACEHUB_API_KEY
# HUGGINGFACEHUB_API_KEY: str | None = os.getenv("HUGGINGFACEHUB_API_KEY")


from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def project_root() -> Path:
    """
    Resolve the project root directory.

    Assumes this file lives in `pmo_assistant/` under the project root.
    """
    return Path(__file__).resolve().parent.parent


# =========================================================
# PATH CONFIGURATION
# =========================================================

BASE_DIR: Path = project_root()

# ✅ All Excel / Docx / PPT files are inside this folder
DATA_DIR: Path = BASE_DIR / "pmo_data"


def resolve_file(relative_name: str) -> Path:
    """
    Resolve a file inside the pmo_data directory and validate existence.
    """
    path = DATA_DIR / relative_name
    if not path.exists():
        raise FileNotFoundError(f"Expected file not found: {path}")
    return path


# =========================================================
# PMO ARTEFACT FILE DEFINITIONS
# =========================================================

EXCEL_FILES = {
    "talent_pool": "Hackhathon_Pool Details.xlsx",
    "resource_allocation": "Hackhathon_Resource Allocation in Projects.xlsx",
    "resource_utilization": "Hackhathon_Resources Utilization_2025.xlsx",
    "resourcing_enablement": "Hackhathon_Resourcing and Enablement.xlsx",
    "third_party": "Hackhathon_Third Party Employees.xlsx",
    "csat": "CSAT - Customer ID and Name V1.0.xlsx",
    "dashboard_ddit": "Dashboard Data Dictionary - (DDIT).xlsx",
    "rca": "Projects - Root Cause Analysis (RCA) for Projects in RED or AMBER Status.xlsx",
    "project_plan": "Project ID - Project Name - Project Plan_V1.0.xlsx",
    "test_cases": "Test Cases - Project ID -Project Name V1.0.xlsx",
}

DOCX_FILES = {
    "brd_reference": "Reference BRD.docx",
    "tdd_reference": "Reference TDD.docx",
    "mom_template": "MoM - Customer Name-Monthly-Bi Weekly-Weekly-Meeting Title-YYYYMMDD.docx",
    "completion_certificate": "Project_Completion_Certificate.docx",
}

PPTX_FILES = {
    "weekly_status": "Template -Project ID - Project Name  - Weekly Status for Customer Name.pptx",
    "handover": "OppID - Opp Description - Proposal to Delivery Team Handover V1.0.pptx",
}


# =========================================================
# LLM CONFIGURATION
# =========================================================

# GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")

# # Default model; can be overridden via env var
# GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# =========================================================
# LLM CONFIGURATION (Anthropic Claude)
# =========================================================

# =========================================================
# LLM CONFIGURATION (OpenAI)
# =========================================================

HUGGINGFACEHUB_API_KEY: str | None = os.getenv("HUGGINGFACEHUB_API_KEY")

# OPENAI_MODEL: str = os.getenv(
#     "OPENAI_MODEL",
#     "gpt-4o-mini"
# )
# =========================================================
# EMBEDDING CONFIGURATION
# =========================================================

EMBEDDING_MODEL_NAME: str = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "sentence-transformers/all-MiniLM-L6-v2"
)

USE_HF_ENDPOINT_EMBEDDINGS: bool = os.getenv(
    "USE_HF_ENDPOINT_EMBEDDINGS",
    "0"
).strip().lower() in ("1", "true", "yes")

HUGGINGFACEHUB_API_KEY: str | None = os.getenv("HUGGINGFACEHUB_API_KEY")
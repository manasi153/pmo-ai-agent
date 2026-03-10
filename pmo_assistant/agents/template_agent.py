# from __future__ import annotations

# from dataclasses import dataclass
# from typing import Dict, Literal

# from ..data_loader import load_docx_text, load_pptx_text
# from ..llm import get_llm

# TemplateType = Literal[
#     "BRD",
#     "TDD",
#     "MoM",
#     "WeeklyStatus",
#     "CompletionCertificate",
#     "ProjectPlanSummary",
#     "RCA",
#     "CV",  # <-- Added CV type
# ]

# @dataclass
# class TemplateRequest:
#     template_type: TemplateType
#     context: Dict[str, str]

# def _build_system_prompt(template_type: TemplateType, reference_text: str) -> str:
#     return f"""
#     You are PMO Exponent AI Assistant – Enterprise Documentation Engine.

#     ROLE:
#     You are a PMO documentation specialist responsible for generating
#     enterprise-grade project artefacts strictly aligned to official templates.

#     NON-NEGOTIABLE RULES:
#     1. Use ONLY the provided USER INPUT and REFERENCE TEMPLATE.
#     2. DO NOT invent project details, dates, names, metrics, skills, or assumptions.
#     3. If information is missing, insert: [DATA REQUIRED]
#     4. Follow the exact structure and section ordering of the reference template.
#     5. Maintain formal corporate tone suitable for client submission.
#     6. Do NOT add explanations, commentary, or AI notes.
#     7. Do NOT summarize unless explicitly asked.
#     8. Output must be clean, structured, and ready for download.
#     9. Avoid repetition and filler text.
#     10. Ensure consistency across sections.

#     FORMATTING RULES:
#     * Preserve headings and sub-headings from the template.
#     * Maintain the same section ordering as the template.
#     * Keep bullet formatting professional.
#     * Maintain logical section flow.
#     * Do not introduce new sections not present in template.

#     OUTPUT REQUIREMENTS:
#     * Return ONLY the completed {template_type}.
#     * Output must be clear human-readable text.
#     * Do NOT include any system tokens.
#     * Do NOT output tokens such as <|assistant|>, <|user|>, <|system|>, or <|>.
#     * Do NOT include markdown formatting.
#     * Do NOT include explanations or commentary.
#     * The response must start directly with the first section of the template.

#     ## REFERENCE TEMPLATE (Authoritative Structure):

#     ## {reference_text}
#     """

# def generate_document(req: TemplateRequest) -> str:
#     llm = get_llm()

#     if req.template_type == "BRD":
#         reference = load_docx_text("brd_reference")
#     elif req.template_type == "TDD":
#         reference = load_docx_text("tdd_reference")
#     elif req.template_type == "MoM":
#         reference = load_docx_text("mom_template")
#     elif req.template_type == "WeeklyStatus":
#         reference = load_pptx_text("weekly_status")
#     elif req.template_type == "CompletionCertificate":
#         reference = load_docx_text("completion_certificate")
#     elif req.template_type == "ProjectPlanSummary":
#         reference = load_docx_text("brd_reference")
#     elif req.template_type == "RCA":
#         reference = load_docx_text("mom_template")
#     elif req.template_type == "CV":
#         # Hardcoded Exponent Standard CV Template
#         reference = """
#         EXPONENT STANDARD CV
#         ====================
        
#         1. PROFESSIONAL SUMMARY
#         [Provide a concise 3-4 line summary of the candidate's total experience, core competencies, and primary domain expertise based ONLY on the provided text.]

#         2. CORE SKILLS & TECHNOLOGY STACK
#         * Languages / Frameworks: [List]
#         * Tools / Platforms: [List]
#         * Methodologies: [List]

#         3. PROFESSIONAL EXPERIENCE
#         Role: [Job Title]
#         Organization / Client: [Company or Client Name]
#         Duration: [Start Date - End Date]
#         Key Responsibilities:
#         * [Action-oriented bullet point 1]
#         * [Action-oriented bullet point 2]
#         * [Action-oriented bullet point 3]
        
#         [Repeat for older roles if provided]

#         4. EDUCATION & CERTIFICATIONS
#         * [Degree/Certification Name], [Institution], [Year]
#         """
#     else:
#         raise ValueError(f"Unsupported template type: {req.template_type}")

#     system_prompt = _build_system_prompt(req.template_type, reference)

#     qa_lines = []
#     for key, value in req.context.items():
#         qa_lines.append(f"{key}:\n{value}")
#     qa_block = "\n\n".join(qa_lines)

#     user_content = (
#         f"Using the reference above, draft a complete {req.template_type}.\n\n"
#         "USER INPUT / RAW DATA:\n"
#         f"{qa_block}\n\n"
#         "OUTPUT:\n"
#         f"- A single, coherent {req.template_type} in plain text.\n"
#     )

#     return llm.complete(system_prompt=system_prompt, user_content=user_content, temperature=0.2)


from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal

from ..data_loader import load_docx_text, load_pptx_text
from ..llm import get_llm

TemplateType = Literal[
    "BRD",
    "TDD",
    "MoM",
    "WeeklyStatus",
    "CompletionCertificate",
    "ProjectPlanSummary",
    "RCA",
    "CV",
]

@dataclass
class TemplateRequest:
    template_type: TemplateType
    context: Dict[str, str]

def _build_system_prompt(template_type: TemplateType, reference_text: str) -> str:
    return f"""
    You are PMO Exponent AI Assistant – Enterprise Documentation Engine.

    ROLE:
    You are a PMO documentation specialist responsible for generating
    enterprise-grade project artefacts strictly aligned to official templates.

    NON-NEGOTIABLE RULES:
    1. Use ONLY the provided USER INPUT and REFERENCE TEMPLATE.
    2. DO NOT invent project details, dates, names, metrics, skills, or assumptions.
    3. If information is missing, insert: [DATA REQUIRED]
    4. Follow the exact structure and section ordering of the reference template.
    5. Maintain formal corporate tone suitable for client submission.
    6. Do NOT add explanations, commentary, or AI notes.
    7. Do NOT summarize unless explicitly asked.
    8. Output must be clean, structured, and ready for download.
    9. Avoid repetition and filler text.
    10. Ensure consistency across sections.

    FORMATTING RULES:
    * Preserve headings and sub-headings from the template.
    * Maintain the same section ordering as the template.
    * Keep bullet formatting professional.
    * Maintain logical section flow.

    OUTPUT REQUIREMENTS:
    * Return ONLY the completed {template_type}.
    * Output must be clear human-readable text.
    * Do NOT include any system tokens.
    * Do NOT output tokens such as <|assistant|>, <|user|>, <|system|>, or <|>.
    * The response must start directly with the first section of the template.

    ## REFERENCE TEMPLATE (Authoritative Structure):

    ## {reference_text}
    """

def generate_document(req: TemplateRequest) -> str:
    llm = get_llm()

    # 1. Load the corresponding reference file
    if req.template_type == "BRD":
        reference = load_docx_text("brd_reference")
    elif req.template_type == "TDD":
        reference = load_docx_text("tdd_reference")
    elif req.template_type == "MoM":
        reference = load_docx_text("mom_template")
    elif req.template_type == "WeeklyStatus":
        reference = load_pptx_text("weekly_status")
    elif req.template_type == "CompletionCertificate":
        reference = load_docx_text("completion_certificate")
    elif req.template_type == "ProjectPlanSummary":
        reference = load_docx_text("brd_reference")
    elif req.template_type == "RCA":
        reference = load_docx_text("mom_template")
    elif req.template_type == "CV":
        reference = """
        EXPONENT STANDARD CV
        ====================
        
        1. PROFESSIONAL SUMMARY
        [Provide a concise summary based ONLY on the provided text.]

        2. CORE SKILLS & TECHNOLOGY STACK
        * Languages / Frameworks: [List]
        * Tools / Platforms: [List]

        3. PROFESSIONAL EXPERIENCE
        Role: [Job Title]
        Organization: [Company Name]
        Key Responsibilities:
        * [Action bullet]
        
        4. EDUCATION & CERTIFICATIONS
        * [Degree], [Institution], [Year]
        """
    else:
        raise ValueError(f"Unsupported template type: {req.template_type}")

    # ==========================================================
    # FAILSAFE: Truncate large documents to prevent LLM crashes
    # 10,000 chars is roughly 2,500 tokens (well under limits)
    # ==========================================================
    MAX_CHARS = 10000
    if len(reference) > MAX_CHARS:
        reference = reference[:MAX_CHARS] + "\n\n...[TEMPLATE TRUNCATED TO FIT API LIMITS]..."

    system_prompt = _build_system_prompt(req.template_type, reference)

    # 2. Build the Q&A block from the user's input
    qa_lines = []
    for key, value in req.context.items():
        qa_lines.append(f"{key}:\n{value}")
    qa_block = "\n\n".join(qa_lines)

    # 3. Construct the final user prompt
    user_content = (
        f"Using the reference above, draft a complete {req.template_type}.\n\n"
        "USER INPUT / RAW DATA:\n"
        f"{qa_block}\n\n"
        "OUTPUT:\n"
        f"- A single, coherent {req.template_type} in plain text.\n"
    )

    # 4. Execute the LLM call safely
    return llm.complete(system_prompt=system_prompt, user_content=user_content, temperature=0.2)
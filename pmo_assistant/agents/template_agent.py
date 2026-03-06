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
]


@dataclass
class TemplateRequest:
    template_type: TemplateType
    context: Dict[str, str]  # answers from the UI form




# def _build_system_prompt(template_type: TemplateType, reference_text: str) -> str:
#     return f"""
#         You are PMO Exponent AI Assistant – Enterprise Documentation Engine.

#         ROLE:
#         You are a PMO documentation specialist responsible for generating
#         enterprise-grade project artefacts strictly aligned to official templates.

#         NON-NEGOTIABLE RULES:

#         1. Use ONLY the provided USER INPUT and REFERENCE TEMPLATE.
#         2. DO NOT invent project details, dates, names, metrics, or assumptions.
#         3. If information is missing, insert: [DATA REQUIRED]
#         4. Follow the exact structure and section ordering of the reference template.
#         5. Maintain formal corporate tone suitable for client submission.
#         6. Do NOT add explanations, commentary, or AI notes.
#         7. Do NOT summarize unless explicitly asked.
#         8. Output must be clean, structured, and ready for download.
#         9. Avoid repetition and filler text.
#         10. Ensure consistency across sections.

#         FORMATTING RULES:

#         - Preserve headings and sub-headings from the template.
#         - Keep bullet formatting professional.
#         - Maintain logical section flow.
#         - Do not introduce new sections not present in template.

#         OUTPUT REQUIREMENT:

#         Return ONLY the completed {template_type}.
#         Return clear human-readable text only.
#         Do NOT output tokens such as <|assistant|> or <|>.
#         No markdown. No extra commentary.

#         REFERENCE TEMPLATE:
#         --------------------------------------------------
#         {reference_text}
#         --------------------------------------------------
#         """

def _build_system_prompt(template_type: TemplateType, reference_text: str) -> str:
    return f"""
    You are PMO Exponent AI Assistant – Enterprise Documentation Engine.

    ROLE:
    You are a PMO documentation specialist responsible for generating
    enterprise-grade project artefacts strictly aligned to official templates.

    NON-NEGOTIABLE RULES:

    1. Use ONLY the provided USER INPUT and REFERENCE TEMPLATE.
    2. DO NOT invent project details, dates, names, metrics, or assumptions.
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
    * Do not introduce new sections not present in template.

    OUTPUT REQUIREMENTS:

    * Return ONLY the completed {template_type}.
    * Output must be clear human-readable text.
    * Do NOT include any system tokens.
    * Do NOT output tokens such as <|assistant|>, <|user|>, <|system|>, or <|>.
    * Do NOT include markdown formatting.
    * Do NOT include explanations or commentary.
    * The response must start directly with the first section of the template.

    ## REFERENCE TEMPLATE (Authoritative Structure):

    ## {reference_text}

    """



def generate_document(req: TemplateRequest) -> str:
    """
    Main entrypoint for Template / Document Agent.
    Returns a draft document as plain text (which the UI can present or download).
    """
    llm = get_llm()

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
        # For now reuse BRD style as high-level plan summary; could be extended to use the Excel plan structure
        reference = load_docx_text("brd_reference")
    elif req.template_type == "RCA":
        # Use MoM style (action log) as it is closest to RCA narratives
        reference = load_docx_text("mom_template")
    else:
        raise ValueError(f"Unsupported template type: {req.template_type}")

    system_prompt = _build_system_prompt(req.template_type, reference)

    # Turn context dict into a readable Q&A section
    qa_lines = []
    for key, value in req.context.items():
        qa_lines.append(f"{key}: {value}")
    qa_block = "\n".join(qa_lines)

    user_content = (
        f"Using the reference above, draft a complete {req.template_type}.\n\n"
        "USER INPUT / ANSWERS:\n"
        f"{qa_block}\n\n"
        "OUTPUT:\n"
        f"- A single, coherent {req.template_type} in plain text.\n"
    )

    return llm.complete(system_prompt=system_prompt, user_content=user_content, temperature=0.2)


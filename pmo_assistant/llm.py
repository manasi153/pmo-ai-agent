


# from __future__ import annotations

# import os
# from typing import Optional
# from huggingface_hub import InferenceClient
# from .config import HUGGINGFACEHUB_API_KEY

# HF_MODEL = os.getenv(
#     "HF_MODEL",
#     "mistralai/Mistral-7B-Instruct-v0.2"
# )


# class LLMClient:

#     def __init__(self, model: Optional[str] = None):

#         if not HUGGINGFACEHUB_API_KEY:
#             raise RuntimeError("HUGGINGFACEHUB_API_KEY not set in .env")

#         self.model = model or HF_MODEL
#         self.client = InferenceClient(
#             model=self.model,
#             token=HUGGINGFACEHUB_API_KEY
#         )

  
    

#     def complete(
#         self,
#         system_prompt: str,
#         user_content: str,
#         temperature: float = 0.2,
#         max_tokens: int = 600,
#         ) -> str:

#         prompt = f"""
#         {system_prompt}

#         User:
#         {user_content}

#         Assistant:
#         """

#         response = self.client.text_generation(
#             prompt,
#             max_new_tokens=max_tokens,
#             temperature=temperature,
#             do_sample=True,
#         )

#         return response.strip()





# _GLOBAL_LLM: Optional[LLMClient] = None


# def get_llm() -> LLMClient:
#     global _GLOBAL_LLM
#     if _GLOBAL_LLM is None:
#         _GLOBAL_LLM = LLMClient()
#     return _GLOBAL_LLM


import os
from typing import Optional
from groq import Groq
from .config import GROQ_API_KEY, GROQ_MODEL

class LLMClient:
    def __init__(self):
        if not GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY not set in .env")
            
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL

    def complete(
        self,
        system_prompt: str,
        user_content: str,
        temperature: float = 0.2,
        max_tokens: int = 500
    ) -> str:

        response = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content
    
_GLOBAL_LLM: Optional[LLMClient] = None


def get_llm() -> LLMClient:
    global _GLOBAL_LLM
    if _GLOBAL_LLM is None:
        _GLOBAL_LLM = LLMClient()
    return _GLOBAL_LLM

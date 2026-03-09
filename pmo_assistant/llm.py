# # from __future__ import annotations

# # import os
# # from typing import Optional
# # from openai import OpenAI

# # from .config import OPENAI_API_KEY, OPENAI_MODEL


# # class LLMClient:

# #     def __init__(self, model: Optional[str] = None):
# #         if not OPENAI_API_KEY:
# #             raise RuntimeError(
# #                 "OPENAI_API_KEY not set in .env"
# #             )

# #         self.client = OpenAI(api_key=OPENAI_API_KEY)
# #         self.model = model or OPENAI_MODEL

# #     def complete(
# #         self,
# #         system_prompt: str,
# #         user_content: str,
# #         temperature: float = 0.2,
# #         max_tokens: int = 1500,
# #     ) -> str:

# #         response = self.client.chat.completions.create(
# #             model=self.model,
# #             temperature=temperature,
# #             max_tokens=max_tokens,
# #             messages=[
# #                 {"role": "system", "content": system_prompt},
# #                 {"role": "user", "content": user_content},
# #             ],
# #         )

# #         return response.choices[0].message.content


# # _GLOBAL_LLM: Optional[LLMClient] = None


# # def get_llm() -> LLMClient:
# #     global _GLOBAL_LLM
# #     if _GLOBAL_LLM is None:
# #         _GLOBAL_LLM = LLMClient()
# #     return _GLOBAL_LLM


# from __future__ import annotations

# import os
# from typing import Optional
# from huggingface_hub import InferenceClient
# from .config import HUGGINGFACEHUB_API_KEY

# HF_MODEL = os.getenv(
#     "HF_MODEL",
#     "HuggingFaceH4/zephyr-7b-beta"   # Recommended for free HF inference
# )


# class LLMClient:

#     def __init__(self, model: Optional[str] = None):

#         if not HUGGINGFACEHUB_API_KEY:
#             raise RuntimeError(
#                 "HUGGINGFACEHUB_API_KEY not set in .env"
#             )

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
#         max_tokens: int = 1024,
#     ) -> str:

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


from __future__ import annotations

import os
from typing import Optional
from huggingface_hub import InferenceClient
from .config import HUGGINGFACEHUB_API_KEY

HF_MODEL = os.getenv(
    "HF_MODEL",
    "mistralai/Mistral-7B-Instruct-v0.2"
)


class LLMClient:

    def __init__(self, model: Optional[str] = None):

        if not HUGGINGFACEHUB_API_KEY:
            raise RuntimeError("HUGGINGFACEHUB_API_KEY not set in .env")

        self.model = model or HF_MODEL
        self.client = InferenceClient(
            model=self.model,
            token=HUGGINGFACEHUB_API_KEY
        )

  
    # def complete(
    #     self,
    #     system_prompt: str,
    #     user_content: str,
    #     temperature: float = 0.2,
    #     max_tokens: int = 2048,
    #     ) -> str:

    #     # 🔥 Manual formatting for Zephyr/Mistral-style models
    #     formatted_prompt = f"""
    #         <|system|>
    #         {system_prompt}
    #         <|user|>
    #         {user_content}
    #         <|assistant|>
    #         """

    #     response = self.client.chat.completions.create(
    #         model="HuggingFaceH4/zephyr-7b-beta",
    #         messages=[{"role": "user", "content": formatted_prompt}],
    #         temperature=temperature,
    #         max_tokens=max_tokens,
    #     )

    #     return response.choices[0].message.content.strip()



    # def complete(
    #     self,
    #     system_prompt: str,
    #     user_content: str,
    #     temperature: float = 0.2,
    #     max_tokens: int = 600,
    # ) -> str:

    #     response = self.client.chat.completions.create(
    #         model="HuggingFaceH4/zephyr-7b-beta",
    #         messages=[
    #             {"role": "system", "content": system_prompt},
    #             {"role": "user", "content": user_content},
    #         ],
    #         temperature=temperature,
    #         max_tokens=max_tokens,
    #     )

    #     text = response.choices[0].message.content

    #     # Clean tokens
    #     if text:
    #         text = text.replace("<|assistant|>", "")
    #         text = text.replace("<|>", "")
    #         text = text.strip()

    #     return text

    # def complete(
    #     self,
    #     system_prompt: str,
    #     user_content: str,
    #     temperature: float = 0.2,
    #     max_tokens: int = 600,
    # ) -> str:

    #     response = self.client.chat.completions.create(
    #         model="HuggingFaceH4/zephyr-7b-beta",
    #         messages=[
    #             {
    #                 "role": "system",
    #                 "content": system_prompt,
    #             },
    #             {
    #                 "role": "user",
    #                 "content": user_content,
    #             },
    #         ],
    #         temperature=temperature,
    #         max_tokens=max_tokens,
    #         # stop=["</s>"]
    #     )

    #     text = response.choices[0].message.content

    #     if text:
    #         text = text.replace("<|assistant|>", "").strip()

    #     return text

    def complete(
        self,
        system_prompt: str,
        user_content: str,
        temperature: float = 0.2,
        max_tokens: int = 600,
        ) -> str:

        prompt = f"""
        {system_prompt}

        User:
        {user_content}

        Assistant:
        """

        response = self.client.text_generation(
            prompt,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
        )

        return response.strip()





_GLOBAL_LLM: Optional[LLMClient] = None


def get_llm() -> LLMClient:
    global _GLOBAL_LLM
    if _GLOBAL_LLM is None:
        _GLOBAL_LLM = LLMClient()
    return _GLOBAL_LLM
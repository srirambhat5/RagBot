from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import RetrievalQA
from langchain_core.language_models.llms import LLM

from google import genai
from google.genai import types

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class GeminiLLM(LLM):

    @property
    def _llm_type(self):
        return "gemini"

    def _call(self, prompt, stop=None, run_manager=None, **kwargs):

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text


def get_llm_chain(retriever):

    llm = GeminiLLM()

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are **MediBot**, an AI-powered assistant trained to help users understand medical documents and health-related questions.

Your job is to provide clear, accurate, and helpful responses based **only on the provided context**.

---

🔍 **Context**:
{context}

🙋‍♂️ **User Question**:
{question}

---

💬 **Answer**:
- Respond in a calm, factual, and respectful tone.
- Use simple explanations when needed.
- If the context does not contain the answer, say: "I'm sorry, but I couldn't find relevant information in the provided documents."
- Do NOT make up facts.
- Do NOT give medical advice or diagnoses.
"""
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )
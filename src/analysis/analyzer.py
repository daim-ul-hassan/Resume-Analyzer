from __future__ import annotations

import json
import os
import re
from typing import Literal

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.analysis.fallback import run_fallback_analysis
from src.models.schemas import ResumeAnalysisResult
from src.services.prompts import ANALYSIS_PROMPT

load_dotenv()

ProviderName = Literal["Auto", "Gemini", "Groq"]

RETRIEVAL_QUERY = (
    "Find the strongest evidence in this resume about measurable impact, technical skills, "
    "leadership, clarity, structure, wording quality, grammar quality, and missing details."
)


def _normalize_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _extract_json_block(raw_text: str) -> dict:
    cleaned = raw_text.strip()
    cleaned = cleaned.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise ValueError("The model response did not contain valid JSON.")
        return json.loads(match.group(0))


def _chunk_resume_text(resume_text: str) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=180)
    documents = splitter.create_documents([resume_text], metadatas=[{"source": "resume"}])

    for index, document in enumerate(documents, start=1):
        document.metadata["chunk"] = index

    return documents


def _keyword_retrieve(documents: list[Document], query: str, k: int = 5) -> list[Document]:
    query_terms = set(re.findall(r"[a-zA-Z]{4,}", query.lower()))
    scored_docs: list[tuple[int, Document]] = []

    for document in documents:
        lower_text = document.page_content.lower()
        score = sum(term in lower_text for term in query_terms)
        score += min(4, len(re.findall(r"\b\d+%|\b\d+\+|\$\d+", document.page_content)))
        scored_docs.append((score, document))

    ranked = [doc for score, doc in sorted(scored_docs, key=lambda item: item[0], reverse=True) if score > 0]
    return ranked[:k] if ranked else documents[:k]


def _semantic_retrieve(documents: list[Document], query: str, gemini_api_key: str) -> list[Document]:
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=gemini_api_key,
    )
    vector_store = InMemoryVectorStore(embedding=embeddings)
    vector_store.add_documents(documents)
    return vector_store.similarity_search(query, k=min(5, len(documents)))


def _format_context(documents: list[Document]) -> str:
    chunks: list[str] = []
    for document in documents:
        chunk_id = document.metadata.get("chunk", "?")
        chunks.append(f"[Chunk {chunk_id}]\n{document.page_content.strip()}")
    return "\n\n".join(chunks)


def _resolve_provider(
    preferred_provider: ProviderName,
    gemini_api_key: str,
    groq_api_key: str,
) -> str | None:
    if preferred_provider == "Gemini":
        return "Gemini" if gemini_api_key else None

    if preferred_provider == "Groq":
        return "Groq" if groq_api_key else None

    if gemini_api_key:
        return "Gemini"

    if groq_api_key:
        return "Groq"

    return None


def _build_llm(provider: str, gemini_api_key: str, groq_api_key: str):
    if provider == "Gemini":
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=gemini_api_key,
            temperature=0.2,
        )

    if provider == "Groq":
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=groq_api_key,
            temperature=0.2,
        )

    raise ValueError("Unsupported provider selected.")


def _build_rag_result(
    raw_text: str,
    resume_text: str,
    provider: str,
    retrieval_mode: str,
    retrieved_documents: list[Document],
) -> ResumeAnalysisResult:
    payload = _extract_json_block(raw_text)

    return ResumeAnalysisResult(
        score=max(0, min(100, int(payload.get("score", 0)))),
        summary=str(payload.get("summary", "")).strip(),
        strengths=_normalize_list(payload.get("strengths"))[:5],
        weaknesses=_normalize_list(payload.get("weaknesses"))[:5],
        suggestions=_normalize_list(payload.get("suggestions"))[:5],
        extracted_text=resume_text,
        analysis_mode="LangChain RAG",
        provider=provider,
        retrieval_mode=retrieval_mode,
        retrieved_context=[doc.page_content.strip() for doc in retrieved_documents],
    )


def analyze_resume(
    resume_text: str,
    candidate_name: str = "",
    preferred_provider: ProviderName = "Auto",
    gemini_api_key: str | None = None,
    groq_api_key: str | None = None,
) -> ResumeAnalysisResult:
    if not resume_text.strip():
        raise ValueError("No resume text found in the uploaded file.")

    resolved_gemini_key = (gemini_api_key or os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")).strip()
    resolved_groq_key = (groq_api_key or os.getenv("GROQ_API_KEY", "")).strip()

    provider = _resolve_provider(preferred_provider, resolved_gemini_key, resolved_groq_key)
    if not provider:
        return run_fallback_analysis(resume_text)

    documents = _chunk_resume_text(resume_text)

    try:
        if resolved_gemini_key:
            retrieved_documents = _semantic_retrieve(documents, RETRIEVAL_QUERY, resolved_gemini_key)
            retrieval_mode = "Semantic RAG"
        else:
            retrieved_documents = _keyword_retrieve(documents, RETRIEVAL_QUERY)
            retrieval_mode = "Keyword RAG"

        context = _format_context(retrieved_documents)
        llm = _build_llm(provider, resolved_gemini_key, resolved_groq_key)

        response = llm.invoke(
            [
                SystemMessage(content="You review resumes carefully and return only valid JSON."),
                HumanMessage(
                    content=ANALYSIS_PROMPT.format(
                        candidate_name=candidate_name.strip() or "Candidate",
                        retrieved_context=context,
                    )
                ),
            ]
        )

        return _build_rag_result(
            raw_text=str(response.content),
            resume_text=resume_text,
            provider=provider,
            retrieval_mode=retrieval_mode,
            retrieved_documents=retrieved_documents,
        )
    except Exception:
        return run_fallback_analysis(resume_text)

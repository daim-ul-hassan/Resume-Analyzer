from __future__ import annotations

import re

from src.models.schemas import ResumeAnalysisResult


POSITIVE_KEYWORDS = {
    "python",
    "streamlit",
    "sql",
    "machine learning",
    "leadership",
    "project",
    "developed",
    "built",
    "improved",
    "managed",
    "analyzed",
    "api",
    "github",
    "team",
    "results",
}

WEAK_VERBS = {"worked", "helped", "did", "made", "tasked"}


def _has_contact_info(text: str) -> bool:
    email_pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    phone_pattern = r"(\+?\d[\d\s\-()]{7,}\d)"
    return bool(re.search(email_pattern, text) or re.search(phone_pattern, text))


def _has_metrics(text: str) -> bool:
    return bool(re.search(r"\b\d+%|\b\d+\+|\$\d+|\b\d+\s*(years|months|users|projects)", text, re.IGNORECASE))


def run_fallback_analysis(resume_text: str) -> ResumeAnalysisResult:
    text = " ".join(resume_text.split())
    lower_text = text.lower()
    word_count = len(text.split())

    score = 45
    strengths: list[str] = []
    weaknesses: list[str] = []
    suggestions: list[str] = []

    keyword_hits = sum(1 for keyword in POSITIVE_KEYWORDS if keyword in lower_text)
    weak_verb_hits = sum(1 for keyword in WEAK_VERBS if f" {keyword} " in f" {lower_text} ")

    if word_count > 150:
        score += 10
        strengths.append("The resume has enough content to evaluate experience and skills.")
    else:
        weaknesses.append("The resume content is too brief and may not give recruiters enough detail.")

    if _has_contact_info(text):
        score += 10
        strengths.append("Contact information appears to be included.")
    else:
        weaknesses.append("Important contact information is missing or unclear.")

    if _has_metrics(text):
        score += 15
        strengths.append("The resume includes measurable impact, which improves credibility.")
    else:
        weaknesses.append("Achievements are not strongly supported by measurable results.")

    if keyword_hits >= 5:
        score += 15
        strengths.append("Relevant technical and professional keywords are present.")
    elif keyword_hits >= 2:
        score += 8
        strengths.append("Some useful role-related keywords are present.")
    else:
        weaknesses.append("The resume could use more role-specific keywords and tools.")

    if weak_verb_hits >= 3:
        score -= 8
        weaknesses.append("Several bullet points use weak action verbs.")

    if len(re.findall(r"[.!?]{2,}", text)) > 0:
        score -= 5
        weaknesses.append("There are signs of punctuation issues that affect readability.")

    if score >= 70:
        suggestions.append("Keep the current structure but tighten a few bullet points for stronger impact.")
    else:
        suggestions.append("Rewrite experience bullets with stronger action verbs and clearer outcomes.")

    suggestions.append("Add numbers, percentages, or business impact wherever possible.")
    suggestions.append("Use clean section titles and concise bullet points for easier scanning.")

    if not strengths:
        strengths.append("The resume provides a starting base that can be improved with stronger structure.")

    if not weaknesses:
        weaknesses.append("Only minor improvements are needed in clarity, wording, and positioning.")

    score = max(0, min(100, score))

    return ResumeAnalysisResult(
        score=score,
        strengths=strengths[:4],
        weaknesses=weaknesses[:4],
        suggestions=suggestions[:4],
        summary="A local heuristic review was used because no compatible live model provider was available.",
        extracted_text=resume_text,
        analysis_mode="Fallback",
        provider="Local",
        retrieval_mode="Keyword Heuristic",
        retrieved_context=[],
    )

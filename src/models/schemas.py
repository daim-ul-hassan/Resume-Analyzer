from dataclasses import dataclass, field


@dataclass
class ResumeAnalysisResult:
    score: int
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    summary: str = ""
    extracted_text: str = ""
    analysis_mode: str = "Fallback"
    provider: str = "Local"
    retrieval_mode: str = "Heuristic"
    retrieved_context: list[str] = field(default_factory=list)

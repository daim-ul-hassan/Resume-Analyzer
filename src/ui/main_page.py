from __future__ import annotations

import html

import streamlit as st

from src.analysis.analyzer import analyze_resume
from src.services.file_parser import extract_text


def _apply_page_style() -> None:
    st.set_page_config(page_title="AI Resume Analyzer", page_icon="AI", layout="wide")
    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top right, rgba(54, 208, 255, 0.14), transparent 26%),
                    radial-gradient(circle at left center, rgba(142, 88, 255, 0.12), transparent 24%),
                    linear-gradient(180deg, #020202 0%, #050505 55%, #020202 100%);
                color: #ffffff;
            }
            [data-testid="stSidebar"] {
                background:
                    linear-gradient(180deg, rgba(10, 10, 10, 0.98), rgba(6, 6, 6, 0.98));
                border-right: 1px solid rgba(255, 255, 255, 0.08);
            }
            [data-testid="stSidebar"] * {
                color: #ffffff !important;
            }
            .block-container {
                max-width: 1200px;
                padding-top: 1.5rem;
                padding-bottom: 3rem;
            }
            .hero-shell {
                position: relative;
                overflow: hidden;
                border-radius: 28px;
                padding: 1.6rem;
                margin-bottom: 1rem;
                background:
                    linear-gradient(135deg, rgba(12, 12, 14, 0.92), rgba(8, 8, 10, 0.88));
                border: 1px solid rgba(114, 235, 255, 0.16);
                box-shadow:
                    0 0 0 1px rgba(255, 255, 255, 0.02) inset,
                    0 20px 50px rgba(0, 0, 0, 0.42);
            }
            .hero-shell::after {
                content: "";
                position: absolute;
                top: -20%;
                right: -10%;
                width: 240px;
                height: 240px;
                background: radial-gradient(circle, rgba(93, 225, 255, 0.18), transparent 65%);
                pointer-events: none;
            }
            .panel-card, .result-card, .mini-card {
                background: rgba(10, 10, 12, 0.88);
                border: 1px solid rgba(255, 255, 255, 0.09);
                border-radius: 22px;
                padding: 1.15rem;
                box-shadow: 0 16px 40px rgba(0, 0, 0, 0.28);
            }
            .panel-card, .result-card {
                margin-bottom: 1rem;
            }
            .eyebrow {
                text-transform: uppercase;
                letter-spacing: 0.18em;
                font-size: 0.74rem;
                color: #8de8ff;
                margin-bottom: 0.5rem;
            }
            .hero-title {
                font-size: 2.5rem;
                line-height: 1.05;
                font-weight: 800;
                margin: 0 0 0.55rem 0;
                color: #ffffff;
            }
            .hero-copy, .muted-text {
                color: #d9d9df;
            }
            .section-title {
                color: #ffffff;
                font-size: 1.05rem;
                font-weight: 700;
                margin-bottom: 0.45rem;
            }
            .metric-row {
                display: flex;
                gap: 0.65rem;
                flex-wrap: wrap;
                margin-top: 1rem;
            }
            .metric-pill {
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                padding: 0.52rem 0.8rem;
                border-radius: 999px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                background: rgba(255, 255, 255, 0.03);
                color: #ffffff;
                font-size: 0.92rem;
            }
            .score-orb {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 118px;
                height: 118px;
                border-radius: 999px;
                background:
                    radial-gradient(circle at 30% 30%, rgba(138, 246, 255, 0.28), rgba(17, 17, 19, 0.92) 60%),
                    #0c0c0e;
                border: 1px solid rgba(141, 232, 255, 0.26);
                box-shadow: 0 0 50px rgba(79, 225, 255, 0.12);
                color: #ffffff;
                font-weight: 800;
                font-size: 1.8rem;
            }
            .score-caption {
                margin-top: 0.6rem;
                color: #bcbcc5;
                font-size: 0.88rem;
            }
            .step-title {
                color: #ffffff;
                font-weight: 700;
                margin-bottom: 0.2rem;
            }
            .step-copy {
                color: #cfd1d8;
                font-size: 0.93rem;
            }
            .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
                background: #0b0b0d !important;
                color: #ffffff !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
            }
            .stButton > button {
                background: linear-gradient(90deg, #9df3ff, #ffffff);
                color: #000000;
                border-radius: 14px;
                border: none;
                font-weight: 800;
                min-height: 3rem;
                box-shadow: 0 10px 30px rgba(108, 236, 255, 0.2);
            }
            .stFileUploader section {
                background: rgba(255, 255, 255, 0.02);
                border: 1px dashed rgba(145, 233, 255, 0.3);
                border-radius: 18px;
            }
            .stProgress > div > div {
                background: linear-gradient(90deg, #8ef0ff, #6d8dff);
            }
            .stAlert, .stInfo, .stSuccess, .stWarning, .stError, .stMarkdown, label, p, li, h1, h2, h3, h4, h5, h6, span {
                color: #ffffff !important;
            }
            a {
                color: #9befff !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_list(items: list[str], empty_text: str) -> None:
    if items:
        for item in items:
            st.markdown(f"- {item}")
    else:
        st.markdown(f"- {empty_text}")


def _render_top_section(user_name: str) -> None:
    greeting_name = user_name.strip() if user_name else ""
    greeting_text = f"Welcome back, {html.escape(greeting_name)}." if greeting_name else "Welcome to your AI hiring cockpit."

    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="eyebrow">Future-Ready Resume Intelligence</div>
            <div class="hero-title">{greeting_text}<br/>AI Resume Analyzer</div>
            <p class="hero-copy">
                Upload a PDF or TXT resume, let the app split it into knowledge chunks, retrieve the most relevant evidence,
                and generate a structured review with score, strengths, weaknesses, and sharper suggestions for impact,
                wording, grammar, and clarity.
            </p>
            <div class="metric-row">
                <div class="metric-pill">RAG workflow</div>
                <div class="metric-pill">Gemini + Groq ready</div>
                <div class="metric-pill">PDF and TXT support</div>
                <div class="metric-pill">Structured feedback output</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    steps = st.columns(3, gap="large")
    step_data = [
        ("01", "Upload Resume", "Drop in a PDF or TXT resume so the app can extract the text cleanly."),
        ("02", "Retrieve Evidence", "LangChain splits the resume into chunks and pulls the most relevant evidence first."),
        ("03", "Review with AI", "Gemini or Groq produces a focused evaluation based on retrieved resume context."),
    ]

    for column, (index, title, copy) in zip(steps, step_data):
        with column:
            st.markdown(
                f"""
                <div class="mini-card">
                    <div class="eyebrow">{index}</div>
                    <div class="step-title">{title}</div>
                    <div class="step-copy">{copy}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_app() -> None:
    _apply_page_style()

    with st.sidebar:
        st.markdown("## Mission Control")
        st.caption("Set your identity, choose a provider path, and connect the API keys you want to use.")

        user_name = st.text_input(
            "Your Name",
            placeholder="Enter your name",
            help="Used for the greeting and the review prompt.",
        )
        preferred_provider = st.selectbox(
            "Preferred AI Provider",
            options=["Auto", "Gemini", "Groq"],
            help="Auto prefers Gemini when available, otherwise Groq.",
        )
        gemini_api_key = st.text_input(
            "Gemini API Key",
            type="password",
            help="Used for Gemini analysis and for semantic embeddings when available.",
        )
        st.markdown("[Get a Gemini API key](https://ai.google.dev/gemini-api/docs/api-key)")

        groq_api_key = st.text_input(
            "Groq API Key",
            type="password",
            help="Used when Groq is selected or when Auto falls back to Groq.",
        )
        st.markdown("[Get a Groq API key](https://console.groq.com/keys)")

        st.caption(
            "If only a Groq key is available, the app still runs RAG using LangChain chunking with keyword retrieval."
        )

    _render_top_section(user_name)

    left, right = st.columns([1.25, 0.75], gap="large")

    with left:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Upload Resume</div>
                <div class="muted-text">Supported formats: PDF and TXT. The app will extract text, retrieve high-signal chunks, and then review the resume.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader("Resume File", type=["pdf", "txt"], label_visibility="collapsed")

    with right:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Live Stack</div>
                <div class="muted-text">LangChain chunking and retrieval are used before model analysis to keep the review grounded in resume evidence.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if uploaded_file is None:
        st.info("Upload a resume to start the retrieval and review flow.")
        return

    st.markdown(
        f"""
        <div class="panel-card">
            <div class="section-title">Loaded File</div>
            <div class="muted-text">{html.escape(uploaded_file.name)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Launch Analysis", type="primary", use_container_width=True):
        with st.spinner("Building the retrieval context and reviewing the resume..."):
            try:
                file_bytes = uploaded_file.getvalue()
                extracted_text = extract_text(uploaded_file.name, file_bytes)
                result = analyze_resume(
                    resume_text=extracted_text,
                    candidate_name=user_name,
                    preferred_provider=preferred_provider,
                    gemini_api_key=gemini_api_key,
                    groq_api_key=groq_api_key,
                )
            except Exception as exc:
                st.error(f"Unable to analyze the file: {exc}")
                return

        summary_col, meta_col = st.columns([0.72, 0.28], gap="large")

        with summary_col:
            st.markdown(
                f"""
                <div class="result-card">
                    <div class="eyebrow">Executive Summary</div>
                    <div class="section-title">Resume Snapshot</div>
                    <div class="muted-text">{html.escape(result.summary or "Your resume analysis is ready.")}</div>
                    <div class="metric-row">
                        <div class="metric-pill">Provider: {html.escape(result.provider)}</div>
                        <div class="metric-pill">Mode: {html.escape(result.analysis_mode)}</div>
                        <div class="metric-pill">Retrieval: {html.escape(result.retrieval_mode)}</div>
                        <div class="metric-pill">Chunks used: {len(result.retrieved_context)}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with meta_col:
            st.markdown(
                f"""
                <div class="result-card" style="text-align:center;">
                    <div class="score-orb">{result.score}</div>
                    <div class="score-caption">Resume Score / 100</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.progress(result.score / 100)

        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Strengths</div>', unsafe_allow_html=True)
            _render_list(result.strengths, "No major strengths were detected.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Weaknesses</div>', unsafe_allow_html=True)
            _render_list(result.weaknesses, "No major weaknesses were detected.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Suggestions</div>', unsafe_allow_html=True)
        _render_list(result.suggestions, "No suggestions available.")
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("Retrieved RAG Context"):
            if result.retrieved_context:
                for index, chunk in enumerate(result.retrieved_context, start=1):
                    st.markdown(f"**Chunk {index}**")
                    st.write(chunk)
            else:
                st.write("No external chunks were retrieved for this run.")

        with st.expander("Extracted Resume Text"):
            st.text_area("Extracted Resume Text", value=result.extracted_text, height=260)

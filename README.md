# AI Resume Analyzer

A simple Streamlit app that accepts resumes in PDF and TXT format, extracts the text, and returns a structured resume review with:

- Score out of 100
- Resume strengths
- Resume weaknesses
- Suggestions for wording, grammar, and overall improvement

## Tech Stack

- Python
- Streamlit
- pypdf
- LangChain
- Gemini API
- Groq API
- python-dotenv

## Project Structure

```text
Resume/
|-- app.py
|-- streamlit_app.py
|-- requirements.txt
|-- .gitignore
|-- README.md
|-- .streamlit/
|   `-- config.toml
`-- src/
    |-- analysis/
    |   |-- analyzer.py
    |   `-- fallback.py
    |-- models/
    |   `-- schemas.py
    |-- services/
    |   |-- file_parser.py
    |   `-- prompts.py
    `-- ui/
        `-- main_page.py
```

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add keys in `.env` if you want local defaults:
   `GEMINI_API_KEY=your_key_here`
   `GROQ_API_KEY=your_key_here`
You can also enter both keys directly inside the app sidebar.
4. Run the app:

```bash
streamlit run app.py
```

You can also run the Streamlit-friendly entry file:

```bash
streamlit run streamlit_app.py
```

## Notes

- The app supports both PDF and TXT resume uploads.
- LangChain is used for chunking and retrieval before the final resume review.
- Gemini can be used for both embeddings and final analysis.
- Groq can be used for final analysis, and the app falls back to keyword retrieval when only a Groq key is available.
- If no API key is provided, the app falls back to a local rule-based analyzer so you can still test the interface and upload flow.
- After local testing, this folder is ready to push to GitHub and deploy with Streamlit.

## Streamlit Deployment

For Streamlit Community Cloud:

1. Connect the GitHub repository.
2. Set the main file path to `streamlit_app.py` or `app.py`.
3. Add secrets in the Streamlit app settings if needed:
   - `GEMINI_API_KEY`
   - `GROQ_API_KEY`
4. Deploy.

The repo already includes:

- `requirements.txt` at the root
- a root Streamlit entry file
- `.streamlit/config.toml` for theme and app defaults

## Troubleshooting

If `pip install -r requirements.txt` says `No matching distribution found` for common packages such as `streamlit`, check whether your shell has `PIP_NO_INDEX=1` set.

In PowerShell, clear it for the current session with:

```powershell
Remove-Item Env:PIP_NO_INDEX -ErrorAction SilentlyContinue
```

Then run:

```powershell
pip install -r requirements.txt
```

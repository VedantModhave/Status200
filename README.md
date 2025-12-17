## EY Techathon 6.0 – Pharma Agentic AI (PS1)

This repository contains a demo implementation of an Agentic AI system for a multinational generic pharma company, built for **EY Techathon 6.0** (Pharma domain, PS1).

### Tech stack

- **Backend / Agents**: Python, LangGraph (planned), lightweight orchestration in `app/graph.py`
- **UI**: Streamlit (`app/main.py`)
- **Core idea**: Master Agent + Worker Agents (IQVIA, EXIM, Clinical Trials, Patents, Internal Docs, Web Intelligence, Report Generator)

### Quick start

1. Create and activate virtual environment (Windows PowerShell):

```powershell
cd "C:\Users\modha\OneDrive\Desktop\EY Pharma"
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the Streamlit UI:

```powershell
streamlit run app/main.py
```

3. Open the URL shown in the terminal (usually `http://localhost:8501`) to use the chat demo.

### Current status

- Streamlit UI is wired to a **temporary Python orchestration** in `app/graph.py`.
- Agent modules (`app/agents/*`) currently return **placeholder summaries** only.
- Next steps:
  - Replace `run_demo_workflow` with a proper LangGraph graph.
  - Add realistic mock CSV/JSON data for IQVIA, EXIM, patents, clinical trials, etc.
  - Implement PDF Report Generator Agent.



## EY Techathon 6.0 – Pharma Agentic AI (PS1)

**Complete Agentic AI solution** for accelerating pharma innovation opportunity identification. Built for **EY Techathon 6.0** (Pharma domain, PS1).

### 🎯 Key Features

- ✅ **Master Agent** with query-aware orchestration and strategic signal detection
- ✅ **7 Worker Agents** (IQVIA, EXIM, Patents, Clinical Trials, Internal, Web, Report)
- ✅ **Dynamic Charts & Tables** generated from mock data
- ✅ **PDF Report Generation** with all visualizations
- ✅ **Clarification Handling** for vague queries
- ✅ **Follow-up Query Support** ("Also check for biosimilar competition")
- ✅ **Entity Extraction** from natural language queries
- ✅ **File Upload** for internal document analysis

### 🛠️ Tech Stack

- **Framework:** LangGraph (Agent Orchestration)
- **UI:** Streamlit (Web Interface)
- **Data:** Pandas, JSON (Mock APIs)
- **Visualization:** Matplotlib (Charts)
- **PDF:** ReportLab (Report Generation)
- **PDF Processing:** PyPDF2 (Document Analysis)

### 🚀 Quick Start

1. **Create and activate virtual environment** (Windows PowerShell):

```powershell
cd "C:\Users\modha\OneDrive\Desktop\EY Pharma"
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

2. **Run the Streamlit UI:**

```powershell
streamlit run app/main.py
```

3. **Open** `http://localhost:8501` in your browser

### 📁 Project Structure

```
EY Pharma/
├── app/
│   ├── main.py              # Streamlit UI
│   ├── graph.py             # LangGraph workflow
│   └── agents/
│       ├── master.py        # Master Agent (orchestrator)
│       ├── workers.py        # 6 Worker Agents
│       ├── report.py         # PDF Report Generator
│       └── state.py          # State models
├── data/                     # Mock data files
│   ├── iqvia_markets.csv
│   ├── exim_trade.csv
│   ├── patents.json
│   ├── clinical_trials.csv
│   ├── web_results.json
│   └── example_queries.csv
├── reports/                  # Generated PDF reports
├── ARCHITECTURE.md          # System architecture documentation
├── BRIEF_DOCUMENT.md        # Submission brief document
└── requirements.txt         # Python dependencies
```

### 💡 Example Queries

- "Find innovation opportunities for tiotropium in India over 5 years"
- "Show market trends and patent landscape"
- "Also check for biosimilar competition" (follow-up)
- "Where is the unmet need in oncology?" (triggers clarification)

### 📊 Strategic Signals

The system automatically detects:
- **🔍 Whitespace:** High market size + Low trial activity
- **💡 Opportunity:** Patent expiry within 2 years → Biosimilar window

### 📚 Documentation

- **ARCHITECTURE.md**: Complete system architecture and agent workflows
- **BRIEF_DOCUMENT.md**: Submission brief with all requirements covered

### ✅ Status: Production-Ready Demo

- ✅ All 7 agents implemented and working
- ✅ LangGraph orchestration functional
- ✅ Dynamic charts and tables
- ✅ PDF reports with visualizations
- ✅ Clarification and follow-up support
- ✅ Complete documentation

### 🎥 Demo Video

Ready for 3-4 minute demo showcasing:
1. User query input
2. Agent orchestration (behind-the-scenes)
3. Strategic signals detection
4. PDF report download



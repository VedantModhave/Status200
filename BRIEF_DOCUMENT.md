# EY Techathon 6.0 – Brief Document Submission

**Problem Statement:** PS1 – Pharmaceuticals  
**Team:** EY Techathon 6.0 – Pharma Domain  
**Submission Date:** December 2025

---

## Executive Summary

This document describes an **Agentic AI solution** for a multinational generic pharmaceutical company seeking to accelerate innovation opportunity identification. The system reduces research time from 2-3 months to minutes by orchestrating multiple specialized AI agents that analyze market data, clinical trials, patents, trade flows, and scientific literature.

**Key Innovation:** A Master Agent that intelligently routes queries to domain-specific Worker Agents, synthesizes findings, and automatically detects strategic signals (whitespace opportunities, biosimilar windows) using rule-based decision logic.

---

## 1. System Architecture Diagram

```
User Query → Master Agent → Worker Agents → Data Sources → Synthesis → PDF Report
                ↓
         [Query Analysis]
         [Task Planning]
         [Agent Selection]
                ↓
    ┌───────────┴───────────┐
    │                       │
IQVIA Agent          EXIM Agent
Patent Agent         Clinical Trials Agent
Internal Agent       Web Intelligence Agent
    │                       │
    └───────────┬───────────┘
                ↓
         [Synthesis Layer]
    [Strategic Signal Detection]
                ↓
         Report Generator
                ↓
         PDF Download
```

**Architecture Components:**
- **Frontend:** Streamlit web application with chat interface
- **Orchestration:** LangGraph workflow engine
- **Agents:** 7 specialized worker agents + 1 master orchestrator
- **Data Layer:** Mock CSV/JSON files simulating real APIs
- **Output:** PDF reports with charts, tables, and strategic insights

---

## 2. Agent Descriptions and Workflows

### Master Agent (Conversation Orchestrator)

**Role:** Central coordinator that interprets queries, plans tasks, and synthesizes results.

**Key Functions:**
1. **Query Interpretation:** Analyzes user intent using keyword matching
2. **Task Planning:** Breaks queries into modular research tasks
3. **Agent Selection:** Routes to relevant worker agents based on query keywords
4. **Clarification Handling:** Asks clarifying questions for vague queries
5. **Follow-up Support:** Handles non-linear inputs like "Also check for..."
6. **Synthesis:** Combines all agent outputs into coherent summary
7. **Strategic Signals:** Detects whitespace and opportunity flags

**Workflow:**
```
User Query → Intent Classification → Agent Selection → Task Delegation → 
Result Collection → Synthesis → Strategic Signal Detection → PDF Generation
```

---

### Worker Agents

| Agent | Responsibility | Data Source | Output Type |
|-------|---------------|-------------|-------------|
| **IQVIA Insights** | Market size, growth, competition | `iqvia_markets.csv` | Tables, Line Charts |
| **EXIM Trade** | Import/export volumes, sourcing | `exim_trade.csv` | Tables, Bar Charts |
| **Patent Landscape** | Patent filings, expiry, FTO risks | `patents.json` | Patent Tables |
| **Clinical Trials** | Trial pipeline, phases, sponsors | `clinical_trials.csv` | Tables, Phase Charts |
| **Internal Insights** | PDF analysis, strategy documents | Uploaded PDFs | Text Summaries |
| **Web Intelligence** | Guidelines, RWE, publications | `web_results.json` | Text with References |
| **Report Generator** | PDF formatting and generation | All agent outputs | PDF Report |

---

## 3. Data Assumptions

### Mock Data Sources

All data sources are simulated using CSV/JSON files that mimic real API responses:

1. **IQVIA Mock API** (`data/iqvia_markets.csv`)
   - Market size, CAGR, competitor data per therapy area
   - Currently covers: Tiotropium in India/US (2021-2024)

2. **EXIM Mock Server** (`data/exim_trade.csv`)
   - Import/export volumes, unit prices, source countries
   - Trade data for Tiotropium API/formulations

3. **USPTO API Clone** (`data/patents.json`)
   - Patent filings, expiry timelines, FTO risk ratings
   - 3 patents for Tiotropium with varying expiry dates

4. **Clinical Trials API Stub** (`data/clinical_trials.csv`)
   - Active trials, phases, sponsors, status
   - Tiotropium trials in India and US

5. **Web Search Proxy** (`data/web_results.json`)
   - Mock web search results for guidelines and RWE
   - Pre-configured snippets for Tiotropium queries

6. **Internal Docs Repository**
   - PDF upload functionality
   - Text extraction via PyPDF2
   - Keyword-based analysis

### Data Limitations

- **Coverage:** Currently optimized for Tiotropium molecule
- **Geographies:** Primary focus on India and US
- **Time Range:** 2021-2024 for market/trade data
- **Production:** Would connect to real APIs with proper authentication

---

## 4. Example Customer Queries

The system has been tested with 10+ strategic queries (see `data/example_queries.csv`):

**Sample Queries:**
1. "Find innovation opportunities for tiotropium in India over the next 5 years"
2. "Which respiratory diseases show low competition but high patient burden in India?"
3. "Identify molecules with patents expiring within 2 years and strong market growth"
4. "Where is the whitespace in severe asthma therapy in the US?"
5. "Also check for biosimilar competition" (follow-up query)
6. "Show market trends and patent landscape" (multi-agent query)
7. "Generate a one-page innovation brief for tiotropium"

**Query Handling:**
- ✅ Open-ended questions → Clarification asked if needed
- ✅ Specific queries → Relevant agents selected
- ✅ Follow-up queries → Additional agents added to workflow
- ✅ Entity extraction → Molecule/region detected from query

---

## 5. Decision Logic (Strategic Signals)

The Master Agent implements rule-based decision logic to identify opportunities:

### Whitespace Detection
**Rule:** High market size (≥USD 100m) + Low active trials (≤2)  
**Output:** "🔍 Whitespace: High-value but under-explored market..."

### Biosimilar Opportunity
**Rule:** Patent expiry within 2 years  
**Output:** "💡 Opportunity: Key patent expires in [year], suggesting window for biosimilars..."

### Example Output:
```
Strategic Signals:
- 🔍 Whitespace: High-value but under-explored market: estimated market size ~USD 155m 
  with only 2 active/recruiting trials in the mock pipeline.
- 💡 Opportunity: Key patent US1234567A (composition) expires in 2025, suggesting a window 
  for biosimilars or differentiated formulations.
```

---

## 6. Technical Implementation

### Framework: LangGraph
- **Orchestration:** StateGraph with conditional routing
- **State Management:** TypedDict-based workflow state
- **Node Functions:** Each agent is a LangGraph node
- **Flow:** Sequential execution with agent-level task checking

### Key Files:
- `app/graph.py`: LangGraph workflow definition
- `app/agents/master.py`: Master Agent logic
- `app/agents/workers.py`: All 6 worker agents
- `app/agents/report.py`: PDF report generator
- `app/main.py`: Streamlit UI

### Dependencies:
- `langgraph>=0.2.0`: Agent orchestration
- `streamlit>=1.38.0`: Web UI
- `pandas>=2.2.0`: Data processing
- `matplotlib>=3.8.0`: Chart generation
- `reportlab>=4.2.0`: PDF generation
- `PyPDF2>=3.0.0`: PDF text extraction

---

## 7. Demo Walkthrough (3-4 minutes)

### Script for Video:

**0:00-0:30 | Introduction**
- "This system accelerates pharma innovation research from months to minutes"
- Show UI: Chat interface, sidebar configuration, file upload

**0:30-1:30 | Query Execution**
- Type: "Find innovation opportunities for tiotropium in India over 5 years"
- Show loading spinner: "Master Agent orchestrating worker agents..."
- Highlight agent activity panel showing 6 agents executing

**1:30-2:30 | Agent Results**
- Expand each agent expander:
  - IQVIA: Market growth chart
  - Clinical Trials: Phase distribution chart
  - Patents: Expiry timeline
  - EXIM: Trade volumes
- Emphasize: "Each agent processes its domain-specific data independently"

**2:30-3:15 | Strategic Signals**
- Show synthesized response with Strategic Signals section
- Highlight: Whitespace detection (high market + low trials)
- Highlight: Opportunity flag (patent expiry → biosimilar window)

**3:15-3:45 | PDF Report**
- Click "Download latest PDF report"
- Open PDF showing:
  - Executive Summary
  - All agent sections with charts and tables
  - Professional formatting

**3:45-4:00 | Closing**
- "This reduces research time from 2-3 months to minutes"
- "Same pattern scales to any molecule or therapy area"

---

## 8. Innovation Highlights

1. **Query-Aware Orchestration:** Master Agent intelligently selects agents based on query intent
2. **Strategic Signal Detection:** Automatic identification of whitespace and opportunities
3. **Follow-up Query Support:** Handles non-linear conversations ("Also check for...")
4. **Clarification Handling:** Asks clarifying questions for vague queries
5. **Dynamic Visualization:** Charts generated on-the-fly from data
6. **Comprehensive PDF Reports:** All findings consolidated into professional reports

---

## 9. Production Readiness

### Current State (Demo):
- ✅ All 7 agents implemented and working
- ✅ Mock data simulating real APIs
- ✅ End-to-end workflow functional
- ✅ PDF reports with charts/tables

### Production Enhancements:
- Replace mock data with real API integrations (IQVIA, USPTO, ClinicalTrials.gov)
- Add LLM-powered synthesis for more sophisticated insights
- Implement RAG for internal document analysis
- Add multi-turn conversation context
- Scale to multiple molecules and geographies

---

## 10. Submission Checklist

- ✅ Live demo / recorded video (3-4 minutes)
- ✅ System Architecture Diagram
- ✅ Agent descriptions and workflows
- ✅ Data assumptions documented
- ✅ Example customer queries (10+ queries)
- ✅ Brief document (this file)

---

**End of Brief Document**


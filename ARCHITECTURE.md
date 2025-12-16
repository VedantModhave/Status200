# EY Techathon 6.0 – Pharma Agentic AI: System Architecture & Documentation

**Team:** EY Techathon 6.0 – Pharma Domain  
**Problem Statement:** PS1 – Pharmaceuticals  
**Date:** December 2025

---

## 1. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (Streamlit Web Application)                  │
│  • Chat Interface for Natural Language Queries                  │
│  • Sidebar: Molecule, Region, Time Horizon Selection          │
│  • File Upload: Internal Documents (PDF)                       │
│  • Agent Activity Panel: Real-time Agent Status                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MASTER AGENT                                  │
│              (Conversation Orchestrator)                         │
│  • Query Interpretation & Intent Classification                 │
│  • Task Planning & Agent Selection                              │
│  • Clarification Handling (if query is vague)                    │
│  • Follow-up Query Support                                      │
│  • Response Synthesis & Strategic Signal Detection              │
└────────────┬───────────────────────────────────┬─────────────────┘
             │                                   │
             │ Delegates Tasks                   │ Synthesizes Results
             │                                   │
             ▼                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WORKER AGENTS                                │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ IQVIA Insights   │  │ EXIM Trade       │  │ Patent       │  │
│  │ Agent            │  │ Agent            │  │ Landscape    │  │
│  │ • Market trends  │  │ • Trade volumes  │  │ Agent        │  │
│  │ • CAGR analysis  │  │ • Import/Export  │  │ • Patents    │  │
│  │ • Competition    │  │ • Sourcing      │  │ • Expiry     │  │
│  │ Output: Charts   │  │ Output: Charts   │  │ • FTO risks  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ Clinical Trials  │  │ Internal         │  │ Web          │  │
│  │ Agent             │  │ Insights Agent  │  │ Intelligence │  │
│  │ • Trial pipeline  │  │ • PDF analysis  │  │ Agent        │  │
│  │ • Phase dist.     │  │ • Key insights   │  │ • Guidelines │  │
│  │ • Sponsors        │  │ • Strategy docs │  │ • RWE        │  │
│  │ Output: Charts    │  │ Output: Summary │  │ • Publications│ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                   │
│                                                                  │
│  • IQVIA Mock API → data/iqvia_markets.csv                     │
│  • EXIM Mock Server → data/exim_trade.csv                       │
│  • USPTO API Clone → data/patents.json                         │
│  • Clinical Trials Stub → data/clinical_trials.csv             │
│  • Web Search Proxy → data/web_results.json                    │
│  • Internal Docs → Uploaded PDFs (processed via PyPDF2)        │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REPORT GENERATOR AGENT                       │
│                                                                  │
│  • Consolidates all agent findings                              │
│  • Formats Executive Summary with Strategic Signals             │
│  • Embeds charts and tables                                     │
│  • Generates downloadable PDF report                            │
│  • Output: reports/report_{molecule}.pdf                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Agent Descriptions and Workflows

### Master Agent (Conversation Orchestrator)

**Responsibilities:**
- Interprets user queries using keyword-based intent classification
- Breaks queries into modular research tasks
- Selects relevant worker agents based on query keywords
- Handles clarification questions for vague queries
- Supports follow-up queries (e.g., "Also check for biosimilar competition")
- Synthesizes responses from all worker agents
- Detects strategic signals (whitespace, opportunities) using rule-based logic

**Workflow:**
1. Receive user query
2. Check if clarification needed → return question if yes
3. Extract molecule/region from query if mentioned
4. Classify query intent (generic vs specific)
5. Select relevant agents (all agents for generic queries, keyword-matched for specific)
6. Delegate tasks to selected worker agents
7. Collect results from all agents
8. Synthesize findings with Strategic Signals
9. Pass to Report Generator

**Decision Logic:**
- **Whitespace Detection:** High market size (≥USD 100m) + Low active trials (≤2) → Whitespace flag
- **Opportunity Detection:** Patent expiry within 2 years → Biosimilar/Value-add opportunity flag

---

### Worker Agents

#### 1. IQVIA Insights Agent
**Input:** Molecule, Region, Time Horizon  
**Data Source:** `data/iqvia_markets.csv`  
**Processing:**
- Filters data by molecule and region
- Calculates market growth (base year → latest year)
- Extracts CAGR and competition metrics
- Generates market trend line chart

**Output:**
- Summary: Market size, growth rate, competition level
- Tables: Year-wise market data
- Charts: Market growth trend (line chart)

---

#### 2. EXIM Trade Agent
**Input:** Molecule, Region  
**Data Source:** `data/exim_trade.csv`  
**Processing:**
- Filters trade data by molecule and region
- Extracts import/export volumes
- Identifies key source countries
- Generates trade volume bar chart

**Output:**
- Summary: Import/export volumes, unit prices, source countries
- Tables: Year-wise trade data
- Charts: Import vs Export volumes (bar chart)

---

#### 3. Patent Landscape Agent
**Input:** Molecule  
**Data Source:** `data/patents.json`  
**Processing:**
- Filters patents by molecule
- Identifies earliest expiring patent
- Calculates years to expiry
- Flags FTO risks

**Output:**
- Summary: Number of patents, earliest expiry, FTO risk
- Tables: Complete patent listing with expiry dates

---

#### 4. Clinical Trials Agent
**Input:** Molecule, Region  
**Data Source:** `data/clinical_trials.csv`  
**Processing:**
- Filters trials by molecule and region
- Identifies active/recruiting trials
- Groups by trial phase
- Generates phase distribution chart

**Output:**
- Summary: Number of active trials, phase distribution
- Tables: Complete trial listing
- Charts: Trial phase distribution (bar chart)

---

#### 5. Internal Insights Agent
**Input:** Molecule, Region, Uploaded PDF (optional)  
**Data Source:** Uploaded PDF documents  
**Processing:**
- Extracts text from uploaded PDF using PyPDF2
- Analyzes content for key strategic terms
- Generates insights related to molecule and region

**Output:**
- Summary: Document analysis, key themes, strategic insights
- Raw References: Extracted text preview

---

#### 6. Web Intelligence Agent
**Input:** Molecule  
**Data Source:** `data/web_results.json`  
**Processing:**
- Retrieves mock web search results
- Extracts guideline and RWE insights
- Identifies repurposing opportunities

**Output:**
- Summary: Web insights, guideline extracts, RWE findings
- Raw References: Source URLs and snippets

---

#### 7. Report Generator Agent
**Input:** Complete ConversationState with all agent results  
**Processing:**
- Consolidates Executive Summary
- Formats Strategic Signals section
- Embeds all charts as images
- Formats all tables with styling
- Generates PDF using ReportLab

**Output:**
- PDF Report: `reports/report_{molecule}.pdf`
- Includes: Title, metadata, executive summary, all agent sections with charts/tables

---

## 3. Data Assumptions

### Mock Data Files

#### `data/iqvia_markets.csv`
**Schema:**
- `therapy_area`: Therapy area (e.g., "Respiratory")
- `country`: Country code (e.g., "India", "US")
- `year`: Year (2021-2024)
- `molecule`: Molecule name (e.g., "Tiotropium")
- `market_size_usd_mn`: Market size in USD millions
- `cagr_pct`: CAGR percentage
- `competitors`: Number of active competitors

**Coverage:** Tiotropium in India and US (2021-2024)

---

#### `data/exim_trade.csv`
**Schema:**
- `molecule`: Molecule name
- `country`: Country code
- `year`: Year
- `import_volume_kg`: Import volume in kg
- `export_volume_kg`: Export volume in kg
- `unit_price_usd`: Average unit price in USD
- `top_source_countries`: Pipe-separated source countries

**Coverage:** Tiotropium trade data for India and US

---

#### `data/patents.json`
**Schema:**
```json
{
  "molecule": "Tiotropium",
  "patent_no": "US1234567A",
  "assignee": "Company Name",
  "patent_type": "composition",
  "filing_date": "2010-01-15",
  "expiry_year": 2025,
  "indication": "COPD",
  "fto_risk": "high"
}
```

**Coverage:** 3 patents for Tiotropium with varying expiry dates

---

#### `data/clinical_trials.csv`
**Schema:**
- `nct_id`: Clinical trial identifier
- `molecule`: Molecule name
- `indication`: Disease indication
- `phase`: Trial phase (Phase 1, Phase 2, Phase 3, Phase 4)
- `status`: Trial status (Active, Recruiting, Completed)
- `sponsor`: Sponsor name
- `country`: Country where trial is conducted
- `start_date`: Trial start date
- `estimated_completion`: Estimated completion date

**Coverage:** Tiotropium trials in India and US

---

#### `data/web_results.json`
**Schema:**
```json
{
  "tiotropium_unmet_need": [
    {
      "title": "COPD Guidelines",
      "snippet": "Persistent symptoms in COPD patients...",
      "url": "https://example.com/guideline"
    }
  ]
}
```

**Coverage:** Mock web search results for Tiotropium-related queries

---

#### `data/example_queries.csv`
**Schema:**
- `id`: Query ID (1-10)
- `question`: Strategic pharma planner question

**Coverage:** 10 example queries covering various use cases

---

## 4. Example Customer Queries

The system supports 10+ strategic queries as documented in `data/example_queries.csv`:

1. "Find innovation opportunities for tiotropium in India over the next 5 years."
2. "Which respiratory diseases in India show high patient burden but limited clinical trial activity?"
3. "Identify molecules in COPD with patents expiring within the next 2 years and strong market growth."
4. "Where is the whitespace in severe asthma therapy in the US when considering trials and guidelines?"
5. "For tiotropium, compare EXIM trade dependence for India versus the US over the last 5 years."
6. "Highlight potential new indications or patient segments for tiotropium based on clinical trials and web evidence."
7. "Which therapy areas in India have high market growth but low competition according to IQVIA mock data?"
8. "For respiratory LAMAs, flag molecules where internal field insights suggest adherence or access gaps."
9. "Assess biosimilar opportunities in inhaled respiratory therapies based on patent expiries and market size."
10. "Generate a one-page innovation brief for tiotropium in India summarising market, patents, trials, and unmet needs."

---

## 5. Conversation Flow Capabilities

### Open-ended Questions
✅ **Supported:** "Where is the unmet need in oncology?"
- System asks clarification: "Would you like the analysis by region, therapy area, or both?"

### Clarifications
✅ **Supported:** System detects vague queries and asks clarifying questions
- Example: "Where is the unmet need?" → "Would you like by region or MoA?"

### Non-linear Inputs
✅ **Supported:** "Also check for biosimilar competition"
- System adds Patent Agent to existing task list
- Follow-up queries append additional agents instead of replacing

### Entity Extraction
✅ **Supported:** Extracts molecule and region from natural language queries
- "Find opportunities for Aspirin in India" → molecule="Aspirin", region="India"
- Falls back to sidebar defaults if not mentioned

---

## 6. Technical Stack

- **Framework:** LangGraph (Agent Orchestration)
- **UI:** Streamlit (Web Interface)
- **Data Processing:** Pandas, JSON
- **Visualization:** Matplotlib (Chart Generation)
- **PDF Generation:** ReportLab
- **PDF Processing:** PyPDF2 (Internal Documents)
- **Language:** Python 3.12+

---

## 7. Key Features

### Dynamic Agent Selection
- Query-aware routing based on keywords
- Generic queries trigger all agents
- Specific queries trigger relevant agents only

### Strategic Decision Logic
- **Whitespace Detection:** High market + Low trials → Opportunity
- **Biosimilar Window:** Patent expiry ≤2 years → Value-add opportunity

### Rich Outputs
- Formatted text summaries
- Interactive charts (market trends, trade volumes, trial phases)
- Data tables with proper formatting
- Professional PDF reports with all visualizations

### Error Handling
- Graceful handling of missing data
- Suggests alternatives when data not available
- Clear error messages explaining limitations

---

## 8. Future Enhancements (Production)

- **Real API Integration:** Replace mock data with real IQVIA, USPTO, ClinicalTrials.gov APIs
- **LLM-powered Synthesis:** Use GPT-4/Claude for more sophisticated synthesis
- **RAG for Internal Docs:** Vector embeddings for better document understanding
- **Multi-turn Conversations:** Maintain context across multiple queries
- **Advanced Analytics:** Machine learning models for opportunity scoring

---

**End of Architecture Documentation**


# StudyBot AI & Review Analytics

An interactive, AI-powered educational analytics platform that transforms unstructured student course evaluations into real-time visual insights, executive sentiment summaries, and interactive natural-language Q&A.

---

## Executive Overview

Educational institutions collect thousands of student course evaluations every semester. While numerical scores provide a high-level rating, **qualitative student feedback contains the crucial context** needed to understand *why* students are struggling or thriving.

**StudyBot AI & Review Analytics** bridges the gap between raw, unorganized survey datasets and actionable decision-making by combining high-speed Pandas data filtering, dynamic Plotly visualizations, and Large Language Model (LLM) intelligence.

---

## Target Audience & Core Use Cases

| User Persona | Key Pain Point | How StudyBot AI Solves It |
| :--- | :--- | :--- |
| **Academic Deans & Directors** | Lack macro visibility across departments; overwhelmed by massive CSV exports. | Instant macro KPI header & automated 1-click LLM executive summaries across subjects. |
| **Department Heads** | Need to isolate specific course modules or failing subjects mid-semester. | Multi-column filtering, rating range sliders, and root-cause analysis in seconds. |
| **Course Instructors** | Difficulty sifting through hundreds of comments to find critical feedback. | Color-coded feedback triage tagging green (5★), amber (3★), and red (1–2★) reviews. |
| **Quality Assurance Teams** | Need rapid evidence synthesis for accreditation and course review reporting. | Interactive natural-language Q&A directly grounded in the live, filtered dataset. |

---

## The Problem vs. The Solution

### The Problem: The Feedback Bottleneck
* **Spreadsheet Overload:** Feedback stays trapped in static CSV files that require hours of manual sorting and reading.
* **Delayed Interventions:** Course issues are typically analyzed long after the term ends, preventing timely student support.
* **Qualitative Blind Spots:** A $3.2 / 5.0$ star rating tells you a course has issues, but fails to explain *what* specific topic or teaching method failed.

### The Solution: StudyBot AI
* **Instant Qualitative Synthesis:** Converts hours of comment reading into seconds of AI summarization.
* **Grounded Natural-Language Chat:** Ask direct questions about student sentiment and receive contextual answers based on active filters.
* **Visual Severity Triage:** Immediately draws attention to urgent 1-star and 2-star student complaints for rapid intervention.

---

## Key Features & System Capabilities

* **Real-Time Macro KPIs:** Dynamic tracking of key statistics including Total Reviews, Average Course Rating, and Critical Complaint Counters (1–2 stars).
* **Interactive Filtering Engine:** Slide rating thresholds (1.00–5.00), select specific academic subjects, and filter metadata with instant chart re-rendering.
* **LLM Executive Summaries:** One-click qualitative sentiment synthesis powered by `meta-llama/Llama-3.2-3B-Instruct` via the Hugging Face Inference API.
* **Color-Coded Feedback Explorer:** Categorized feedback cards with visual severity indicators (Green = 5★ Praise, Amber = 3★ Neutral, Red = 1–2★ Critical Alert).
* **Ask StudyBot Assistant:** Context-aware chat agent that receives live dataframe state to answer natural-language queries about course trends.
* **Adaptive Dual-Theme UI:** Professional custom CSS interface supporting seamless Light Mode and Dark Mode environments.

---

## Architecture & Data Flow

```text
┌─────────────────────────┐
│ Raw CSV / User Upload   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Pandas Data Engine      │ ── (Filters & Calculates Metrics)
└────────────┬────────────┘
             │
      ┌──────┴──────────────────────────┐
      ▼                                 ▼
┌─────────────────────────┐   ┌──────────────────────────────────┐
│ Plotly Visual Analytics │   │ Hugging Face Inference API       │
│ (Interactive Charts)    │   │ (Llama-3.2-3B-Instruct Model)    │
└────────────┬────────────┘   └─────────────────┬────────────────┘
             │                                  │
             └────────────────┬─────────────────┘
                              ▼
                ┌───────────────────────────┐
                │ Streamlit Web Dashboard   │
                │ (Interactive Dual-Theme UI)│
                └───────────────────────────┘

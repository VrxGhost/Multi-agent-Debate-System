---
title: Multi-agent-Debate-System 
emoji: ⚖️
colorFrom: purple
colorTo: blue
sdk: streamlit
sdk_version: "1.45.0"
app_file: app.py
pinned: false
---

# ⚖️ Multi-Agent Debate System

A multi-agent AI system where two LLMs argue opposing sides of any claim across multiple rounds, with a third LLM acting as an impartial judge that scores each round and declares a winner.

Built with LangGraph for agent orchestration and Streamlit for the live UI.

[![Live Demo](https://img.shields.io/badge/🤗%20Live%20Demo-Hugging%20Face-yellow?style=for-the-badge)](https://huggingface.co/spaces/VrxGhost/Multi-Agent-Debate-System)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-latest-green?style=flat)
![Streamlit](https://img.shields.io/badge/Streamlit-latest-red?style=flat&logo=streamlit)
![Groq](https://img.shields.io/badge/Groq-Free_API-orange?style=flat)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)

---

## 🔴 Live Demo

👉 **[Try it here — huggingface.co/spaces/VrxGhost/Multi-Agent-Debate-System](https://huggingface.co/spaces/VrxGhost/Multi-Agent-Debate-System)**

Enter any controversial claim and watch three AI agents debate it in real time.

---

## 🎯 What it does

You enter any controversial claim — the system spins up three AI agents:

- 🔵 **PRO Agent** (`qwen/qwen3-32b`) — argues strongly **for** the claim
- 🔴 **CON Agent** (`meta-llama/llama-4-scout-17b-16e-instruct`) — argues strongly **against** the claim
- ⚖️ **Judge Agent** (`llama-3.3-70b-versatile`) — scores each round 1–10 and declares a winner

Each agent reads the opponent's last argument and counter-argues across N rounds. The judge tallies round wins and declares the overall debate winner with full reasoning.

---

## 🏗️ Architecture

```
app.py
  └── debate_graph.py        ← LangGraph orchestration
        ├── pro_agent.py     ← PRO LLM agent
        ├── con_agent.py     ← CON LLM agent
        ├── judge_agent.py   ← Judge LLM agent
        ├── llms.py          ← 3 different Groq models
        └── state.py         ← Shared DebateState (TypedDict)
```

### Agent Flow

```
START → PRO argues → CON counters → JUDGE scores
           ↑                              |
           |         (loop N rounds)      |
           └──────────────────────────────┘
                                          |
                                    FINAL VERDICT
```

The `DebateState` dictionary is passed between all agents — each one reads from it and writes back to it, maintaining full debate history across rounds.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **LangGraph** | Agent orchestration and state graph |
| **LangChain Groq** | LLM API wrapper |
| **Groq API** | Free inference for open-source models |
| **Streamlit** | Live web UI |
| **Python TypedDict** | Structured shared state between agents |
| **python-dotenv** | Secure API key management |

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/Multi-agent-Debate-System.git
cd Multi-agent-Debate-System
```

### 2. Create and activate virtual environment

```bash
python -m venv debate
# Windows
.\debate\Scripts\activate
# Mac/Linux
source debate/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get your free Groq API key

- Go to [console.groq.com](https://console.groq.com)
- Sign up for free (no credit card needed)
- Create an API key

### 5. Create `.env` file

```
GROQ_API_KEY=your_groq_api_key_here
```

### 6. Run the app

```bash
streamlit run app.py
```

---

## 📁 File Structure

```
Multi-agent-Debate-System/
├── app.py              # Streamlit UI
├── debate_graph.py     # LangGraph graph builder + flow control
├── pro_agent.py        # PRO side agent logic
├── con_agent.py        # CON side agent logic
├── judge_agent.py      # Judge agent + score parser
├── llms.py             # 3 Groq LLM instances
├── state.py            # DebateState TypedDict
├── requirements.txt    # Dependencies
├── .env                # API keys (not committed)
├── .gitignore          # Ignores .env and venv
└── README.md
```

---

## 💡 Key Design Decisions

**Why 3 different models?**
Each agent uses a model suited to its role — PRO uses `qwen3-32b` for strong reasoning and persuasion, CON uses `llama-4-scout` for fast and nuanced countering, and the Judge uses `llama-3.3-70b` as the most capable model for fair evaluation. This simulates diverse reasoning styles and prevents model bias in the debate outcome.

**Why LangGraph over a simple loop?**
LangGraph manages state transitions, conditional edges, and agent routing declaratively — making the orchestration clean, readable, and easy to extend with additional agents.

**Why TypedDict for state?**
Gives full IDE autocomplete and type safety across all agent files without introducing circular imports — keeping the codebase modular and maintainable.

---

## 📸 Screenshots
<img width="2879" height="1510" alt="Screenshot 2026-05-30 120902" src="https://github.com/user-attachments/assets/f2aae629-d912-4df1-aa24-9b43ec957b5b" />


<img width="2871" height="1520" alt="image" src="https://github.com/user-attachments/assets/f51d63bc-63d3-4d3d-9ca1-403168cf77a4" />

---

## 📄 License

MIT License — free to use and modify.

---

## 🙋 Author

Built to demonstrate multi-agent LLM orchestration, prompt engineering, and agentic system design using free open-source models.

> *"Multi-agent systems are the hottest interview topic in 2026 — this project shows you understand agent orchestration, not just prompt engineering."*

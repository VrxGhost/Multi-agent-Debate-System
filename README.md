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

Two LLM agents argue opposite sides of any claim for up to 10 rounds, and a third LLM judges every round. Built with LangGraph and Streamlit, running on Groq's free API and deployed on Hugging Face Spaces.

[![Live Demo](https://img.shields.io/badge/%F0%9F%9A%80_Live_Demo-HuggingFace_Spaces-orange)](https://huggingface.co/spaces/VrxGhost/Multi-Agent-Debate-System) [![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org) [![LangGraph](https://img.shields.io/badge/Agents-LangGraph-green)](https://langchain-ai.github.io/langgraph/) [![Streamlit](https://img.shields.io/badge/App-Streamlit-red)](https://streamlit.io) [![Groq](https://img.shields.io/badge/LLMs-Groq-F55036)](https://console.groq.com) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

<!-- Screenshots: replace each SCREENSHOT-…-LINK below with that image's github.com/user-attachments link -->
<img width="2879" height="1400" alt="Debate settings in the sidebar and round 1 of a debate on remote work" src="SCREENSHOT-1-LINK" />

*Pick a claim and 1–10 rounds in the sidebar, which also lists the three models in use. Each round appears as soon as the judge has scored it.*

<img width="2876" height="1225" alt="Round 2: PRO and CON arguments side by side with the judge's scores and reasoning" src="SCREENSHOT-2-LINK" />

*Every round shows both arguments side by side, the judge's scores out of 10, the round winner and a one-sentence reason.*

<img width="2819" height="1484" alt="Round 3 and the final result: PRO wins 3 rounds to 0" src="SCREENSHOT-3-LINK" />

*The final result counts rounds won (3–0 for PRO here), and the full PRO → CON → JUDGE log is one click away.*

---

## ✨ Highlights

- **Three LLM agents on a LangGraph state machine:** PRO → CON → judge, looping for 1–10 rounds, then a verdict node
- **A judge parser that survives format drift:** reads `**PRO_SCORE:** 8`, `8/10`, `7.5` and lowercase labels, keeps every score between 1 and 10, and takes the round winner from the scores
- **A live UI that keeps your result:** each round appears as soon as it's judged, and the finished debate stays on screen when you touch the sidebar
- **Fails gracefully:** a missing or wrong key, Groq rate limits, a retired model or an unreadable judge reply each show a clear message instead of a traceback
- **Safe to leave public on a free key:** claims are capped at 600 characters and debates at 10 rounds, and the claim never goes into a system prompt
- **Reproducible and auto-deployed:** pinned dependencies, an explicit LangGraph step limit, and a GitHub Actions workflow that pushes every commit on `main` to the Space

---

## 🔴 Live Demo

👉 **[Try it here → huggingface.co/spaces/VrxGhost/Multi-Agent-Debate-System](https://huggingface.co/spaces/VrxGhost/Multi-Agent-Debate-System)**

Type a claim, pick the number of rounds and click **Start Debate**. Each round appears as soon as the judge has scored it, followed by the final result and the full debate log.

The Space goes to sleep when nobody has used it for a while, so the first load can take a minute. All visitors share one free Groq key: if you see a rate-limit message, wait a minute and try fewer rounds.

---

## 🎯 The Three Agents

| Agent | Model on Groq | Job | What it sees |
| --- | --- | --- | --- |
| 🔵 **PRO** | `openai/gpt-oss-20b` | Argues **for** the claim in at most 3 sentences | The claim and CON's last argument |
| 🔴 **CON** | `qwen/qwen3.8-27b` | Argues **against** the claim in at most 3 sentences | The claim and PRO's newest argument |
| ⚖️ **Judge** | `openai/gpt-oss-120b` | Scores both sides from 1 to 10 and gives a one-sentence reason | The claim and both arguments of the round |

The side that wins more rounds wins the debate. Tied rounds count for neither side.

---

## 🏛️ System Architecture

![System Architecture](docs/diagrams/1-system-architecture.svg)

The visitor's browser talks to a Streamlit app on a Hugging Face Space. `app.py` checks the API key and the input, then runs the LangGraph graph from `debate_graph.py`. Its three agents call three Groq models through `llms.py`, the only file that names the models. Every push to `main` runs a GitHub Actions workflow that force-pushes the repo to the Space, where Hugging Face installs the pinned `requirements.txt` and restarts the app. The workflow only deploys; it doesn't run tests yet.

---

## 🔄 How It Works

![How a debate runs](docs/diagrams/2-how-it-works.svg)

```
START → pro → con → judge → more rounds? ── yes → pro
                                         └─ no  → verdict → END
```

1. **One shared state.** Every node reads and updates the same `DebateState` dictionary: the claim, the round counter, both sides' arguments, the judge's scores and an ordered debate log.
2. **One round is three nodes.** `pro` and `con` each send their model the claim and the opponent's latest argument, both wrapped in `<<` `>>` so they read as debate content rather than instructions. `judge` sends the claim and both arguments to the largest model.
3. **Turning the judge's text into numbers.** `parse_verdict()` uses regular expressions to find both scores, even in markdown, `8/10` or decimal form. It keeps them between 1 and 10 and gives the round to the higher score; on a tie it keeps the judge's own pick. A reply without scores raises an error that the UI turns into a message.
4. **Looping.** `should_continue` sends the graph back to `pro` while rounds remain. Then `verdict` counts the rounds each side won and sets the winner to PRO, CON or TIE.
5. **Streaming.** `app.py` runs the graph with `graph.stream(..., stream_mode="values")` and a step limit of `3 × rounds + 5`, and draws each round the moment its score appears.

---

## ⚙️ How the App Works

**Activity diagram:** everything that can happen from opening the page to the final result.

![Activity Diagram](docs/diagrams/3-activity-diagram.svg)

Streamlit reruns `app.py` from top to bottom every time you touch a widget, and `st.button` is `True` only on the run right after the click. So the finished debate is saved in `st.session_state` and redrawn on later reruns without any new API calls. Starting a new debate replaces it.

| Situation | What you see |
| --- | --- |
| `GROQ_API_KEY` is missing | A red message that says where to add the key; nothing else loads |
| The key is wrong | "Groq rejected the API key…" |
| Groq's free-tier rate limit is hit | A rate-limit message; finished rounds stay on screen |
| A model is retired, or Groq is down | "The call to Groq failed (…)"; finished rounds stay on screen |
| The judge's reply has no scores | A message asking you to start the debate again |
| The claim is blank | A warning, and no API calls |
| The claim is very long | The box stops at 600 characters |
| You move the slider after a debate | The debate stays, with a note that it's your last one |

---

## 💡 Key Design Decisions

**Why LangGraph instead of a loop?** The debate is a small state machine: three nodes, a conditional edge that loops back, and a verdict node. LangGraph makes that flow explicit, enforces a step limit, and lets the UI stream the state after every step.

**Why different model families?** CON runs on Qwen while PRO and the judge use OpenAI's open-weight gpt-oss models, so the two debaters don't argue the same way. The judge gets the biggest model. The trade-off is described under Known Limitations.

**Why does the winner come from the scores?** The judge also writes a `ROUND_WINNER` line, but an LLM can contradict its own numbers. Taking the winner from the scores keeps the round winner, the numbers on screen and the final tally consistent.

**Why keep the claim out of the system prompt?** The system prompt sets the model's rules, so a claim pasted there could rewrite them ("ignore all previous instructions…"). The claim goes in the user message between `<<` and `>>`, and both debaters are told to treat it as debate content.

---

## 🧠 Key Learnings

**LLM output is not an API.** The first judge parser only understood the exact line `PRO_SCORE: 8`. A reply like `**PRO_SCORE:** 8` silently became a 5–5 tie, and `8/10` crashed it. Regex parsing, range checks and taking the winner from the scores fixed both.

**Defaults change under you.** Groq retired all three Llama models this project started with in July and August 2026. LangGraph raised its default step limit from 25 to about 10,000 in version 1.0.6, which was the only reason 10-round debates (31 steps) worked before the limit was set explicitly. The model names now live in one file with environment-variable overrides, and the dependencies are pinned.

**Streamlit reruns everything.** Moving the slider after a debate used to wipe the result, because the button is `True` for one run only. Keeping the result in `st.session_state` fixed it without extra API calls.

**Check a problem before fixing it.** Qwen models can put their reasoning inside `<think>` tags, which would leak into CON's arguments. 15 real CON replies from the live Space contained none, so no workaround was added.

---

## ⚠️ Known Limitations

- **Debaters have a short memory.** Each one sees the claim and only the opponent's latest argument, not the whole debate.
- **CON runs on a Groq Preview model.** Groq can retire `qwen/qwen3.8-27b` at short notice. The app then shows an error message until `CON_MODEL` is set to another model.
- **The judge may favour PRO's style.** PRO and the judge both run gpt-oss models, and PRO won most rounds in test debates. Part of that may be the judge preferring text from its own model family.
- **One shared free key.** Groq's free tier has per-minute request and token limits, and a 10-round debate makes 30 calls, so busy moments can hit them.
- **No automated tests yet.** They're next on the roadmap.

---

## 🗂️ Project Structure

```
Multi-agent-Debate-System/
│
├── app.py                              # Streamlit UI: settings, live rounds, results, errors
├── debate_graph.py                     # DebateState, the LangGraph graph and the verdict
├── pro_agent.py                        # PRO debater
├── con_agent.py                        # CON debater
├── judge_agent.py                      # Judge + parse_verdict(), the score parser
├── llms.py                             # Model names (MODELS) + the three Groq clients
├── requirements.txt                    # Pinned dependencies
├── .env.example                        # Template for your GROQ_API_KEY
├── docs/
│   └── diagrams/
│       ├── 1-system-architecture.svg   # Browser → Space → Groq, plus the deploy path
│       ├── 2-how-it-works.svg          # The LangGraph loop, its state, the judge parser
│       └── 3-activity-diagram.svg      # Every path through one run of app.py
├── .github/
│   └── workflows/
│       └── sync-to-hf.yml              # Pushes main to the Hugging Face Space
└── README.md                           # This file; its header is the Space config
```

---

## 🚀 Run Locally

With Python 3.10 or newer:

```bash
git clone https://github.com/VrxGhost/Multi-agent-Debate-System.git
cd Multi-agent-Debate-System
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
```

Get a free API key at [console.groq.com](https://console.groq.com) (no credit card needed) and put it in `.env` after `GROQ_API_KEY=`. Then start the app:

```bash
streamlit run app.py
```

and open http://localhost:8501.

### Configuration

| Variable | Default | What it does |
| --- | --- | --- |
| `GROQ_API_KEY` | *(required)* | Your Groq key: in `.env` locally, or under **Settings → Variables and secrets** on a Hugging Face Space |
| `PRO_MODEL` | `openai/gpt-oss-20b` | Model for the PRO debater |
| `CON_MODEL` | `qwen/qwen3.8-27b` | Model for the CON debater |
| `JUDGE_MODEL` | `openai/gpt-oss-120b` | Model for the judge |
| `MAX_ROUNDS` | `10` | The highest value on the rounds slider |

---

## 🛠️ Tech Stack

| Layer | Tools |
| --- | --- |
| Agents | LangGraph 1.2 (`StateGraph`, conditional edges), LangChain Core |
| LLMs | Groq API through `langchain-groq`: gpt-oss-20b, Qwen 3.8 27B, gpt-oss-120b |
| App | Streamlit 1.45 |
| Deployment | Hugging Face Spaces, GitHub Actions |
| Config | python-dotenv, environment variables |

---

## 🗺️ Roadmap

- [x] Three-agent debate loop with LangGraph
- [x] Judge parsing that survives format changes; the winner comes from the scores
- [x] Rounds appear live; clear error messages instead of tracebacks
- [x] The last debate survives reruns
- [x] Input limits and prompt-injection-resistant prompts
- [x] Pinned dependencies and an explicit step limit
- [x] Auto-deploy with GitHub Actions
- [ ] Unit tests and linting in GitHub Actions before deploying
- [ ] Partial state updates with LangGraph reducers
- [ ] Give the debaters the full debate history
- [ ] Structured output for the judge, so there is nothing to parse

---

## 📄 License

MIT. See [LICENSE](LICENSE).

---

## 👤 Author

**Arya Dutta**, B.Tech CSE student at IEM Kolkata, building AI and backend systems

[![HuggingFace](https://img.shields.io/badge/HuggingFace-VrxGhost-yellow)](https://huggingface.co/VrxGhost) [![GitHub](https://img.shields.io/badge/GitHub-VrxGhost-181717)](https://github.com/VrxGhost) [![LinkedIn](https://img.shields.io/badge/LinkedIn-Arya_Dutta-0A66C2)](https://www.linkedin.com/in/arya-dutta-9a4619317)

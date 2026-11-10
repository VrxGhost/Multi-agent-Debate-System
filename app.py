import os
import streamlit as st
import groq
from langgraph.errors import GraphRecursionError

from dotenv import load_dotenv
load_dotenv()
st.set_page_config(
    page_title="AI Debate Arena",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Multi-Agent Debate Arena")
st.caption("Two LLMs argue a claim across multiple rounds. A judge scores each round and declares a winner.")
if not os.getenv("GROQ_API_KEY"):
    st.error(
        "GROQ_API_KEY is not set. Copy .env.example to .env and paste your Groq key into it. "
        "On Hugging Face, add it under Space settings > Variables and secrets."
    )
    st.stop()

from debate_graph import build_graph, recursion_limit_for # noqa: E402  (needs the key, so it must come after the check)

from llms import MODELS  # noqa: E402

MAX_CLAIM_CHARS = 600
MAX_ROUNDS = max(2, int(os.getenv("MAX_ROUNDS", "10")))  # e.g. MAX_ROUNDS=5 in Space settings; the slider needs at least 2

def show_round(score, pro_argument, con_argument):
    """Draw one finished round: both arguments, the judge's scores and the reason."""
    st.markdown(f"## ♦️ Round {score['round']}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔵 PRO")
        st.info(pro_argument)
    with col2:
        st.markdown("### 🔴 CON")
        st.error(con_argument)

    st.markdown("#### ⚖️ Judge's Verdict")
    j1, j2, j3 = st.columns(3)
    with j1:
        st.metric(label="PRO Score", value=f"{score['pro']}/10")
    with j2:
        st.metric(label="CON Score", value=f"{score['con']}/10")
    with j3:
        st.metric(label="Round Winner", value=score["winner"])

    st.caption(f"🧠 Judge's reasoning: {score['reason']}")
    st.divider()

with st.sidebar:
    st.header("⚙️ Debate Settings")
    st.divider()
    
    claim = st.text_area(
        "Enter a claim to debate:",
        value="Remote work is better than working from office",
        height=130,
        max_chars=MAX_CLAIM_CHARS,
        help="Enter any controversial topic you want the AI agents to debate"
    )
    
    rounds = st.slider(
        "Number of rounds:",
        min_value = 1,
        max_value=MAX_ROUNDS,
        value=min(3, MAX_ROUNDS),
        help="More rounds = longer debate"
    )
    
    st.divider()
    st.markdown("**Models being used:**")
    st.markdown(f"🔵 PRO — `{MODELS['PRO']}`")
    st.markdown(f"🔴 CON — `{MODELS['CON']}`")
    st.markdown(f"⚖️ JUDGE — `{MODELS['JUDGE']}`")
    st.divider()
    
    start = st.button(
        "🚀 Start Debate",
        type="primary",
        use_container_width=True
    )
claim = claim.strip()[:MAX_CLAIM_CHARS]
if start and not claim:
    st.warning("Please enter a claim to debate first.")
    st.stop()

if not start:
    st.info("👈 Set your claim and number of rounds in the sidebar, then click Start Debate!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🔵 PRO Agent")
        st.write("Argues strongly FOR the claim")
    with col2:
        st.markdown("### 🔴 CON Agent")
        st.write("Argues strongly AGAINST the claim")
    with col3:
        st.markdown("### ⚖️ Judge Agent")
        st.write("Scores each round and declares the overall winner")

if start:
    graph = build_graph()

    initial_state = {
        "claim": claim,
        "rounds": rounds,
        "current_round": 1,
        "pro_arguments": [],
        "con_arguments": [],
        "scores": [],
        "winner": "",
        "debate_log": []
    }

    st.markdown(f"## 📋 Debate Topic")
    st.info(f'"{claim}"')
    st.divider()

    shown = 0  # how many rounds are already on the screen
    try:
        with st.spinner("Agents are debating... each round appears as soon as the judge scores it"):
            for result in graph.stream(
                initial_state,
                {"recursion_limit": recursion_limit_for(rounds)},
                stream_mode="values",
            ):
                while shown < len(result["scores"]):
                    show_round(result["scores"][shown], result["pro_arguments"][shown], result["con_arguments"][shown])
                    shown += 1
    except groq.AuthenticationError:
        st.error("Groq rejected the API key. Check GROQ_API_KEY in your .env file or in the Space secrets.")
        st.stop()
    except groq.RateLimitError:
        st.error("Groq's free-tier rate limit was reached. Wait a minute, then try again with fewer rounds.")
        st.stop()
    except groq.APIError as e:
        st.error(f"The call to Groq failed ({type(e).__name__}). Please try again in a moment.")
        st.stop()
    except ValueError:
        st.error("The judge's reply had no scores in it, so this round couldn't be scored. Please start the debate again.")
        st.stop()
    except GraphRecursionError:
        st.error("The debate ran more steps than expected and was stopped. This is a bug, please report it.")
        st.stop()


    # final winner
    st.markdown("## 🏆 Final Result")

    pro_wins = sum(1 for s in result["scores"] if s["winner"] == "PRO")
    con_wins = sum(1 for s in result["scores"] if s["winner"] == "CON")
    winner = result["winner"]

    w1, w2, w3 = st.columns(3)
    with w1:
        st.metric("Rounds won by PRO", pro_wins)
    with w2:
        st.metric("Rounds won by CON", con_wins)
    with w3:
        st.metric("🏆 Winner", winner)
    st.caption("The side that wins more rounds wins the debate. Tied rounds count for neither side.")

    if winner == "PRO":
        st.success("🏆 PRO side wins the debate!")
    elif winner == "CON":
        st.error("🏆 CON side wins the debate!")
    else:
        st.warning("🤝 It's a TIE!")

    # debate log expander
    with st.expander("📜 View Full Debate Log"):
        for entry in result["debate_log"]:
            if entry["side"] == "PRO":
                st.markdown(f"**🔵 PRO — Round {entry['round']}**")
                st.info(entry["argument"])
            elif entry["side"] == "CON":
                st.markdown(f"**🔴 CON — Round {entry['round']}**")
                st.error(entry["argument"])
            elif entry["side"] == "JUDGE":
                st.markdown(f"**⚖️ JUDGE — Round {entry['round']}**")
                st.warning(entry["argument"])
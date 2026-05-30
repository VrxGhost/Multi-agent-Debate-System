import streamlit as st
from debate_graph import build_graph

st.set_page_config(
    page_title="AI Debate Arena",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Multi-Agent Debate Arena")
st.caption("Two LLMs argue a claim across multiple rounds. A judge scores each round and declares a winner.")

with st.sidebar:
    st.header("⚙️ Debate Settings")
    st.divider()
    
    claim = st.text_area(
        "Enter a claim to debate:",
        value="Remote work is better than working from office",
        height=130,
        help="Enter any controversial topic you want the AI agents to debate"
    )
    
    rounds = st.slider(
        "Number of rounds:",
        min_value=1,
        max_value=8,
        value=3,
        help="More rounds = longer debate"
    )
    
    st.divider()
    st.markdown("**Models being used:**")
    st.markdown("🔵 PRO — `llama-3.1-8b-instant`")
    st.markdown("🔴 CON — `meta-llama/llama-4-scout-17b-16e-instruct`")
    st.markdown("⚖️ JUDGE — `llama-3.3-70b-versatile`")
    st.divider()
    
    start = st.button(
        "🚀 Start Debate",
        type="primary",
        use_container_width=True
    )

if not start:
    st.info("👈 Set your claim and number of rounds in the sidebar, then click Start Debate!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🔵 PRO Agent")
        st.write("Argues strongly FOR the claim using fast Llama model")
    with col2:
        st.markdown("### 🔴 CON Agent")
        st.write("Argues strongly AGAINST the claim using Mixtral model")
    with col3:
        st.markdown("### ⚖️ Judge Agent")
        st.write("Scores each round and declares the overall winner")

if start and claim:
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

    with st.spinner("Agents are debating... please wait"):
        result = graph.invoke(initial_state)

    # display each round
    for score in result["scores"]:
        r = score["round"]

        st.markdown(f"## ♦️ Round {r}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🔵 PRO")
            st.info(result["pro_arguments"][r - 1])

        with col2:
            st.markdown("### 🔴 CON")
            st.error(result["con_arguments"][r - 1])

        st.markdown("#### ⚖️ Judge's Verdict")
        j1, j2, j3 = st.columns(3)

        with j1:
            st.metric(
                label="PRO Score",
                value=f"{score['pro']}/10"
            )
        with j2:
            st.metric(
                label="CON Score",
                value=f"{score['con']}/10"
            )
        with j3:
            st.metric(
                label="Round Winner",
                value=score["winner"]
            )

        st.caption(f"🧠 Judge's reasoning: {score['reason']}")
        st.divider()

    # final winner
    st.markdown("## 🏆 Final Result")

    total_pro = sum(s["pro"] for s in result["scores"])
    total_con = sum(s["con"] for s in result["scores"])
    winner = result["winner"]

    w1, w2, w3 = st.columns(3)
    with w1:
        st.metric("Total PRO Score", f"{total_pro}")
    with w2:
        st.metric("Total CON Score", f"{total_con}")
    with w3:
        st.metric("🏆 Winner", winner)

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
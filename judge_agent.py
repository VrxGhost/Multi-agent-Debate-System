from langchain_core.messages import HumanMessage, SystemMessage
from llms import judge_llm


def judge_agent(state):     
    pro = state["pro_arguments"][-1]
    con = state["con_arguments"][-1]

    response = judge_llm.invoke([
        SystemMessage(content="Judge the debate. Format:\nPRO_SCORE: X\nCON_SCORE: X\nROUND_WINNER: PRO or CON\nREASON: one sentence"),
        HumanMessage(content=f"PRO: {pro}\nCON: {con}")
    ])
    text = response.content
    lines = text.strip().split("\n")
    score = {"round": state["current_round"], "pro": 5, "con": 5, "winner": "TIE", "reason": ""}
    for line in lines:
        if line.startswith("PRO_SCORE:"):
            score["pro"] = int(line.split(":")[1].strip())
        elif line.startswith("CON_SCORE:"):
            score["con"] = int(line.split(":")[1].strip())
        elif line.startswith("ROUND_WINNER:"):
            score["winner"] = line.split(":")[1].strip()
        elif line.startswith("REASON:"):
            score["reason"] = line.split(":", 1)[1].strip()
    state["scores"].append(score)   # ← saves score to state
    state["current_round"] += 1
    return state                  
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from pro_agent import pro_agent        # ← import line
from con_agent import con_agent        # ← import line
from judge_agent import judge_agent    # ← import line



class DebateState(TypedDict):
    claim: str
    rounds: int
    current_round: int
    pro_arguments: List[str]
    con_arguments: List[str]
    scores : List[dict]
    debate_log: List[dict]
    winner: str

def should_continue(state: DebateState) -> str:
    if state["current_round"] <= state["rounds"]:
        return "continue"
    return "end"

def final_verdict(state: DebateState) -> DebateState:
    pro_wins = sum(1 for s in state["scores"] if s["winner"] == "PRO")
    con_wins = sum(1 for s in state["scores"] if s["winner"] == "CON")
    if pro_wins > con_wins:
        state["winner"] = "PRO"
    elif con_wins > pro_wins:
        state["winner"] = "CON"
    else:
        state["winner"] = "TIE"
    return state

def build_graph():
    graph = StateGraph(DebateState)
    graph.add_node("pro", pro_agent)
    graph.add_node("con", con_agent)
    graph.add_node("judge", judge_agent)
    graph.add_node("verdict", final_verdict)   
    graph.set_entry_point("pro")
    graph.add_edge("pro", "con")
    graph.add_edge("con", "judge")
    graph.add_conditional_edges("judge", should_continue, {
        "continue": "pro",
        "end": "verdict"
    })
    graph.add_edge("verdict", END)            
    return graph.compile()
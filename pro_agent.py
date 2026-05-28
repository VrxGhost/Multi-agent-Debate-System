from langchain_core.messages import HumanMessage, SystemMessage
from llms import pro_llm  

def pro_agent(state):
    claim = state["claim"]
    history = ""
    if state["con_arguments"]:
        last_con = state["con_arguments"][-1]
        history = f"\nOpponent's last argument: {last_con}\nNow counter it."

    response = pro_llm.invoke([
        SystemMessage(content=f"You are arguing FOR: '{claim}'. Max 3 sentences."),
        HumanMessage(content=f"Round {state['current_round']}: Make your argument.{history}")
    ])
    arg = response.content
    state["pro_arguments"].append(arg)
    state["debate_log"].append({"round": state["current_round"], "side": "PRO", "argument": arg})
    return state
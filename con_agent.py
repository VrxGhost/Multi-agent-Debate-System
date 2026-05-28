from llms import con_llm
from langchain_core.messages import HumanMessage, SystemMessage

def con_agent(state):        
    claim = state["claim"]
    last_pro = state["pro_arguments"][-1]

    response = con_llm.invoke([
        SystemMessage(content=f"Argue AGAINST: '{claim}'. Max 3 sentences."),
        HumanMessage(content=f"Counter this: '{last_pro}'")
    ])
    state["con_arguments"].append(response.content)
    return state                  
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

MODELS = {
    "PRO": os.getenv("PRO_MODEL", "openai/gpt-oss-20b"),
    "CON": os.getenv("CON_MODEL", "qwen/qwen3.8-27b"),
    "JUDGE": os.getenv("JUDGE_MODEL", "openai/gpt-oss-120b"),
}

pro_llm = ChatGroq(model=MODELS["PRO"])
con_llm = ChatGroq(model=MODELS["CON"])
judge_llm = ChatGroq(model=MODELS["JUDGE"])
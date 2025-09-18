from agent_state_lib import AgentState
from langdetect import detect

def detect_language(state: AgentState) -> str:
    lang = detect(state["question"])
    return "english" if lang == "en" else "non_english"


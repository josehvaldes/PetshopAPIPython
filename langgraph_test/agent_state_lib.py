
from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    question: str
    embedded_question: Optional[str]
    retrieved_docs: Optional[List[str]]
    answer: Optional[str]

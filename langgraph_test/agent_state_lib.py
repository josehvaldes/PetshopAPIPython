
from typing import TypedDict, List, Optional
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import AIMessage, HumanMessage


class SimpleMessageHistory:
    def __init__(self):
        self.messages:list[HumanMessage|AIMessage] = []

    def get_messages(self):
        return self.messages

    def add_message(self, message: HumanMessage|AIMessage):
        self.messages.append(message)
    

class AgentState(TypedDict):
    question: Optional[str]
    embedded_question: Optional[str]
    answer: Optional[str]
    db_path: Optional[str]
    user_id: Optional[str]

    #memory usecase
    chat_memory: Optional[str]
    profile_memory: Optional[List[str]]
    facts_memory: Optional[str]

    #for basic usecase
    retrieved_docs: Optional[List[str]]




from typing import TypedDict, List, Optional
from langchain.memory import VectorStoreRetrieverMemory, ConversationBufferMemory

class AgentState(TypedDict):
    question: Optional[str]
    embedded_question: Optional[str]
    answer: Optional[str]
    
    #memory usecase
    user_id: Optional[str]
    chat_memory: Optional[str]
    profile_memory: Optional[List[str]]
    facts_memory: Optional[str]

    #for basic usecase
    retrieved_docs: Optional[List[str]]




class MemoryDict(TypedDict):
    facts_memory: VectorStoreRetrieverMemory
    chat_memory: ConversationBufferMemory
    profile_memory: list[str] 



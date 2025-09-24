from agent_state_lib import AgentState, SimpleMessageHistory
from langchain.vectorstores import Milvus
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_milvus import Milvus
from petshop_memory.conversation_memory import SQLiteConversationMemory
from petshop_memory.profile_memory import SQLiteProfileMemory

from langchain_core.runnables import RunnableLambda, RunnableParallel

# Embedding model
embedding_model = HuggingFaceEmbeddings(model_name="multi-qa-mpnet-base-dot-v1")

#keep the retriever at Model level
retriever = Milvus(
    embedding_model,
    collection_name="Dogs_Breeds_milvus_EN_1",
    connection_args={"host": "localhost", "port": "19530"}
).as_retriever(search_kwargs={"k": 5})


def a_retrieve_facts_memory(state:AgentState):

    query = state["embedded_question"]
    docs = retriever.invoke(query)
    content = [ doc.page_content for doc in docs ]
    content_str = "\n".join(content)
    return content_str

# Define a node that retrieves memory
def retrieve_facts_memory(state:AgentState)-> AgentState:

    content_str = a_retrieve_facts_memory(state)
    return {**state, "facts_memory": content_str}


def a_retrieve_chat_history(state:AgentState):
    db_path = state["db_path"]
    user_id = state["user_id"]

    chat_history_handler = SQLiteConversationMemory(db_path)
    response = chat_history_handler.load_memory_variables(user_id)
    chat_history_handler.close()

    messages = response["chat_history"]
    chat_memory_str = "\n".join([
      f"Human: {msg.content}" if msg.type == "human" else f"AI: {msg.content}"
        for msg in messages
    ])

    return chat_memory_str

def retrieve_chat_history(state:AgentState)-> AgentState:
    chat_memory_str = a_retrieve_chat_history(state)
    return {**state, "chat_memory": chat_memory_str}

def a_retrieve_profile_memory(state:AgentState)-> AgentState:
    db_path = state["db_path"]
    user_id = state["user_id"]
    profile_memory_handler = SQLiteProfileMemory(db_path)
    profile_memory = profile_memory_handler.get_pet_summary(user_id)
    profile_memory_handler.close()
    profile_memory_str = '\n'.join(profile_memory)
    return profile_memory_str

def retrieve_profile_memory(state:AgentState)-> AgentState:
    profile_memory_str = a_retrieve_profile_memory(state)
    return {**state, "profile_memory": profile_memory_str}

def load_memory_nodes(parallelExecution:bool) -> RunnableLambda:

    if parallelExecution:
        # Wrap it as a Runnable
        fact_memory_node = RunnableLambda(a_retrieve_facts_memory)
        chat_memory_node = RunnableLambda(a_retrieve_chat_history)
        profile_memory_node = RunnableLambda(a_retrieve_profile_memory)
        
        # Combine them into a parallel runnable
        memory_builder = RunnableParallel({
            "facts_memory": fact_memory_node,
            "profile_memory": profile_memory_node,
            "chat_memory": chat_memory_node
        })
        return memory_builder
    else:
        # Wrap it as a Runnable
        fact_memory_node = RunnableLambda(retrieve_facts_memory)
        chat_memory_node = RunnableLambda(retrieve_chat_history)
        profile_memory_node = RunnableLambda(retrieve_profile_memory)
        #chain the nodes for sequential execution    
        chain = fact_memory_node|chat_memory_node|profile_memory_node
        return chain

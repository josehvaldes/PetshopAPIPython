from agent_state_lib import AgentState, MemoryDict
from langchain.vectorstores import Milvus
from langchain.memory import VectorStoreRetrieverMemory
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_milvus import Milvus
from langchain.memory import ConversationBufferMemory
from petshop_memory.conversation_memory import SQLiteConversationMemory
from petshop_memory.profile_memory import SQLiteProfileMemory


# Embedding model
embedding_model = HuggingFaceEmbeddings(model_name="multi-qa-mpnet-base-dot-v1")

#keep the retriever at Model level
retriever = Milvus(
    embedding_model,
    collection_name="Dogs_Breeds_milvus_EN_1",
    connection_args={"host": "localhost", "port": "19530"}
).as_retriever(search_kwargs={"k": 5})


def load_memory(db_path:str, user_id:str, facts_key:str) -> MemoryDict:

    milvus_facts = VectorStoreRetrieverMemory(retriever=retriever, memory_key=facts_key)

    chat_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    chat_history_handler = SQLiteConversationMemory(db_path)
    chat_data = chat_history_handler.load_memory_variables(user_id)
    messages = chat_data["chat_history"]
    for msg in messages:
        chat_memory.chat_memory.add_message(msg)

    chat_history_handler.close()

    profile_memory_handler = SQLiteProfileMemory(db_path)
    profile_memory = profile_memory_handler.get_pet_summary(user_id)
    profile_memory_handler.close()

    return {
        "facts_memory": milvus_facts,
        "chat_memory": chat_memory,
        "profile_memory": profile_memory
    }


# def retrieve_dog_profile(state:AgentState):
#     dog_info = state["memory"].load_memory_variables({})
#     return {"dog_profile": dog_info}

# def update_dog_age(state:AgentState):
#     new_age = state["input"]["age"]
#     state["memory"].save_context({"input": "update"}, {"output": f"Dog age is now {new_age}"})
#     return state



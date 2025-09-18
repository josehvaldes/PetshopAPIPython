#milvus tool
from agent_state_lib import AgentState
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_milvus import Milvus

# Embedding model
embedding_model = HuggingFaceEmbeddings(model_name="multi-qa-mpnet-base-dot-v1")
vector_store = Milvus(
    embedding_model,
    collection_name="Dogs_Breeds_milvus_EN_1",
    connection_args={"host": "localhost", "port": "19530"}
)


def retrieve_docs(state: AgentState) -> AgentState:

    if 'embedded_question' not in state or state['embedded_question'] is None:
        print(f"missing 'embedded_question' in state: {state}")
        return state    
    else:
        results = vector_store.similarity_search(
            state['embedded_question'],
            k=6,
        )
        print(f"Retrieved {len(results)} documents from Milvus for the query: 'state['embedded_question']'")
        state['retrieved_docs'] = [doc.page_content for doc in results]
        return state
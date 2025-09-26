
from metaflow import FlowSpec, step

class HelloFlow(FlowSpec):
    """
    A flow where Metaflow prints 'Hi'.

    Run this flow to validate that Metaflow is installed correctly.

    """

    @step
    def start(self):
        """
        This is the 'start' step. All flows must have a step named 'start' that
        is the first step in the flow.

        """
        print("HelloFlow is starting.")
        self.db_path = "../sqlite_test/petshopdb/petshop_database.db"
        self.user_id = "pepuso"
        self.embedded_query = ""
        self.next(self.load_profile_memory, self.load_conversation_memory)

    @step
    def load_profile_memory(self):
        """
        A step for metaflow to load_profile_memory.

        """
        print("Metaflow says: Hi load_profile_memory!")
        from petshop_memory.profile_memory import SQLiteProfileMemory
        profile_memory_handler = SQLiteProfileMemory(self.db_path)
        profile_memory = profile_memory_handler.get_pet_summary(self.user_id)
        profile_memory_handler.close()
        profile_memory_str = '\n'.join(profile_memory)
        print("Profile memory:", profile_memory)

        self.profile_memory = profile_memory_str
        self.next(self.join)

    @step
    def load_conversation_memory(self):
        """
        A step for metaflow to load_conversation_memory.

        """
        print("Metaflow says: Hi load_conversation_memory!")
        from petshop_memory.conversation_memory import SQLiteConversationMemory
        chat_history_handler = SQLiteConversationMemory(self.db_path)
        response = chat_history_handler.load_memory_variables(self.user_id)
        chat_history_handler.close()

        messages = response["chat_history"]
        chat_memory_str = "\n".join([
        f"Human: {msg.content}" if msg.type == "human" else f"AI: {msg.content}"
            for msg in messages
        ])

        self.conversation_memory = chat_memory_str
        self.next(self.join)

    @step
    def load_facts_memory(self):
        """
        A step for metaflow to load_facts_memory.
        """
        print("Metaflow says: load_facts_memory!")
        from langchain.vectorstores import Milvus
        from langchain_huggingface import HuggingFaceEmbeddings

        try:
            # Embedding model
            embedding_model = HuggingFaceEmbeddings(model_name="multi-qa-mpnet-base-dot-v1")

            #keep the retriever at Model level
            retriever = Milvus(
                embedding_model,
                collection_name="Dogs_Breeds_milvus_EN_1",
                connection_args={"host": "172.23.208.1", "port": "19530"}
            ).as_retriever(search_kwargs={"k": 5})

            print(f"retriever created! {self.embedded_query}")
            docs = retriever.invoke(self.embedded_query)
            content = [ doc.page_content for doc in docs ]
            content_str = "\n".join(content)
            self.facts_memory = content_str
        except Exception as e:
            print(f"Error in load_facts_memory: {e}")
            self.facts_memory = "Error retrieving facts memory."
        finally:
            self.next(self.join)
        

    @step
    def join(self, inputs):
        """
        A step for metaflow to join memory.

        """
        
        self.profile_memory = inputs.load_profile_memory.profile_memory
        self.conversation_memory = inputs.load_conversation_memory.conversation_memory
        print("Metaflow says: Memory recovered")
        print("Profile memory:")
        print(self.profile_memory)
        print("Conversation memory:")
        print(self.conversation_memory)
        self.next(self.end)

    @step
    def end(self):
        """
        This is the 'end' step. All flows must have an 'end' step, which is the
        last step in the flow.

        """
        print("HelloFlow is all done.")


if __name__ == "__main__":
    HelloFlow()
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import Tool
from openAI.memory_tools.milvus_tool import milvus_tool, milvus_search
from openAI.memory_tools.profile_tool import user_profile_tool, user_profile_lookup
from openAI.memory_tools.azure_ai_search_tool import ai_search_tool, azure_ai_search

client = AIProjectClient.from_connection_string("..TODO..")

tools = [
    Tool.from_json(milvus_tool),
    Tool.from_json(user_profile_tool),
    Tool.from_json(ai_search_tool)
]

agent = client.agents.create_or_update(
    name="rag_agent",
    model="gpt-4o-mini",
    tools=tools,
    instructions="You are a helpful assistant that can retrieve documents from Milvus, Azure AI Search, and user profiles from Azure Storage Tables before answering."
)

response = client.agents.chat(
    agent_name="rag_agent",
    messages=[{"role": "user", "content": "What’s the best training plan for my dog?"}],
    context={"user_id": "{update the user here}}"}  
)
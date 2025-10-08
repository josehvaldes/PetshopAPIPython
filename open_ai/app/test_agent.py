import os
from app.settings import get_settings
#from app.memory_tools.milvus_tool import milvus_tool, milvus_search
#from app.memory_tools.profile_tool import user_profile_tool, user_profile_lookup
from app.memory_tools.azure_ai_search_tool import ai_search_tool, azure_ai_search

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import AzureAISearchQueryType, AzureAISearchTool, ListSortOrder, MessageRole
from azure.ai.projects.models import ConnectionType


settings = get_settings()


with AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=settings.azure_ai_foundry_endpoint
    ) as project_client:
    print("Creating AIProjectClient")
    conn = project_client.connections.get_default(ConnectionType.AZURE_AI_SEARCH)
    print("Got connection ID")
    print(f"Connection ID: {conn.id}")
    print(f"Connection Name: {conn.name}")
    conn_id = conn.id

    print(f"Creating AzureAISearchTool. Index name from settings: {settings.azure_ai_search_index_name}")
    ai_search = AzureAISearchTool(
        index_connection_id=conn_id,
        index_name=settings.azure_ai_search_index_name,
        query_type=AzureAISearchQueryType.SIMPLE,
        top_k=3,
        filter="",
    )

    agents_client = project_client.agents
    agent = agents_client.create_agent(
        model= "gpt-4o-mini", #os.environ["MODEL_DEPLOYMENT_NAME"],
        name="mini-agent-gpt4o",
        instructions="You are a helpful agent",
        tools=ai_search.definitions,
        tool_resources=ai_search.resources,
    )

    print(f"Created agent, ID: {agent.id}")

    thread = agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="which dogs are good for search and rescue? Give top 4 breeds and cite your sources.",
    )
    print(f"Created message, ID: {message.id}")

    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")
        

    # Fetch run steps to get the details of the agent run
    print("Fetching run steps...")
    run_steps = agents_client.run_steps.list(thread_id=thread.id, run_id=run.id)
    for step in run_steps:
        print(f"Step {step['id']} status: {step['status']}")
        step_details = step.get("step_details", {})
        tool_calls = step_details.get("tool_calls", [])

        if tool_calls:
            print("  Tool calls:")
            for call in tool_calls:
                print(f"    Tool Call ID: {call.get('id')}")
                print(f"    Type: {call.get('type')}")

                azure_ai_search_details = call.get("azure_ai_search", {})
                if azure_ai_search_details:
                    print(f"    azure_ai_search input: {azure_ai_search_details.get('input')}")
                    print(f"    azure_ai_search output: {azure_ai_search_details.get('output')}")
        print()  # add an extra newline between steps

        # Delete the agent when done
    agents_client.delete_agent(agent.id)
    print("Deleted agent")


    # [START populate_references_agent_with_azure_ai_search_tool]
    # Fetch and log all messages
    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for message in messages:
        if message.role == MessageRole.AGENT and message.url_citation_annotations:
            print("Agent message with citations:")
            placeholder_annotations = {
                annotation.text: f" [see {annotation.url_citation.title}] ({annotation.url_citation.url})"
                for annotation in message.url_citation_annotations
            }
            for message_text in message.text_messages:
                message_str = message_text.text.value
                for k, v in placeholder_annotations.items():
                    message_str = message_str.replace(k, v)
                print(f"{message.role}: {message_str}")
        else:
            print("Message without citations:")
            for message_text in message.text_messages:
                print(f"{message.role}: {message_text.text.value}")
    # [END populate_references_agent_with_azure_ai_search_tool]

    print("Done.") 
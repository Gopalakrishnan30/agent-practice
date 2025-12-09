import os
from azure.ai.projects import AIProjectClient
from azure.identity import ClientSecretCredential
from azure.ai.projects.models import AzureAISearchTool
from dotenv import load_dotenv

# --- NEW: Load environment variables from .env file ---
load_dotenv()

# ---------------------------------------------------------
# 1. Azure Credentials
# ---------------------------------------------------------
# For production: always store in ENV or KeyVault
credential = ClientSecretCredential(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET")
)

# ---------------------------------------------------------
# 2. Azure AI Project Endpoint
# ---------------------------------------------------------
PROJECT_ENDPOINT = os.getenv("AZURE_PROJECT_ENDPOINT")

project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=credential
)

print("✔ Connected to Azure AI Project via endpoint")

# ---------------------------------------------------------
# 3. Retrieve AI Search Connection ID Automatically
#
# ---------------------------------------------------------
print("Fetching connections...")
connections = project_client.connections._list_connections()["value"]

conn_id = None

for conn in connections:
    metadata = conn["properties"].get("metadata", {})
    if metadata.get("type", "").upper() == "AZURE_AI_SEARCH":
        conn_id = conn["id"]
        break

if not conn_id:
    raise Exception("❌ No Azure AI Search connection found in this project!")

print("✔ Detected Azure AI Search Connection ID:", conn_id)

# ---------------------------------------------------------
# 4. Configure AI Search Tool
# ---------------------------------------------------------
INDEX_NAME = "vector-1763641519710"   # your created index

# Create proper tool instance (recommended over manual dict)
ai_search_tool = AzureAISearchTool(
    index_connection_id=conn_id,
    index_name=INDEX_NAME
)

# ---------------------------------------------------------
# 5. Create Agent (TOOLS + TOOL_RESOURCES must match)
# ---------------------------------------------------------
agent = project_client.agents.create_agent(
    model="gpt-4o-mini",
    name="my-agent-aisearch",
    instructions="You are a helpful agent. Use Azure AI Search for RAG queries.",
    tools=ai_search_tool.definitions,          # required
    tool_resources=ai_search_tool.resources    # required
)

print("✔ Agent created:", agent.id)

# ---------------------------------------------------------
# 6. Create Conversation Thread
# ---------------------------------------------------------
thread = project_client.agents.create_thread()
print("✔ Thread created:", thread.id)

# ---------------------------------------------------------
# 7. Interactive Chat Loop
# ---------------------------------------------------------
print("\n🎤 Chat started — type 'end' to stop.\n")

while True:
    user_input = input("User: ")

    if user_input.lower().strip() == "end":
        project_client.agents.delete_agent(agent.id)
        print("✔ Agent deleted. Conversation ended.")
        break

    # Send user message
    project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    # Process run
    run = project_client.agents.create_and_process_run(
        thread_id=thread.id,
        agent_id=agent.id
    )

    if run.status == "failed":
        print("❌ Run failed:", run.last_error)
        break

    # Retrieve the latest response
    messages = project_client.agents.list_messages(thread_id=thread.id)
    reply = messages.data[0].content[0].text.value

    print("Agent:", reply)

print("Chat closed.")

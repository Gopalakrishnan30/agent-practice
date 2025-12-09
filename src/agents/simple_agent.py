import json
import os
from azure.ai.projects import AIProjectClient
from azure.identity import ClientSecretCredential
from dotenv import load_dotenv

# --- NEW: Load environment variables from .env file ---
load_dotenv()

# ---------------- AZURE CONFIGURATION ----------------
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP")
PROJECT_NAME = os.getenv("AZURE_PROJECT_NAME")

PROJECT_ENDPOINT = os.getenv("AZURE_PROJECT_ENDPOINT")
MODEL = "gpt-4o"

# ---------------- AUTHENTICATION ----------------
credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

# ---------------- PROJECT CLIENT ----------------
project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    subscription_id=SUBSCRIPTION_ID,
    resource_group_name=RESOURCE_GROUP,
    project_name=PROJECT_NAME,
    credential=credential
)

print("✓ Azure AI Project Client initialized successfully")

# ---------------- CREATE AGENT ----------------
agent = project_client.agents.create_agent(
    name="my-agent",
    model=MODEL,
    instructions="You are a helpful agent."
)

print(f"✓ Agent created: {agent.id}")

# ---------------- CREATE THREAD ----------------
thread = project_client.agents.threads.create()
print(f"✓ Thread created: {thread.id}")

# ---------------- SEND USER MESSAGE ----------------
project_client.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="Who is the PM of India?"
)

# ---------------- PROCESS AGENT RUN ----------------
run = project_client.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id
)

# ---------------- FETCH AND PRINT RESPONSE ----------------
messages = project_client.agents.messages.list(thread_id=thread.id)

print("\n--------- RESPONSE ---------")
for m in messages:
    # Extract text content from structured message
    text = ""
    for item in m.content:
        if item.get("type") == "text" and "text" in item and "value" in item["text"]:
            text += item["text"]["value"]
    if m.role == "assistant":
        print(text)
print("-----------------------------")

# ---------------- CLEANUP ----------------
project_client.agents.delete_agent(agent.id)
print("✓ Agent deleted successfully")

import os
import time
from azure.identity import ClientSecretCredential
from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv

# --- NEW: Load environment variables from .env file ---
load_dotenv()

# ====================== CONFIG ======================
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP")
PROJECT_NAME = os.getenv("AZURE_PROJECT_NAME")

PROJECT_ENDPOINT = os.getenv("AZURE_PROJECT_ENDPOINT")
MODEL = "gpt-4o"

# ====================== AUTH ======================
credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    subscription_id=SUBSCRIPTION_ID,
    resource_group_name=RESOURCE_GROUP,
    project_name=PROJECT_NAME,
    credential=credential
)

print("✅ Azure AI Project Client initialized successfully")

# ====================== AGENT ======================
agent = client.agents.create_agent(
    name="Sales Data Analysis Agent",
    model=MODEL,
    instructions="You can analyze CSV data, summarize insights, and generate visualizations using code interpreter."
)
print(f"✅ Agent created: {agent.id}")

# ====================== THREAD ======================
thread = client.agents.threads.create()
print(f"✅ Thread created: {thread.id}")

# ====================== READ CSV ======================
csv_file_path = os.path.join(os.getcwd(), "sales_data.csv")
if not os.path.exists(csv_file_path):
    raise FileNotFoundError(f"❌ File not found: {csv_file_path}")

with open(csv_file_path, "r") as f:
    csv_content = f.read()

# ====================== MAIN INTERACTIVE LOOP ======================
print("\n💬 You can now chat with your agent. Type 'exit' to quit.\n")

while True:
    user_input = input("🧑 You: ").strip()
    if user_input.lower() in ["exit", "quit"]:
        break

    # Combine user query with CSV content for the agent
    message_content = f"{user_input}\n\nCSV Data:\n{csv_content}"

    # Send message to agent
    client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=message_content
    )

    # Run the agent
    run = client.agents.runs.create_and_process(
        thread_id=thread.id, agent_id=agent.id)
    while True:
        time.sleep(3)
        status = client.agents.runs.get(
            thread_id=thread.id, run_id=run.id).status
        print(f"⏳ Run status: {status}")
        if status in ["completed", "failed", "cancelled"]:
            break

    if status != "completed":
        print(f"❌ Run ended with status: {status}")
        continue

    # Fetch and print assistant responses
    messages = client.agents.messages.list(thread_id=thread.id)
    print("\n📩 Assistant Responses:")
    for msg in messages:
        if msg.role == "assistant":
            text = ""
            for item in msg.content:
                if item.get("type") == "text":
                    text += item["text"]["value"]
            print("💬", text)
    print("—" * 50)

# ====================== CLEANUP ======================
client.agents.delete_agent(agent.id)
print(f"🧹 Agent deleted: {agent.id}")

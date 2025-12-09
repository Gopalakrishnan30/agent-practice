import os
import time
from azure.identity import ClientSecretCredential
from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv

# --- NEW: Load environment variables from .env file ---
load_dotenv()

# ================= CONFIG =================
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

PROJECT_ENDPOINT = os.getenv("AZURE_PROJECT_ENDPOINT")
FILE_PATH = "gpt-4-system-card.pdf"  # PDF/CSV/DOCX
AGENT_MODEL = "gpt-4o"
AGENT_NAME = "file-analysis-agent"

# ================= AUTHENTICATION =================
credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

project_client = AIProjectClient(
    credential=credential,
    endpoint=PROJECT_ENDPOINT
)
print(f"✅ AIProjectClient initialized for endpoint: {PROJECT_ENDPOINT}")

# ================= CREATE AGENT =================
agent = project_client.agents.create_agent(
    model=AGENT_MODEL,
    name=AGENT_NAME,
    instructions=(
        "You are an assistant that analyzes uploaded files. "
        "Answer questions strictly based on the uploaded file."
    )
)
print(f"✅ Agent created: {agent.id}")

# ================= CREATE THREAD =================
thread = project_client.agents.threads.create()
print(f"✅ Thread created: {thread.id}")

# ================= UPLOAD FILE =================
try:
    with open(FILE_PATH, "rb") as f:
        uploaded_file = project_client.files.create(
            name=os.path.basename(FILE_PATH),
            file=f,
            purpose="assistants"  # this is required
        )
    print(f"✅ Uploaded file, file ID: {uploaded_file.id}")
except FileNotFoundError:
    print(f"❌ File not found: {FILE_PATH}")
    exit(1)
except Exception as e:
    print(f"❌ ERROR during file upload: {e}")
    exit(1)

# ================= INTERACTIVE LOOP =================
try:
    while True:
        user_input = input("User: ").strip()
        if user_input.lower() in ["exit", "quit", "end"]:
            print("Ending the conversation.")
            break

        # Send user message with reference to uploaded file
        project_client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input,
            attachments=[{"file_id": uploaded_file.id}]
        )

        # Run the agent
        run = project_client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id
        )

        if run.status == "failed":
            print(
                f"❌ Run failed: {run.last_error.code}: {run.last_error.message}")
            continue

        # Wait to ensure messages are written
        time.sleep(1)

        # Fetch messages
        messages = list(
            project_client.agents.messages.list(thread_id=thread.id))
        latest_msg = None
        for msg in reversed(messages):
            if msg.role == "assistant" and msg.content:
                latest_msg = msg
                break

        if latest_msg:
            print(f"Agent: {latest_msg.content[0].text.value}")
        else:
            print("Agent: No valid response received.")

finally:
    # ================= CLEANUP =================
    print("\n--- Cleanup ---")
    try:
        project_client.agents.delete_agent(agent.id)
        print("🗑️ Deleted agent")
    except Exception:
        pass

    try:
        project_client.files.delete(uploaded_file.id)
        print("🗑️ Deleted uploaded file")
    except Exception:
        pass

# JSON File schema is already created by tself.

from azure.identity import ClientSecretCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder
from azure.ai.agents.models import (
    OpenApiTool,
    OpenApiConnectionAuthDetails,
    OpenApiConnectionSecurityScheme
)
import jsonref
import asyncio
from pathlib import Path

# Azure AI Project Configuration
import os
from dotenv import load_dotenv
load_dotenv('.env')
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
PROJECT_ENDPOINT = os.getenv("AZURE_PROJECT_ENDPOINT")

# Connection configuration
OPENAPI_SCHEMA_FILE = "./tripadvisor_api_schema.json"
# Enter your CONNECTED RESOURCE name here
connection_name = "Tripadvisor-connector"

# Initializing connection to Azure using client credentials.


def _initialize_azure_client():
    """Initialize Azure AI Project client"""
    credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )

    project_client = AIProjectClient(
        credential=credential,
        endpoint=PROJECT_ENDPOINT
    )
    return project_client

# Loads OpenAPI Schema


def load_openapi_schema():
    """Load OpenAPI schema from JSON file"""
    with open(OPENAPI_SCHEMA_FILE, 'r', encoding='utf-8') as f:
        return jsonref.loads(f.read())

# Creates a tool that the AI agent can use to call the TripAdvisor API


def create_openapi_tool(connection_id: str):
    """Create OpenAPI tool with connected resource authentication"""
    openapi_spec = load_openapi_schema()

    auth = OpenApiConnectionAuthDetails(
        security_scheme=OpenApiConnectionSecurityScheme(
            connection_id=connection_id
        )
    )

    api_title = openapi_spec.get('info', {}).get('title', 'TripAdvisor API')

    return OpenApiTool(
        name="tripadvisor_api",
        spec=openapi_spec,
        description=f"{api_title} for travel content and recommendations",
        auth=auth
    )


# Creates the actual AI agent with TripAdvisor capabilities
def create_travel_agent(project_client):
    """Create Azure AI Agent with TripAdvisor OpenAPI tool"""
    conn_list = project_client.connections.list()
    connection_id = [conn["id"]
                     for conn in conn_list if conn.get("name") == connection_name][0]
    openapi_tool = create_openapi_tool(connection_id)

    instructions = """You are a travel assistant with direct access to the TripAdvisor API.

Use the tripadvisor_api tool to search for locations, hotels, restaurants, and attractions.
Get detailed information including ratings, reviews, and descriptions.
Provide real-time travel recommendations with specific details like ratings, addresses, and contact info."""

    agent = project_client.agents.create_agent(
        model="gpt-4o-mini",
        name="TripAdvisor-API-Assistant",
        description="Travel assistant with TripAdvisor API access",
        instructions=instructions,
        temperature=0.7,
        tools=openapi_tool.definitions
    )

    return agent


# Creates a conversation thread to maintain chat history
def create_conversation_thread():
    """Create conversation thread"""
    thread = project_client.agents.threads.create()
    return thread

# Handles the core conversation logic


def process_conversation(user_message: str) -> str:
    """Process user message and return response"""
    project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )

    run = project_client.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id
    )

    if run.status == "completed":
        messages = project_client.agents.messages.list(
            thread_id=thread.id,
            order=ListSortOrder.DESCENDING,
            limit=1
        )

        for message in messages:
            if message.role == "assistant" and hasattr(message, 'text_messages') and message.text_messages:
                return message.text_messages[-1].text.value

    return "Please try again."

# Cleans up resources when the program ends


def cleanup():
    """Clean up resources"""
    if thread:
        project_client.agents.threads.delete(thread.id)


"""Main execution"""
project_client = _initialize_azure_client()
agent = create_travel_agent(project_client)
thread = create_conversation_thread()

print("TripAdvisor Assistant Ready!")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ["exit", "quit"]:
        break

    if user_input:
        response = process_conversation(user_input)
        print(f"Assistant: {response}\n")

cleanup()

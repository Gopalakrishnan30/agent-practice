import os
import json
import time
import requests
from typing import Any, Callable, Set

from dotenv import load_dotenv

from azure.ai.projects import AIProjectClient
from azure.identity import ClientSecretCredential
from azure.ai.agents.models import FunctionTool  # <-- IMPORTANT

# ----------------------------------------------------------------------
# Load environment variables
# ----------------------------------------------------------------------
load_dotenv()

# ----------------------------------------------------------------------
# 1. Freshdesk function that the Agent can call
# ----------------------------------------------------------------------
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")


def create_freshdesk_ticket(Email: str, Subject: str) -> str:
    """
    Creates a ticket in Freshdesk.

    :param Email: Email address of the requester.
    :param Subject: Subject line for the ticket.
    :return: JSON string with Freshdesk ticket details or error info.
    """

    FRESHDESK_DOMAIN = os.getenv("FRESHDESK_DOMAIN")
    FRESHDESK_API_KEY = os.getenv("FRESHDESK_API_KEY")

    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets"

    ticket_data = {
        "email": Email,
        "subject": Subject,
        "description": "This ticket was created via Azure AI Agent.",
        "priority": 2,
        "status": 2,
        "tags": ["AI-Agent", "Automation"]
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.post(
        url,
        auth=(FRESHDESK_API_KEY, "X"),
        headers=headers,
        data=json.dumps(ticket_data),
    )

    if response.status_code == 201:
        return json.dumps(response.json(), indent=4)

    return json.dumps(
        {"status_code": response.status_code, "error": response.text},
        indent=4
    )


# The set of user-defined functions to expose as tools
user_functions: Set[Callable[..., Any]] = {create_freshdesk_ticket}


# ----------------------------------------------------------------------
# 2. Main – Azure AI Project + Agent setup
# ----------------------------------------------------------------------
if __name__ == "__main__":

    # ---------------------------------------------------------------
    # Azure Entra ID credentials (your values)
    # ---------------------------------------------------------------
    credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )

    PROJECT_ENDPOINT = (
        os.getenv("AZURE_PROJECT_ENDPOINT")
    )

    # Create AIProjectClient
    project_client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=credential,
    )

    print("✔ Connected to Azure AI Project")

    # ---------------------------------------------------------------
    # Build tools using FunctionTool (correct for 1.0.0)
    # This generates the correct `tools[0].function` structure.
    # ---------------------------------------------------------------
    functions_tool = FunctionTool(functions=user_functions)

    # ---------------------------------------------------------------
    # Create Agent
    # ---------------------------------------------------------------
    agent = project_client.agents.create_agent(
        model="gpt-4o-mini",
        name="freshdesk-agent",
        instructions=(
            "You are a helpful support assistant. "
            "When the user needs help, decide whether to create a Freshdesk ticket "
            "by calling the 'create_freshdesk_ticket' function."
        ),
        tools=functions_tool.definitions,  # <-- CRITICAL
        # No tool_resources needed for pure function tools
    )

    print(f"✔ Agent created. ID: {agent.id}")

    # ---------------------------------------------------------------
    # Create a thread (conversation context)
    # ---------------------------------------------------------------
    thread = project_client.agents.threads.create()
    print(f"✔ Thread created. ID: {thread.id}")

    print("\n💬 Chat started. Type 'end' to exit.\n")

    # ------------------------------------------------------------------
    # 3. Interactive loop: send message → run agent → handle function calls
    # ------------------------------------------------------------------
    while True:
        user_input = input("User: ").strip()
        if user_input.lower() == "end":
            print("Ending conversation...")
            break

        # 1) Send user message
        message = project_client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input,
        )

        # 2) Create a run
        run = project_client.agents.runs.create(
            thread_id=thread.id,
            agent_id=agent.id,
        )

        # 3) Poll until run is completed or requires_action
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = project_client.agents.runs.get(
                thread_id=thread.id,
                run_id=run.id,
            )

            # ------------------------------------------------------
            # If the run requires tool outputs (function calls)
            # ------------------------------------------------------
            if run.status == "requires_action" and run.required_action:
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []

                for tool_call in tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(
                        tool_call.function.arguments or "{}")

                    print(f"\n🔧 Tool call requested: {func_name}")
                    print(f"   Arguments: {func_args}")

                    if func_name == "create_freshdesk_ticket":
                        result = create_freshdesk_ticket(
                            Email=func_args.get("Email", ""),
                            Subject=func_args.get("Subject", ""),
                        )
                    else:
                        # Unknown tool – safely return error back
                        result = json.dumps(
                            {"error": f"Unknown tool {func_name}"},
                            indent=4
                        )

                    tool_outputs.append(
                        {
                            "tool_call_id": tool_call.id,
                            "output": result,
                        }
                    )

                # Submit tool outputs so agent can continue
                run = project_client.agents.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs,
                )

        print(f"↪ Run finished with status: {run.status}")

        # 4) Retrieve all messages and print the last assistant response
        messages = list(
            project_client.agents.messages.list(thread_id=thread.id))
        # Find the latest assistant message
        assistant_msg = next(
            (m for m in reversed(messages) if m["role"] == "assistant"),
            None
        )

        if assistant_msg:
            # assistant_msg["content"] is a list; each item has {"type": "output_text", "text": {"value": "..."}}
            parts = assistant_msg["content"]
            if parts and parts[0]["type"] == "output_text":
                text_value = parts[0]["text"]["value"]
                print(f"\nAgent: {text_value}\n")
            else:
                print(f"\nAgent (raw message): {assistant_msg}\n")
        else:
            print("\n(Agent did not send a reply.)\n")

    # ------------------------------------------------------------------
    # 4. Cleanup (optional)
    # ------------------------------------------------------------------
    project_client.agents.delete_agent(agent.id)
    print("✔ Agent deleted. Session closed.")

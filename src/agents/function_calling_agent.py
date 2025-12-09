import json
import os
import requests
from azure.identity import ClientSecretCredential
from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv

# --- NEW: Load environment variables from .env file ---
load_dotenv()

# ---------------- AZURE & WEATHER CONFIGURATION ----------------
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")


SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP")
PROJECT_NAME = os.getenv("AZURE_PROJECT_NAME")

PROJECT_ENDPOINT = os.getenv("AZURE_PROJECT_ENDPOINT")

# OpenWeatherMap API key
OPENWEATHER_MAP_API_KEY = os.getenv("OPENWEATHER_MAP_API_KEY")

# ---------------- AUTHENTICATION ----------------
credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

# ---------------- AZURE AI PROJECT CLIENT ----------------
try:
    client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        subscription_id=SUBSCRIPTION_ID,
        resource_group_name=RESOURCE_GROUP,
        project_name=PROJECT_NAME,
        credential=credential
    )
    print("✅ Azure AI Project Client created successfully")
except Exception as e:
    print("❌ Failed to create Azure AI Project Client:", e)
    exit(1)

# ---------------- WEATHER FUNCTION ----------------


def get_weather(latitude: float, longitude: float) -> dict:
    """Fetch current weather for given latitude and longitude."""
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={latitude}&lon={longitude}&appid={OPENWEATHER_MAP_API_KEY}&units=metric"
    )
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            return {"error": data.get("message", "API error")}
        return {
            "latitude": data["coord"]["lat"],
            "longitude": data["coord"]["lon"],
            "weather_condition": data["weather"][0]["description"],
            "temperature": data["main"]["temp"],
            "city": data.get("name", "Unknown")
        }
    except Exception as e:
        return {"error": str(e)}

# ---------------- MAIN EXECUTION ----------------


def main():
    try:
        # Create agent
        agent = client.agents.create_agent(
            model="gpt-4o",
            name="weather-agent",
            instructions="You provide helpful weather information to the user."
        )
        print(f"🤖 Agent created: {agent.id}")

        # Create conversation thread
        thread = client.agents.threads.create()
        print(f"🧵 Thread created: {thread.id}")

        while True:
            user_input = input("User: ")
            if user_input.lower() == "end":
                print("Exiting conversation...")
                break

            # Send user message
            client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_input
            )

            # Weather trigger
            if "weather" in user_input.lower():
                # Example: London coordinates
                weather_info = get_weather(latitude=51.5074, longitude=-0.1278)
                client.agents.messages.create(
                    thread_id=thread.id,
                    role="assistant",
                    content=f"Weather info:\n{json.dumps(weather_info, indent=4)}"
                )

            # Print full conversation
            messages = client.agents.messages.list(thread_id=thread.id)
            print("\n🪶 Conversation:")
            for msg in messages.data:
                print(f"{msg.role.capitalize()}: {msg.content}")

    except Exception as e:
        print("❌ Error occurred:", e)

    finally:
        # Delete agent to clean up resources
        if 'agent' in locals():
            client.agents.delete_agent(agent.id)
            print("🧹 Agent deleted.")


# ---------------- RUN SCRIPT ----------------
if __name__ == "__main__":
    main()

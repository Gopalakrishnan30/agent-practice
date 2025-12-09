# Import dependencies
# Import List and Optional types for type hinting
from typing import List, Optional
# Import agent classes and orchestration
from semantic_kernel.agents import Agent, ChatCompletionAgent, SequentialOrchestration
# Import Azure OpenAI connector
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
# Import message content class for agent responses
from semantic_kernel.contents import ChatMessageContent
# Import runtime for agent execution
from semantic_kernel.agents.runtime import InProcessRuntime
import os  # Import os for environment variable access
import asyncio  # Import asyncio for asynchronous programming
# Import dotenv to load environment variables from .env file
from dotenv import load_dotenv


# Load environment variables from .env file into the environment
load_dotenv()

# Azure OpenAI Configuration - Replace with your Azure credentials
# Get API key from environment
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
# Get endpoint URL from environment
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# Get deployment name from environment
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
# Get API version from environment
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Debug function to test connection


async def test_azure_connection():
    """Test Azure OpenAI connection before running orchestration"""
    try:
        ai_service = AzureChatCompletion(
            api_key=AZURE_OPENAI_API_KEY,  # Use loaded API key
            endpoint=AZURE_OPENAI_ENDPOINT,  # Use loaded endpoint
            deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME,  # Use loaded deployment name
            api_version=AZURE_OPENAI_API_VERSION  # Use loaded API version
        )

        # Simple test prompt
        test_agent = ChatCompletionAgent(
            name="TestAgent",  # Name for the test agent
            # Simple instruction
            instructions="You are a test agent. Respond with 'Connection successful!'",
            service=ai_service,  # Use the AzureChatCompletion service
        )

        print("🔍 Testing Azure OpenAI connection...")  # Notify user of test

        # This will fail if connection is bad
        return True  # If no exception, connection is successful

    except Exception as e:
        print(f"❌ Connection test failed: {e}")  # Print error message
        print("\n🔧 Common fixes:")  # Print troubleshooting tips
        print("1. Check your endpoint URL (should end with /)")
        print("2. Verify your API key is correct")
        print("3. Ensure deployment name matches exactly")
        print("4. Try API version: '2023-12-01-preview'")
        print("5. Check if your Azure resource is active")
        return False  # Return False if connection fails

# Function to get the agents


def get_social_media_agents() -> List[Agent]:
    """
    Define three agents for social media post optimization:
    1. AnalyzerAgent: Analyzes the original post for tone, engagement factors, and issues
    2. OptimizerAgent: Creates an improved version based on the analysis
    3. ReviewerAgent: Final review and polish for maximum engagement
    """

    # Initialize the Azure OpenAI service
    ai_service = AzureChatCompletion(
        api_key=AZURE_OPENAI_API_KEY,  # Use API key from environment
        endpoint=AZURE_OPENAI_ENDPOINT,  # Use endpoint from environment
        # Use deployment name from environment
        deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME,
        api_version=AZURE_OPENAI_API_VERSION  # Use API version from environment
    )

    # Agent 1 - Analyzer Agent
    analyzer_agent = ChatCompletionAgent(
        name="AnalyzerAgent",  # Name of the agent
        instructions=(
            "You are a social media analyst. Given a social media post, analyze and identify:\n"
            "- Current tone and style\n"
            "- Engagement potential (hashtags, call-to-action, emotional appeal)\n"
            "- Target audience\n"
            "- Areas for improvement\n"
            "- Missing elements (emojis, hashtags, etc.)\n\n"
            "Provide a structured analysis with specific recommendations."
        ),  # Instructions for analysis
        service=ai_service,
    )

    # Agent 2 - Optimizer Agent
    optimizer_agent = ChatCompletionAgent(
        name="OptimizerAgent",  # Name of the agent
        instructions=(
            "You are a social media content optimizer. Based on the analysis provided, "
            "create an improved version of the original social media post that:\n"
            "- Enhances engagement potential\n"
            "- Improves clarity and impact\n"
            "- Adds appropriate hashtags and emojis\n"
            "- Includes a clear call-to-action\n"
            "- Maintains authenticity\n\n"
            "Output only the optimized post content."
        ),  # Instructions for optimization
        service=ai_service,
    )

    # Agent 3 - Teviewer Agent
    reviewer_agent = ChatCompletionAgent(
        name="ReviewerAgent",  # Name of the agent
        instructions=(
            "You are a social media content reviewer. Review the optimized post and make final improvements:\n"
            "- Ensure perfect grammar and spelling\n"
            "- Optimize hashtag placement and relevance\n"
            "- Balance emoji usage (not too many, not too few)\n"
            "- Ensure the call-to-action is compelling\n"
            "- Make sure the post fits platform character limits\n\n"
            "Output the final, polished social media post."
        ),  # Instructions for review and polish
        service=ai_service,
    )

    # Return the list of agents
    return [analyzer_agent, optimizer_agent, reviewer_agent]

# Function to print agent's response callback


def agent_response_callback(message: ChatMessageContent) -> None:
    """Callback function to observe agent responses"""
    print(f"\n{'='*50}")  # Print separator
    print(f"🤖 {message.name}")  # Print agent name
    print(f"{'='*50}")  # Print separator
    print(message.content)  # Print agent's message content
    print()  # Print empty line

# Alternative example Function with a business post to run the multi agent squential orchestration for social media post optimization


async def run_business_post_example():
    """Example with a business-focused social media post"""

    agents = get_social_media_agents()  # Get the list of agents
    sequential_orchestration = SequentialOrchestration(
        members=agents,  # Pass agents as members of the orchestration
        # Set callback for agent responses
        agent_response_callback=agent_response_callback,
    )

    runtime = InProcessRuntime()  # Create a runtime for agent execution
    runtime.start()  # Start the runtime

    business_post = """
    Hi Folks, I am launching a new Beginners to Pro Course on Udemy on 
    Model Context Protocol MCP across the AI Ecosystem covering
    AI Frameworks and Models
    """  # Example business post to optimize

    print(f"📝 Original Business Post:")  # Print header
    print(f"{'-'*35}")  # Print separator
    print(business_post.strip())  # Print the original post
    print(f"{'-'*35}\n")  # Print separator

    try:
        orchestration_result = await sequential_orchestration.invoke(
            task=business_post,  # Pass the business post as the task
            runtime=runtime,  # Use the created runtime
        )

        # Wait for the result with a timeout
        final_result = await orchestration_result.get(timeout=60)

        # Print header for final result
        print("🎉 FINAL OPTIMIZED BUSINESS POST")
        print("="*55)  # Print separator
        print(final_result)  # Print the optimized post
        print("="*55)  # Print separator

    except Exception as e:
        # Print error if orchestration fails
        print(f"❌ Error during orchestration: {e}")

    finally:
        await runtime.stop_when_idle()  # Stop the runtime when idle


# Main function
async def main():
    """Main function to run the examples"""
    print("🎯 Social Media Post Optimization with Sequential Agents")  # Print title
    print("="*60)  # Print separator
    # Reminder to set config
    print("⚠️  Remember to set your Azure OpenAI configuration values!")
    print("="*60)  # Print separator

    # Check if API key is set
    if AZURE_OPENAI_API_KEY == "your-azure-openai-api-key":
        # Warn if API key is not set
        print("❌ Please set your Azure OpenAI configuration before running!")
        return

    # Test connection first
    connection_ok = await test_azure_connection()  # Test Azure connection
    if not connection_ok:
        # Warn if connection fails
        print("❌ Connection test failed. Please fix configuration before proceeding.")
        return

    print("✅ Connection test passed!\n")  # Notify if connection is successful

    # Run the business post example
    # Print which example is running
    print("💼 Example 2: Business Post Optimization")
    await run_business_post_example()  # Run the business post optimization

    print("\n" + "="*80 + "\n")  # Print final separator


# Execute everything
if __name__ == "__main__":
    # Run the main function asynchronously if script is executed directly
    asyncio.run(main())

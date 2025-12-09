# 🤖 Azure AI Agent Toolkit

A comprehensive Python toolkit for building intelligent AI agents using Azure AI Services, featuring RAG capabilities, multi-agent orchestration, and enterprise integrations.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Azure](https://img.shields.io/badge/azure-AI%20Services-0078D4)

## 📋 Overview

Azure AI Agent Toolkit provides a production-ready framework for building sophisticated AI agents with:

- **🔍 RAG (Retrieval Augmented Generation)** - Integration with Azure AI Search for knowledge-based responses
- **🛠️ Function Calling** - Custom tools and external API integrations
- **📊 Code Interpreter** - Execute Python code and analyze data
- **🔗 Multi-Agent Orchestration** - Sequential workflows with Semantic Kernel
- **🎫 Enterprise Integrations** - Freshdesk, TripAdvisor, Email, and more
- **🔐 Secure by Design** - Environment-based configuration management

## ✨ Features

### Core Agent Types

1. **Simple Chat Agent** - Basic conversational AI
2. **Code Interpreter Agent** - Execute code and analyze CSV data
3. **RAG Agent** - Knowledge retrieval with Azure AI Search
4. **Function Calling Agent** - Weather, API calls, custom tools
5. **File Search Agent** - PDF/Document analysis
6. **Multi-Agent System** - Sequential orchestration workflows

### Integrations

- ✅ Freshdesk ticket creation
- ✅ TripAdvisor API for travel recommendations
- ✅ Email sending via Azure Logic Apps
- ✅ OpenAPI/Swagger integration support

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Azure subscription with AI Services
- Azure AI Project created

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/azure-ai-agent-toolkit.git
cd azure-ai-agent-toolkit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your Azure credentials
nano .env
```

### Basic Usage

```python
from src.utils.azure_client import AzureClientManager

# Initialize agent
manager = AzureClientManager()
client = manager.initialize()

# Start chatting
agent = client.agents.create_agent(
    model="gpt-4o",
    name="my-agent",
    instructions="You are a helpful assistant."
)
```

## 📸 Screenshots

### Agent Conversation
![Agent Chat](./assets/screenshots/agent_chat.png)

### RAG Implementation
![RAG Search](./assets/screenshots/rag_search.png)

### Multi-Agent Orchestration
![Multi-Agent](./assets/screenshots/multi_agent.png)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Application                      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Azure AI Agent Framework                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐     │
│  │  Agents  │  │  Tools   │  │  Orchestration   │     │
│  └──────────┘  └──────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │  GPT-4   │  │ AI Search│  │  APIs    │
    │  Models  │  │   RAG    │  │ External │
    └──────────┘  └──────────┘  └──────────┘
```

## 📚 Documentation

- [Setup Guide](./docs/setup_guide.md)
- [Architecture](./docs/architecture.md)
- [API Reference](./docs/api_reference.md)
- [Examples](./docs/examples.md)

## 🛣️ Roadmap

### Phase 1 (Current)
- [x] Basic agent implementations
- [x] RAG with Azure AI Search
- [x] Function calling framework
- [x] Multi-agent orchestration

### Phase 2 (Q1 2025)
- [ ] Streaming responses
- [ ] Agent memory persistence
- [ ] Advanced tool chaining
- [ ] Web UI dashboard

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md).

## 📄 License

This project is licensed under the MIT License - see [LICENSE](./LICENSE).

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

Made with ❤️ for the Azure AI community

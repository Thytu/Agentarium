# 🌿 Agentarium

<div align="center">

[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-yellow.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/agentarium.svg)](https://badge.fury.io/py/agentarium)

A powerful Python framework for managing and orchestrating AI agents with ease. Agentarium provides a flexible and intuitive way to create, manage, and coordinate interactions between multiple AI agents in various environments.

[Installation](#installation) •
[Quick Start](#quick-start) •
[Features](#features) •
[Examples](#examples) •
[Documentation](#documentation) •
[Contributing](#contributing)

</div>

## 🚀 Installation

```bash
pip install agentarium
```

## 🎯 Quick Start

```python
from agentarium import Agent

# Create agents
agent1 = Agent(name="agent1")
agent2 = Agent(name="agent2")

# Direct communication between agents
alice.talk_to(bob, "Hello Bob! I heard you're working on some interesting ML projects.")

# Agent autonomously decides its next action based on context
bob.act()
```

## ✨ Features

- **🤖 Advanced Agent Management**: Create and orchestrate multiple AI agents with different roles and capabilities
- **🔄 Autonomous Decision Making**: Agents can make decisions and take actions based on their context
- **💾 Checkpoint System**: Save and restore agent states and interactions for reproducibility
- **🎭 Customizable Actions**: Define custom actions beyond the default talk/think capabilities
- **🧠 Memory & Context**: Agents maintain memory of past interactions for contextual responses
- **⚡ AI Integration**: Seamless integration with various AI providers through aisuite
- **⚡ Performance Optimized**: Built for efficiency and scalability
- **🛠️ Extensible Architecture**: Easy to extend and customize for your specific needs

## 📚 Examples

### Basic Chat Example
Create a simple chat interaction between agents:

```python
from agentarium import Agent

# Create agents with specific characteristics
alice = Agent.create_agent(name="Alice", occupation="Software Engineer")
bob = Agent.create_agent(name="Bob", occupation="Data Scientist")

# Direct communication
alice.talk_to(bob, "Hello Bob! I heard you're working on some interesting projects.")

# Let Bob autonomously decide how to respond
bob.act()
```

### Adding Custom Actions
Add new capabilities to your agents:

```python
from agentarium import Agent, Action

# Define a simple greeting action
def greet(name: str, **kwargs) -> str:
    return f"Hello, {name}!"

# Create an agent and add the greeting action
agent = Agent.create_agent(name="Alice")
agent.add_action(
    Action(
        name="GREET",
        description="Greet someone by name",
        parameters=["name"],
        function=greet
    )
)

# Use the custom action
agent.execute_action("GREET", "Bob")
```

### Using Checkpoints
Save and restore agent states:

```python
from agentarium import Agent
from agentarium.CheckpointManager import CheckpointManager

# Initialize checkpoint manager
checkpoint = CheckpointManager("demo")

# Create and interact with agents
alice = Agent.create_agent(name="Alice")
bob = Agent.create_agent(name="Bob")

alice.talk_to(bob, "What a beautiful day!")
checkpoint.update(step="interaction_1")

# Save the current state
checkpoint.save()
```

More examples can be found in the [examples/](examples/) directory.

## 📖 Documentation

### Agent Creation
Create agents with custom characteristics:

```python
agent = Agent.create_agent(
    name="Alice",
    age=28,
    occupation="Software Engineer",
    location="San Francisco",
    bio="A passionate developer who loves AI"
)
```

### LLM Configuration
Configure your LLM provider and credentials using a YAML file:

```yaml
llm:
  provider: "openai"  # The LLM provider to use (any provider supported by aisuite)
  model: "gpt-4"      # The specific model to use from the provider

aisuite:              # (optional) Credentials for aisuite
  openai:            # Provider-specific configuration
    api_key: "sk-..."  # Your API key
```

### Key Components

- **Agent**: Core class for creating AI agents with personalities and autonomous behavior
- **CheckpointManager**: Handles saving and loading of agent states and interactions
- **Action**: Base class for defining custom agent actions
- **AgentInteractionManager**: Manages and tracks all agent interactions

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'feat: add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Thanks to all contributors who have helped shape Agentarium 🫶


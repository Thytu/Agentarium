import os
import pytest

from agentarium import Agent
from agentarium.CheckpointManager import CheckpointManager
from agentarium.AgentInteractionManager import AgentInteractionManager


@pytest.fixture(autouse=True)
def cleanup_checkpoint_files():
    """Automatically clean up any checkpoint files after each test."""
    yield
    # Clean up any .dill files in the current directory
    for file in os.listdir():
        if file.endswith('.dill'):
            os.remove(file)


@pytest.fixture
def base_agent():
    """Create a basic agent for testing."""
    agent = Agent.create_agent(
        name="TestAgent",
        age=25,
        occupation="Software Engineer",
        location="Test City",
        bio="A test agent"
    )
    yield agent
    # Reset the agent after each test that uses this fixture
    agent.reset()


@pytest.fixture
def interaction_manager():
    """Create a fresh interaction manager for testing."""
    return AgentInteractionManager()


@pytest.fixture
def checkpoint_manager():
    """Create a test checkpoint manager."""
    manager = CheckpointManager("test_checkpoint")
    yield manager
    # Cleanup is handled by cleanup_checkpoint_files fixture


@pytest.fixture
def agent_pair():
    """Create a pair of agents for interaction testing."""
    alice = Agent.create_agent(name="Alice", bio="Alice is a test agent")
    bob = Agent.create_agent(name="Bob", bio="Bob is a test agent")
    yield alice, bob
    # Reset both agents after each test that uses this fixture
    alice.reset()
    bob.reset()

import pytest

from agentarium import Agent, Action
from agentarium.constant import DefaultValue


def test_agent_creation():
    """Test basic agent creation with default and custom values."""
    # Test with default values
    agent = Agent.create_agent(bio="A test agent") # prevents the LLM from generating a bio
    assert agent.agent_id is not None
    assert agent.name is not None
    assert agent.age is not None
    assert agent.occupation is not None
    assert agent.location is not None
    assert agent.bio is not None

    # Test with custom values
    custom_agent = Agent.create_agent(
        name="Alice",
        age=25,
        occupation="Software Engineer",
        location="San Francisco",
        bio="A passionate software engineer"
    )
    assert custom_agent.name == "Alice"
    assert custom_agent.age == 25
    assert custom_agent.occupation == "Software Engineer"
    assert custom_agent.location == "San Francisco"
    assert custom_agent.bio == "A passionate software engineer"


def test_agent_default_actions():
    """Test that agents are created with default actions."""
    agent = Agent.create_agent()
    assert "talk" in agent._actions
    assert "think" in agent._actions


def test_agent_custom_actions():
    """Test adding and using custom actions."""
    def custom_action(*args, **kwargs):
        agent = kwargs["agent"]
        return {"message": f"Custom action by {agent.name}"}

    custom_action_obj = Action(
        name="custom",
        description="A custom action",
        parameters=["message"],
        function=custom_action
    )

    agent = Agent.create_agent(name="Bob", bio="A test agent")
    agent.add_action(custom_action_obj)

    assert "custom" in agent._actions
    result = agent.execute_action("custom", "test message")
    assert result["action"] == "custom"
    assert "message" in result


def test_agent_interaction():
    """Test basic interaction between agents."""
    alice = Agent.create_agent(name="Alice")
    bob = Agent.create_agent(name="Bob")

    message = "Hello Bob!"
    alice.talk_to(bob, message)

    # Check Alice's interactions
    alice_interactions = alice.get_interactions()
    assert len(alice_interactions) == 1
    assert alice_interactions[0].sender == alice
    assert alice_interactions[0].receiver == bob
    assert alice_interactions[0].message == message

    # Check Bob's interactions
    bob_interactions = bob.get_interactions()
    assert len(bob_interactions) == 1
    assert bob_interactions[0].sender == alice
    assert bob_interactions[0].receiver == bob
    assert bob_interactions[0].message == message


def test_agent_think():
    """Test agent's ability to think."""
    agent = Agent.create_agent(name="Alice")
    thought = "I should learn more about AI"

    agent.think(thought)

    interactions = agent.get_interactions()
    assert len(interactions) == 1
    assert interactions[0].sender == agent
    assert interactions[0].receiver == agent
    assert interactions[0].message == thought


def test_invalid_action():
    """Test handling of invalid actions."""
    agent = Agent.create_agent()

    with pytest.raises(RuntimeError):
        agent.execute_action("nonexistent_action", "test")


def test_agent_reset():
    """Test resetting agent state."""
    agent = Agent.create_agent()
    agent.think("Initial thought")

    assert len(agent.get_interactions()) == 1

    agent.reset()
    assert len(agent.get_interactions()) == 0
    assert len(agent.storage) == 0

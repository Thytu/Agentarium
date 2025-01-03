import pytest

from agentarium import Agent, Action
from agentarium.constant import DefaultValue


def test_agent_creation(base_agent):
    """Test basic agent creation with default and custom values."""
    # Test with default values
    assert base_agent.agent_id is not None
    assert base_agent.name is not None
    assert base_agent.age is not None
    assert base_agent.occupation is not None
    assert base_agent.location is not None
    assert base_agent.bio is not None

    # Test without default values (nor bio)
    custom_agent = Agent.create_agent(
        name="Alice",
        age=25,
        occupation="Software Engineer",
        location="San Francisco",
    )
    assert isinstance(custom_agent.name, str)
    assert isinstance(custom_agent.age, int)
    assert isinstance(custom_agent.occupation, str)
    assert isinstance(custom_agent.location, str)
    assert isinstance(custom_agent.bio, str)


def test_agent_default_actions(agent_pair):
    """Test that agents are created with default actions."""
    alice, _ = agent_pair
    assert "talk" in alice._actions
    assert "think" in alice._actions


def test_agent_custom_actions(base_agent):
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

    base_agent.add_action(custom_action_obj)

    assert "custom" in base_agent._actions
    result = base_agent.execute_action("custom", "test message")
    assert result["action"] == "custom"
    assert "message" in result


def test_agent_interaction(agent_pair):
    """Test basic interaction between agents."""

    alice, bob = agent_pair

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


def test_agent_think(agent_pair):
    """Test agent's ability to think."""

    agent, _ = agent_pair
    thought = "I should learn more about AI"

    agent.think(thought)

    interactions = agent.get_interactions()
    assert len(interactions) == 1
    assert interactions[0].sender == agent
    assert interactions[0].receiver == agent
    assert interactions[0].message == thought


def test_invalid_action(base_agent):
    """Test handling of invalid actions."""

    with pytest.raises(RuntimeError):
        base_agent.execute_action("nonexistent_action", "test")


def test_agent_reset(base_agent):
    """Test resetting agent state."""
    base_agent.think("Initial thought")

    assert len(base_agent.get_interactions()) == 1

    base_agent.reset()
    assert len(base_agent.get_interactions()) == 0
    assert len(base_agent.storage) == 0

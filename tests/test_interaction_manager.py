import pytest

from agentarium.Agent import Agent
from agentarium.AgentInteractionManager import AgentInteractionManager

@pytest.fixture
def interaction_manager():
    """Create a test interaction manager."""
    return AgentInteractionManager()


def test_agent_registration(interaction_manager, agent_pair):
    """Test registering agents with the interaction manager."""
    alice, bob = agent_pair

    # Verify agents are registered
    assert alice.agent_id in interaction_manager._agents
    assert bob.agent_id in interaction_manager._agents

    # Verify correct agent objects are stored
    assert interaction_manager._agents[alice.agent_id] is alice
    assert interaction_manager._agents[bob.agent_id] is bob


def test_interaction_recording(interaction_manager, agent_pair):
    """Test recording interactions between agents."""
    alice, bob = agent_pair
    message = "Hello Bob!"

    # Record an interaction
    interaction_manager.record_interaction(alice, bob, message)

    # Verify interaction was recorded
    assert len(alice.get_interactions()) == 1

    interaction = alice.get_interactions()[0]
    assert interaction.sender.agent_id == alice.agent_id
    assert interaction.receiver[0].agent_id == bob.agent_id
    assert interaction.message == message

def test_get_agent_interactions(interaction_manager, agent_pair):
    """Test retrieving agent interactions."""
    alice, bob = agent_pair

    # Record multiple interactions
    interaction_manager.record_interaction(alice, bob, "Hello!")
    interaction_manager.record_interaction(bob, alice, "Hi there!")
    interaction_manager.record_interaction(alice, bob, "How are you?")

    # Get Alice's interactions
    alice_interactions = interaction_manager.get_agent_interactions(alice)
    assert len(alice_interactions) == 3

    # Get Bob's interactions
    bob_interactions = interaction_manager.get_agent_interactions(bob)
    assert len(bob_interactions) == 3

def test_get_agent(interaction_manager, agent_pair):
    """Test retrieving agents by ID."""
    alice, bob = agent_pair

    # Test getting existing agents
    assert interaction_manager.get_agent(alice.agent_id) is alice
    assert interaction_manager.get_agent(bob.agent_id) is bob

    # Test getting non-existent agent
    assert interaction_manager.get_agent("nonexistent_id") is None

def test_interaction_order(interaction_manager, agent_pair):
    """Test that interactions are recorded in order."""
    alice, bob = agent_pair

    messages = ["First", "Second", "Third"]

    for msg in messages:
        interaction_manager.record_interaction(alice, bob, msg)

    # Verify interactions are in order
    interactions = interaction_manager.get_agent_interactions(alice)
    for i, interaction in enumerate(interactions):
        assert interaction.message == messages[i]

def test_self_interaction(interaction_manager, agent_pair):
    """Test recording self-interactions (thoughts)."""
    alice, _ = agent_pair
    thought = "I should learn more"

    interaction_manager.record_interaction(alice, alice, thought)

    interactions = interaction_manager.get_agent_interactions(alice)
    assert len(interactions) == 1
    assert interactions[0].sender.agent_id == alice.agent_id
    assert interactions[0].receiver[0].agent_id == alice.agent_id
    assert interactions[0].message == thought

def test_interaction_validation(interaction_manager, agent_pair):
    """Test validation of interaction recording."""

    alice, _ = agent_pair

    unregistered_agent = type("UnregisteredAgent", (Agent,), {
        "agent_id": "some_unregistered_id",
        "__init__": lambda self, *args, **kwargs: None,
        "agent_informations": {},
    })()

    with pytest.raises(ValueError):
        interaction_manager.record_interaction(unregistered_agent, alice, "Hello")

    with pytest.raises(ValueError):
        interaction_manager.record_interaction(alice, unregistered_agent, "Hello")

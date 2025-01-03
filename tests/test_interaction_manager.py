import pytest
from agentarium import Agent, Interaction
from agentarium.AgentInteractionManager import AgentInteractionManager


@pytest.fixture
def interaction_manager():
    """Create a test interaction manager."""
    return AgentInteractionManager()


@pytest.fixture
def test_agents(interaction_manager):
    """Create test agents for interaction testing."""
    alice = Agent.create_agent(name="Alice")
    bob = Agent.create_agent(name="Bob")
    return alice, bob


def test_agent_registration(interaction_manager, test_agents):
    """Test registering agents with the interaction manager."""
    alice, bob = test_agents

    # Verify agents are registered
    assert alice.agent_id in interaction_manager._agents
    assert bob.agent_id in interaction_manager._agents

    # Verify correct agent objects are stored
    assert interaction_manager._agents[alice.agent_id] is alice
    assert interaction_manager._agents[bob.agent_id] is bob

def test_interaction_recording(interaction_manager, test_agents):
    """Test recording interactions between agents."""
    alice, bob = test_agents
    message = "Hello Bob!"

    # Record an interaction
    interaction_manager.record_interaction(alice, bob, message)

    # Verify interaction was recorded
    assert len(interaction_manager._interactions) == 1
    interaction = interaction_manager._interactions[0]
    assert interaction.sender is alice
    assert interaction.receiver is bob
    assert interaction.message == message

def test_get_agent_interactions(interaction_manager, test_agents):
    """Test retrieving agent interactions."""
    alice, bob = test_agents

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

def test_get_agent(interaction_manager, test_agents):
    """Test retrieving agents by ID."""
    alice, bob = test_agents

    # Test getting existing agents
    assert interaction_manager.get_agent(alice.agent_id) is alice
    assert interaction_manager.get_agent(bob.agent_id) is bob

    # Test getting non-existent agent
    assert interaction_manager.get_agent("nonexistent_id") is None

def test_interaction_order(interaction_manager, test_agents):
    """Test that interactions are recorded in order."""
    alice, bob = test_agents

    messages = ["First", "Second", "Third"]

    for msg in messages:
        interaction_manager.record_interaction(alice, bob, msg)

    # Verify interactions are in order
    interactions = interaction_manager.get_agent_interactions(alice)
    for i, interaction in enumerate(interactions):
        assert interaction.message == messages[i]

def test_self_interaction(interaction_manager, test_agents):
    """Test recording self-interactions (thoughts)."""
    alice, _ = test_agents
    thought = "I should learn more"

    interaction_manager.record_interaction(alice, alice, thought)

    interactions = interaction_manager.get_agent_interactions(alice)
    assert len(interactions) == 1
    assert interactions[0].sender is alice
    assert interactions[0].receiver is alice
    assert interactions[0].message == thought

def test_interaction_validation(interaction_manager, test_agents):
    """Test validation of interaction recording."""
    alice, _ = test_agents

    # Test with unregistered agent
    unregistered_agent = Agent.create_agent(name="Unregistered")

    with pytest.raises(RuntimeError):
        interaction_manager.record_interaction(unregistered_agent, alice, "Hello")

    with pytest.raises(RuntimeError):
        interaction_manager.record_interaction(alice, unregistered_agent, "Hello")
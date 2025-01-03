import os
import pytest
from agentarium import Agent
from agentarium.CheckpointManager import CheckpointManager

@pytest.fixture
def checkpoint_manager():
    """Create a test checkpoint manager."""
    manager = CheckpointManager("test_checkpoint")
    yield manager
    # Cleanup after tests
    if os.path.exists(manager.path):
        os.remove(manager.path)


def test_checkpoint_manager_initialization(checkpoint_manager):
    """Test checkpoint manager initialization."""
    assert checkpoint_manager.name == "test_checkpoint"
    assert checkpoint_manager.path == "test_checkpoint.dill"
    assert checkpoint_manager._action_idx == 0
    assert len(checkpoint_manager.recorded_actions) == 0


def test_checkpoint_save_load(checkpoint_manager):
    """Test saving and loading checkpoint data."""
    # Create agents and perform actions
    alice = Agent.create_agent(name="Alice")
    bob = Agent.create_agent(name="Bob")

    alice.talk_to(bob, "Hello Bob!")
    bob.talk_to(alice, "Hi Alice!")

    # Save checkpoint
    checkpoint_manager.save()

    # Create a new checkpoint manager and load data
    new_manager = CheckpointManager("test_checkpoint")
    new_manager.load()

    # Verify recorded actions were loaded
    assert len(new_manager.recorded_actions) > 0
    assert new_manager.recorded_actions == checkpoint_manager.recorded_actions

def test_checkpoint_recording(checkpoint_manager):
    """Test that actions are properly recorded."""
    alice = Agent.create_agent(name="Alice")
    bob = Agent.create_agent(name="Bob")

    # Perform some actions
    alice.talk_to(bob, "Hello!")
    bob.think("I should respond...")
    bob.talk_to(alice, "Hi there!")

    # Check that actions were recorded
    assert len(checkpoint_manager.recorded_actions) == 3

def test_singleton_behavior():
    """Test that CheckpointManager behaves like a singleton."""
    manager1 = CheckpointManager("test_singleton")
    manager2 = CheckpointManager("test_singleton")

    # Both instances should reference the same object
    assert manager1 is manager2

    # Clean up
    if os.path.exists(manager1.path):
        os.remove(manager1.path)

def test_invalid_checkpoint_load():
    """Test loading from a non-existent checkpoint file."""
    manager = CheckpointManager("nonexistent_checkpoint")

    with pytest.raises(FileNotFoundError):
        manager.load()

def test_checkpoint_reset():
    """Test resetting checkpoint manager state."""
    manager = CheckpointManager("test_reset")

    # Create some actions
    alice = Agent.create_agent(name="Alice")
    alice.think("Test thought")

    assert len(manager.recorded_actions) > 0

    # Reset by creating a new instance with a different name
    new_manager = CheckpointManager("different_name")
    assert len(new_manager.recorded_actions) == 0

    # Clean up
    if os.path.exists(manager.path):
        os.remove(manager.path)
    if os.path.exists(new_manager.path):
        os.remove(new_manager.path)
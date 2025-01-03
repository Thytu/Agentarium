from agentarium import Agent
from agentarium.CheckpointManager import CheckpointManager


if __name__ == '__main__':

    # Initialize the CheckpointManager with a unique identifier for this session
    # The "demo" identifier is used to detect if this simulation was run before
    # If you run this script multiple times, Agentarium will automatically:
    # 1. Detect it's the same simulation (based on the "demo" identifier)
    # 2. Load cached results instead of re-running expensive LLM calls
    # 3. Skip redundant agent interactions that were already computed
    checkpoint = CheckpointManager("demo")

    # Create two agents - their states will be tracked by the checkpoint manager
    # Even agent creation is cached - if these agents were created before,
    # they'll be loaded from cache with their exact same properties
    alice = Agent.create_agent(name="Alice")
    bob = Agent.create_agent(name="Bob")

    # When this interaction happens:
    # - First run: Actually calls the LLM and stores the result
    # - Subsequent runs: Loads the cached interaction result automatically
    alice.talk_to(bob, "What a beautiful day!")

    # Persist all checkpoints to disk
    # This saves the entire simulation state for future runs
    # Next time you run this script, it will use this saved state
    checkpoint.save()

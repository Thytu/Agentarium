from __future__ import annotations

from typing import Dict, List, TYPE_CHECKING
from .Interaction import OneToOneInteraction, OneToManyInteraction

if TYPE_CHECKING:
    from .Agent import Agent


class AgentInteractionManager:
    """
    A singleton class that manages all interactions between agents in the environment.

    This class is responsible for:
    - Keeping track of all registered agents
    - Recording and storing interactions between agents
    - Providing access to interaction history for both individual agents and the entire system

    The manager implements the Singleton pattern to ensure a single source of truth
    for all agent interactions across the environment.
    """

    _instance = None

    def __new__(cls):
        """
        Implements the singleton pattern to ensure only one instance exists.

        Returns:
            AgentInteractionManager: The single instance of the manager.
        """
        if cls._instance is None:
            cls._instance = super(AgentInteractionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        Initializes the interaction manager if not already initialized.

        Due to the singleton pattern, this will only execute once, even if
        multiple instances are created.
        """
        if not self._initialized:
            self._agents: Dict[str, Agent] = {}
            self._interactions: List[OneToOneInteraction | OneToManyInteraction] = []
            self._agent_private_interactions: Dict[str, List[OneToOneInteraction | OneToManyInteraction]] = {}
            self._initialized = True

    def register_agent(self, agent: Agent) -> None:
        """
        Register a new agent with the interaction manager.

        This method adds the agent to the manager's registry and initializes
        their private interaction history.

        Args:
            agent (Agent): The agent to register with the manager.
        """
        self._agents[agent.agent_id] = agent
        self._agent_private_interactions[agent.agent_id] = []

    def reset_agent(self, agent: Agent) -> None:
        """
        Reset the agent's state.
        """
        self._agent_private_interactions[agent.agent_id] = []

    def get_agent(self, agent_id: str) -> Agent | None:
        """
        Retrieve an agent by their ID.

        Args:
            agent_id (str): The unique identifier of the agent.

        Returns:
            Agent | None: The requested agent if found, None otherwise.
        """
        return self._agents.get(agent_id)

    def _record_one_to_one_interaction(self, sender: Agent, receiver: Agent, message: str) -> None:

        if receiver.agent_id not in self._agents:
            raise ValueError(f"Receiver agent {receiver.agent_id} not registered in the interaction manager.")

        interaction = OneToOneInteraction(sender=sender, receiver=receiver, message=message)

        # Record in global interactions
        self._interactions.append(interaction)

        # Record in private interactions for both sender and receiver
        self._agent_private_interactions[sender.agent_id].append(interaction)

        # Prevent storing interactions twice if the sender and receiver are the same
        if receiver.agent_id != sender.agent_id:
            self._agent_private_interactions[receiver.agent_id].append(interaction)

    def _record_one_to_many_interaction(self, sender: Agent, receivers: list[Agent], message: str) -> None:

        if any(_receiver.agent_id not in self._agents for _receiver in receivers):
            invalid_receivers = [_receiver for _receiver in receivers if _receiver.agent_id not in self._agents]
            raise ValueError(f"Receiver agent(s) {invalid_receivers} not registered in the interaction manager.")

        interaction = OneToManyInteraction(sender=sender, receivers=receivers, message=message)

        # Record in global interactions
        self._interactions.append(interaction)

        # Record in private interactions for both sender and receiver
        self._agent_private_interactions[sender.agent_id].append(interaction)

        for _receiver in receivers:
            if _receiver.agent_id != sender.agent_id:
                self._agent_private_interactions[_receiver.agent_id].append(interaction)

    def record_interaction(self, sender: Agent, receiver: Agent | list[Agent], message: str) -> None:
        """
        Record a new interaction between two agents.

        This method creates a new Interaction object and stores it in both the global
        interaction history and the private interaction histories of both involved agents.

        Args:
            sender (Agent): The agent initiating the interaction.
            receiver (Agent | list[Agent]): The agent(s) receiving the interaction.
            message (str): The content of the interaction.
        """

        if sender.agent_id not in self._agents:
            raise ValueError(f"Sender agent {sender.agent_id} is not registered in the interaction manager.")

        if isinstance(receiver, list):
            self._record_one_to_many_interaction(sender, receiver, message)
        else:
            self._record_one_to_one_interaction(sender, receiver, message)

    def get_all_interactions(self) -> List[OneToOneInteraction | OneToManyInteraction]:
        """
        Retrieve the complete history of all interactions in the environment.

        This method is primarily used for administrative and debugging purposes.

        Returns:
            List[Interaction]: A list of all interactions that have occurred.
        """
        return self._interactions

    def get_agent_interactions(self, agent: Agent) -> List[OneToOneInteraction | OneToManyInteraction]:
        """
        Retrieve all interactions involving a specific agent.

        This includes both interactions where the agent was the sender
        and where they were the receiver.

        Args:
            agent (Agent): The agent whose interactions to retrieve.

        Returns:
            List[Interaction]: A list of all interactions involving the agent.
        """
        return self._agent_private_interactions.get(agent.agent_id, [])

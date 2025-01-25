from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Agent import Agent

@dataclass
class OneToOneInteraction:
    """
    Represents a single interaction between two agents in the environment.

    This class captures the essential details of communication between agents,
    including who initiated the interaction (sender), who received it (receiver),
    and the content of the interaction (message).

    Attributes:
        sender (Agent): The agent who initiated the interaction.
        receiver (Agent): The agent who received the interaction.
        message (str): The content of the interaction between the agents.
    """

    sender: Agent
    """The agent who initiated the interaction."""

    receiver: Agent
    """The agent who received the interaction."""

    message: str
    """The content of the interaction between the agents."""

    def dump(self) -> dict:
        """
        Returns a dictionary representation of the interaction.
        """
        return {
            "sender": self.sender.agent_id,
            "receiver": self.receiver.agent_id,
            "message": self.message,
        }

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the interaction.

        Returns:
            str: A formatted string showing sender, receiver, and the interaction message.
        """
        return f"{self.sender.name} ({self.sender.agent_id}) said to {self.receiver.name} ({self.receiver.agent_id}): {self.message}"

    def __repr__(self) -> str:
        """
        Returns a string representation of the interaction, same as __str__.

        Returns:
            str: A formatted string showing sender, receiver, and the interaction message.
        """
        return self.__str__()



@dataclass
class OneToManyInteraction:
    """
    Represents a single interaction between one agent and multiple agents in the environment.

    This class captures the essential details of communication between agents,
    including who initiated the interaction (sender), who received it (receiver),
    and the content of the interaction (message).

    Attributes:
        sender (Agent): The agent who initiated the interaction.
        receivers list[Agent]: The agents who received the interaction.
        message (str): The content of the interaction between the agents.
    """

    sender: Agent
    """The agent who initiated the interaction."""

    receivers: list[Agent]
    """The agents who received the interaction."""

    message: str
    """The content of the interaction between the agents."""

    def dump(self) -> dict:
        """
        Returns a dictionary representation of the interaction.
        """
        return {
            "sender": self.sender.agent_id,
            "receivers": self.receivers.agent_id,
            "message": self.message,
        }

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the interaction.

        Returns:
            str: A formatted string showing sender, receivers, and the interaction message.
        """
        return f"{self.sender.name} ({self.sender.agent_id}) said to {', '.join([_receiver.name + f'({_receiver.agent_id})' for _receiver in self.receivers])}: {self.message}"

    def __repr__(self) -> str:
        """
        Returns a string representation of the interaction, same as __str__.

        Returns:
            str: A formatted string showing sender, receivers, and the interaction message.
        """
        return self.__str__()


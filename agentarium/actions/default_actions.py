import logging

from agentarium.utils import cache_w_checkpoint_manager
from agentarium.actions.Action import Action, verify_agent_in_kwargs

logger = logging.getLogger(__name__)

@verify_agent_in_kwargs
@cache_w_checkpoint_manager
def talk_action_function(*args, **kwargs):
    """
    Send a message from one agent to another and record the interaction.

    Args:
        *args: Variable length argument list where:
            - First argument (str): The ID of the agent to send the message to
            - Second argument (str): The content of the message to send
        **kwargs: Arbitrary keyword arguments. Must contain 'agent' key with the Agent instance.

    Returns:
        dict: A dictionary containing:
            - sender (str): The ID of the sending agent
            - receiver (str | list[str]): The ID of the receiving agent
            - message (str): The content of the message

    Raises:
        RuntimeError: If less than 1 argument is provided, if 'agent' is not in kwargs,
                     or if the receiver agent ID is invalid.
    """

    if len(args) < 1:
        raise RuntimeError(f"Received a TALK action with less than 1 argument: {args}")

    if "agent" not in kwargs:
        raise RuntimeError(f"Couldn't find agent in  {kwargs=} for TALK action")

    # Retrieve the receiver IDs
    receiver_ids = [_rec.strip() for _rec in args[0].split(',') if len(_rec.strip()) != 0]

    # If the receiver is "all", talk to all agents
    if "all" in receiver_ids:
        receiver_ids = [agent.agent_id for agent in kwargs["agent"]._interaction_manager._agents.values()]

    # Retrieve the receivers from their IDs
    receivers = [kwargs["agent"]._interaction_manager.get_agent(_receiver_id) for _receiver_id in receiver_ids]

    # Check if the receivers are valid
    if any(receiver is None for receiver in receivers):
        logger.error(f"Received a TALK action with an invalid agent ID {args[0]=} {args=} {kwargs['agent']._interaction_manager._agents=}")
        raise RuntimeError(f"Received a TALK action with an invalid agent ID: {args[0]=}. {args=}")

    message = args[1]

    if len(message) == 0:
        logger.warning(f"Received empty message for talk_action_function: {args=}")

    # Record the interaction
    kwargs["agent"]._interaction_manager.record_interaction(kwargs["agent"], receivers, message)

    return {
        "sender": kwargs["agent"].agent_id,
        "receiver": [receiver.agent_id for receiver in receivers],
        "message": message,
    }

@verify_agent_in_kwargs
@cache_w_checkpoint_manager
def think_action_function(*args, **kwargs):
    """
    Record an agent's internal thought.

    Args:
        *params: Variable length argument list where the first argument is the thought content.
        **kwargs: Arbitrary keyword arguments. Must contain 'agent' key with the Agent instance.

    Returns:
        dict: A dictionary containing:
            - sender (str): The ID of the thinking agent
            - receiver (str): Same as sender (since it's an internal thought)
            - message (str): The content of the thought

    Raises:
        RuntimeError: If no parameters are provided for the thought content.
    """

    if len(args) < 1:
        raise RuntimeError(f"Received a TALK action with less than 1 argument: {args}")

    if "agent" not in kwargs:
        raise RuntimeError(f"Couldn't find agent in  {kwargs=} for TALK action")

    message = args[0]

    kwargs["agent"]._interaction_manager.record_interaction(kwargs["agent"], kwargs["agent"], message)

    return {
        "sender": kwargs["agent"].agent_id,
        "receiver": kwargs["agent"].agent_id,
        "message": message,
    }


# Create action instances at module level
talk_action_description = """\
Talk to agents by specifying their IDs followed by the content to say:
- To talk to a single agent: Enter an agent ID (e.g. "1")
- To talk to multiple agents: Enter IDs separated by commas (e.g. "1,2,3")
- To talk to all agents: Enter "all"\
"""
talk_action = Action(
    name="talk",
    description=talk_action_description,
    parameters=["agent_id", "message"],
    function=talk_action_function,
)

think_action = Action(
    name="think",
    description="Think about something.",
    parameters=["content"],
    function=think_action_function,
)

default_actions = {
    talk_action.name: talk_action,
    think_action.name: think_action,
}

# __all__ = ["talk_action", "think_action", "default_actions"]

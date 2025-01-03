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
            - receiver (str): The ID of the receiving agent
            - message (str): The content of the message

    Raises:
        RuntimeError: If less than 1 argument is provided, if 'agent' is not in kwargs,
                     or if the receiver agent ID is invalid.
    """

    if len(args) < 1:
        raise RuntimeError(f"Received a TALK action with less than 1 argument: {args}")

    if "agent" not in kwargs:
        raise RuntimeError(f"Couldn't find agent in  {kwargs=} for TALK action")

    receiver = kwargs["agent"]._interaction_manager.get_agent(args[0])

    if receiver is None:
        logger.error(f"Received a TALK action with an invalid agent ID {args[0]=} {args=} {kwargs['agent']._interaction_manager._agents=}")
        raise RuntimeError(f"Received a TALK action with an invalid agent ID: {args[0]}. {args=}")

    message = args[1]

    kwargs["agent"]._interaction_manager.record_interaction(kwargs["agent"], receiver, message)

    return {
        "sender": kwargs["agent"].agent_id,
        "receiver": receiver.agent_id,
        "message": message,
    }

@verify_agent_in_kwargs
@cache_w_checkpoint_manager
def think_action_function(*params, **kwargs):
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
    return talk_action_function(kwargs["agent"].agent_id, *params, **kwargs)


# Create action instances at module level
talk_action = Action(
    name="talk",
    description="Talk to the agent with the given ID.",
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

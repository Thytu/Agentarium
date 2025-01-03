import logging

from functools import wraps
from dataclasses import dataclass
from typing import Callable, Any, Dict, Union, Optional, List


# TODO: rename the output key "action" to "_action_name"
def standardize_action_output(action):
    """
    Decorator that standardizes the output format of action functions.

    This decorator ensures that all action functions return a dictionary with a
    consistent format, containing at minimum an 'action' key with the action name.
    If the original function returns a dictionary, its contents are preserved
    (except for the 'action' key which may be overwritten). If it returns a
    non-dictionary value, it is stored under the 'output' key.

    Args:
        fun (Callable): The action function to decorate.

    Returns:
        Callable: A wrapped function that standardizes the output format.
    """

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):

            fn_output = function(*args, **kwargs)

            output = fn_output if isinstance(fn_output, dict) else {"output": fn_output}

            if "action" in output:
                logging.warning((
                    f"The action '{action.name}' returned an output with an 'action' key. "
                    "This is not allowed, it will be overwritten."
                ))

            output["action"] = action.name

            return output

        return wrapper

    return decorator


def verify_agent_in_kwargs(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "agent" not in kwargs:
            raise RuntimeError(f"Couldn't find agent in {kwargs=} for {function.__name__} action")
        return function(*args, **kwargs)
    return wrapper


@dataclass
class Action:
    """
    Represents an action that an agent can perform.

    Attributes:
        name (str): Unique identifier for the action. Also used to remove the action from the agent's action space.
        description (str, optional): Short description of what the action does.
        parameters (Union[List[str], str]): List of parameters names or a single parameter name.
        function: Callable that implements the action.

    Example:
        ```python
        action = Action(
            name="CHATGPT",
            description="Use ChatGPT",
            parameters=["prompt"],
            function=use_chatgpt,
        )
        ```
    """

    name: str
    description: Optional[str]
    parameters: Union[List[str], str]
    function: Callable[[Any, ...], Dict[str, Any]]

    def __post_init__(self):
        """Validate action attributes after initialization."""

        if len(self.name) < 1:
            raise ValueError("Action name must be non-empty")

        if isinstance(self.parameters, str):
            self.parameters = [self.parameters]

        if not isinstance(self.parameters, list):
            raise ValueError("Parameters must be a list of strings or a single string")

        if any(not isinstance(p, str) for p in self.parameters):
            raise ValueError("Parameter names must be strings")

        if any(len(p) < 1 for p in self.parameters):
            raise ValueError("Parameter names must be non-empty")

        # Store the function's module and name for pickling
        if hasattr(self.function, '__module__') and hasattr(self.function, '__name__'):
            self._function_module = self.function.__module__
            self._function_name = self.function.__name__
        else:
            raise ValueError("Function must be a named function (not a lambda) defined at module level")

        self.function = standardize_action_output(self)(self.function)

    def get_format(self):
        """Returns a string representation of the action's format for use in prompts.

        The format consists of the action name followed by its parameters, all enclosed in square brackets.
        For example, an action named "TALK" with parameters ["agent_id", "message"] would return:
        "[TALK][agent_id][message]"

        Returns:
            str: The formatted string showing how to use the action in prompts.
        """
        return f"[{self.name}]" + "".join([f"[{p}]" for p in self.parameters])

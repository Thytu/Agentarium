import json
import hashlib

from typing import Dict, Any
# from .CheckpointManager import CheckpointManager


def dict_hash(dictionary: Dict[str, Any]) -> str:
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()

    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)

    return dhash.hexdigest()



def cache_w_checkpoint_manager(function):
    """
    A decorator that checks if an action should be skipped based on recorded actions.

    If the action is found in the checkpoint manager's recorded actions, it will be skipped.
    This helps in replaying simulations without duplicating actions.

    Args:
        function (Callable[..., Any]): The function to decorate

    Returns:
        Callable[..., Any]: The decorated function
    """


    def wrapper(*args, **kwargs):

        from .CheckpointManager import CheckpointManager

        checkpoint_manager = CheckpointManager()

        expected_hash = checkpoint_manager.recorded_actions[checkpoint_manager._action_idx]["hash"] if len(checkpoint_manager.recorded_actions) > checkpoint_manager._action_idx else None
        action_hash = str({"function": function.__name__, "args": args, "kwargs": kwargs})

        if action_hash == expected_hash:
            checkpoint_manager._action_idx += 1
            return checkpoint_manager.recorded_actions[checkpoint_manager._action_idx - 1]["result"]

        result = function(*args, **kwargs)
        checkpoint_manager.recorded_actions = checkpoint_manager.recorded_actions[:checkpoint_manager._action_idx] + [{
            "hash": action_hash,
            "result": result,
        }]
        checkpoint_manager._action_idx += 1
        return result

    return wrapper

"""
This demo showcases how to create a custom action for Agentarium agents.
It demonstrates:
1. Creating an agent with a custom personality
2. Adding a new action (ChatGPT integration) to the agent
3. Using both direct action calls and autonomous agent behavior

The demo specifically shows how to use the `add_action` method to extend an agent's capabilities.

Action Definition Format:
    Action(
        name: str,           # Unique identifier for the action
        description: str,    # Description of what the action does
        parameters: List[str], # List of parameter names the action accepts
        function: Callable   # Function that implements the action behavior
    )

The action function should take (*args, **kwargs) as parameters and return
either a string or a dictionary. If a dictionary is returned, it can contain any keys
except 'action' which is reserved. The function's output will be automatically
standardized to include the action name.
"""

import aisuite as ai
from typing import Dict, Any
from agentarium import Agent, Action


# Initialize the AI client for ChatGPT interactions
llm_client = ai.Client()


def use_chatgpt(prompt: str, *args, **kwargs) -> Dict[str, str]:
    """
    A custom action that allows an agent to interact with ChatGPT.
    This function demonstrates how to:
    1. Maintain conversation history in agent's storage
    2. Make API calls to external services
    3. Update agent's memory with the interaction

    The function follows the required format for custom actions:
    - Takes an agent as the first parameter
    - Takes action-specific parameters after that
    - Returns either a string or a dictionary (dictionary in this case)

    Args:
        agent (Agent): The agent instance performing the action
        prompt (str): The message to send to ChatGPT
        *args, **kwargs: Additional arguments (not used in this demo)

    Returns:
        Dict[str, str]: A dictionary containing:
            - agent_prompt: The original prompt sent to ChatGPT
            - chatgpt_response: ChatGPT's response
            Note: The 'action' key will be automatically added by the framework when called by agent.act()
    """

    agent: Agent = kwargs["agent"] # Every action receives the agent in kwargs

    # Initialize chat history if it doesn't exist
    if "chatgpt_history" not in agent.storage:
        agent.storage["chatgpt_history"] = []

    # Prepare and send the message to ChatGPT
    chatgpt_history = agent.storage["chatgpt_history"]
    chatgpt_history.append({"role": "user", "content": prompt})

    response = llm_client.chat.completions.create(
        model="openai:gpt-4o-mini",
        messages=chatgpt_history,
        temperature=0.2,
        timeout=60
    ).choices[0].message.content.strip()

    # Store the interaction in agent's memory and history
    agent.storage["chatgpt_history"].append({"role": "assistant", "content": response})
    agent.think(f"What you said to ChatGPT: {prompt}")
    agent.think(f"ChatGPT response: {response}")

    return {
        "agent_prompt": prompt,
        "chatgpt_response": response
    }


def print_agent_output(output: Dict[str, Any]) -> None:
    """
    Helper function to format and print agent's action outputs.

    Args:
        output (Dict[str, Any]): The output dictionary from an agent's action
    """
    print(f"=== Agent executed action '{output['action']}' with the following output ===", end="\n\n")

    for key, value in output.items():
        if key != "action":
            print(f"  {key}: {value}", end="\n\n")

    print("=" * 65, end="\n\n\n")


def main():
    """
    Main demo function showcasing:
    1. Agent creation with personality
    2. Adding a custom action
    3. Direct action calls vs autonomous behavior
    """
    # Create an agent with a defined personality
    agent = Agent.create_agent(
        agent_id="demo_agent",
        name="John",
        gender="male",
        age=25,
        occupation="software engineer",
        location="San Francisco",
        bio="John is a curious software engineer who loves to learn and experiment with AI.",
    )

    # Add the ChatGPT action to the agent's capabilities
    # This demonstrates how to use add_action:
    # 1. Define the action descriptor with prompt, format, and example
    # 2. Provide an action function that implements the behavior
    agent.add_action(
        # Action descriptor - tells the agent how to use this action
        Action(
            name="CHATGPT",
            description="Use ChatGPT to have a conversation or ask questions.",
            parameters=["prompt"],
            function=use_chatgpt
        )
    )

    # Initialize the agent's thoughts
    agent.think("I've just been created and I can use ChatGPT to interact!")

    # Example 1: Direct action call
    output = agent.execute_action("CHATGPT", "Hello! Can you help me learn about artificial intelligence?")
    print_agent_output(output)  # Add the action name to the output

    # Example 2: Autonomous behavior - agent can now choose to use ChatGPT on its own
    output = agent.act()
    print_agent_output(output)


if __name__ == '__main__':
    main()

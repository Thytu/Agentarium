from __future__ import annotations

import re
import logging
import aisuite as ai

from copy import deepcopy
from .actions.Action import Action
from typing import List, Dict, Any
from faker import Faker
from .Interaction import Interaction
from .AgentInteractionManager import AgentInteractionManager
from .Config import Config
from .utils import cache_w_checkpoint_manager
from .actions.default_actions import default_actions
from .constant import DefaultValue


faker = Faker()
config = Config()
llm_client = ai.Client({**config.aisuite})


class Agent:
    """
    A class representing an autonomous agent in the environment.

    The Agent class is the core component of the Agentarium system, representing
    an individual entity capable of:
    - Maintaining its own identity and characteristics
    - Interacting with other agents through messages
    - Making autonomous decisions based on its state and interactions
    - Generating responses using natural language models

    Each agent has a unique identifier and a set of characteristics that define
    its personality and behavior. These characteristics can be either provided
    during initialization or generated automatically.

    Attributes:
        agent_id (str): Unique identifier for the agent
        agent_informations (dict): Dictionary containing agent characteristics
            including name, age, gender, occupation, location, and bio
        _interaction_manager (AgentInteractionManager): Singleton instance managing
            all agent interactions
    """

    _interaction_manager = AgentInteractionManager()
    _allow_init = False

    _default_generate_agent_prompt = """You're goal is to generate the bio of a fictional person.
Make this bio as realistic and as detailed as possible.
You may be given information about the person to generate a bio for, if so, use that information to generate a bio.
If you are not given any information about the person, generate a bio for a random person.

You must generate the bio in the following format:
Bio: [Bio of the person]
"""

    _default_self_introduction_prompt = """
Informations about yourself:
{agent_informations}

Your interactions:
{interactions}
"""

    _default_act_prompt = """{self_introduction}

Given the above information, think about what you should do next.

The following are the possible actions you can take:
{actions}

Write in the following format:
<THINK>
{{YOUR_THOUGHTS}}
</THINK>

<ACTION>
[{{One of the following actions: {list_of_actions}}}]
</ACTION>
"""

    def __init__(self, **kwargs):
        """
        Initialize an agent with given or generated characteristics.
        This method should not be called directly - use create_agent() instead.
        """

        if not Agent._allow_init:
            raise RuntimeError("Agent instances should be created using Agent.create_agent()")

        if "agent_id" in kwargs:
            self.agent_id = kwargs.pop("agent_id")

        self.agent_id = self.agent_id if self.agent_id!= DefaultValue.NOT_PROVIDED else faker.uuid4()
        self.agent_informations: dict = kwargs or {}

        if "gender" not in kwargs or kwargs["gender"] == DefaultValue.NOT_PROVIDED:
            self.agent_informations["gender"] = faker.random_element(elements=["male", "female"])

        if "name" not in kwargs or kwargs["name"] == DefaultValue.NOT_PROVIDED:
            self.agent_informations["name"] = getattr(faker, f"name_{self.agent_informations['gender']}")()

        if "age" not in kwargs or kwargs["age"] == DefaultValue.NOT_PROVIDED:
            self.agent_informations["age"] = faker.random_int(18, 80)

        if "occupation" not in kwargs or kwargs["occupation"] == DefaultValue.NOT_PROVIDED:
            self.agent_informations["occupation"] = faker.job()

        if "location" not in kwargs or kwargs["location"] == DefaultValue.NOT_PROVIDED:
            self.agent_informations["location"] = faker.city()

        if "bio" not in kwargs or kwargs["bio"] == DefaultValue.NOT_PROVIDED:
            self.agent_informations["bio"] = Agent._generate_agent_bio(self.agent_informations)

        self._interaction_manager.register_agent(self)

        self._self_introduction_prompt = deepcopy(Agent._default_self_introduction_prompt)
        self._act_prompt = deepcopy(Agent._default_act_prompt)

        self._actions = deepcopy(default_actions) if kwargs["actions"] == DefaultValue.NOT_PROVIDED else kwargs["actions"]

        self.storage = {}  # Useful for storing data between actions. Note: not used by the agentarium system.

    def __setstate__(self, state):
        self.__dict__.update(state) # default __setstate__
        self._interaction_manager.register_agent(self) # add the agent to the interaction manager

    @staticmethod
    @cache_w_checkpoint_manager
    def create_agent(
        agent_id: str = DefaultValue.NOT_PROVIDED,
        gender: str = DefaultValue.NOT_PROVIDED,
        name: str = DefaultValue.NOT_PROVIDED,
        age: int = DefaultValue.NOT_PROVIDED,
        occupation: str = DefaultValue.NOT_PROVIDED,
        location: str = DefaultValue.NOT_PROVIDED,
        bio: str = DefaultValue.NOT_PROVIDED,
        actions: dict = DefaultValue.NOT_PROVIDED,
        **kwargs,
    ) -> Agent:
        """
        Initialize an agent with given or generated characteristics.

        Creates a new agent instance with a unique identifier and a set of
        characteristics. If specific characteristics are not provided, they
        are automatically generated to create a complete and realistic agent
        profile.

        The following characteristics are handled:
        - Gender (male/female)
        - Name (appropriate for the gender)
        - Age (between 18 and 80)
        - Occupation (randomly selected job)
        - Location (randomly selected city)
        - Bio (generated based on other characteristics)
        - Actions, by default "talk" and "think" actions are available (default actions or custom actions)
        Args:
            **kwargs: Dictionary of agent characteristics to use instead of
                generating them. Any characteristic not provided will be
                automatically generated.
        """
        try:
            Agent._allow_init = True
            return Agent(
                agent_id=agent_id,
                gender=gender,
                name=name,
                age=age,
                occupation=occupation,
                location=location,
                bio=bio,
                actions=actions,
                **kwargs
            )
        finally:
            Agent._allow_init = False

    @property
    def name(self) -> str:
        """
        Get the agent's name.

        Returns:
            str: The name of the agent.
        """
        return self.agent_informations["name"]

    @property
    def gender(self) -> str:
        """
        Get the agent's gender.

        Returns:
            str: The gender of the agent.
        """
        return self.agent_informations["gender"]

    @property
    def age(self) -> int:
        """
        Get the agent's age.

        Returns:
            int: The age of the agent.
        """
        return self.agent_informations["age"]

    @property
    def occupation(self) -> str:
        """
        Get the agent's occupation.

        Returns:
            str: The occupation of the agent.
        """
        return self.agent_informations["occupation"]

    @property
    def location(self) -> str:
        """
        Get the agent's location.

        Returns:
            str: The location of the agent.
        """
        return self.agent_informations["location"]

    @property
    def bio(self) -> str:
        """
        Get the agent's biography.

        Returns:
            str: The biography of the agent.
        """
        return self.agent_informations["bio"]

    @staticmethod
    def _generate_prompt_to_generate_bio(**kwargs) -> str:
        """
        Generate a prompt for creating an agent's biography.

        Creates a prompt that will be used by the language model to generate
        a realistic biography for the agent. If characteristics are provided,
        they are incorporated into the prompt to ensure the generated bio
        is consistent with the agent's existing traits.

        Args:
            **kwargs: Dictionary of agent characteristics to incorporate
                into the biography generation prompt.

        Returns:
            str: A formatted prompt string for biography generation.
        """
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if not kwargs:
            return Agent._default_generate_agent_prompt

        prompt = Agent._default_generate_agent_prompt
        prompt += "\nInformation about the person to generate a bio for:"

        for key, value in kwargs.items():
            prompt += f"\n{key}: {value}"

        return prompt

    @staticmethod
    def _generate_agent_bio(agent_informations: dict) -> str:
        """
        Generate a biography for an agent using a language model.

        Uses the OpenAI API to generate a realistic and detailed biography
        based on the agent's characteristics. The biography is generated
        to be consistent with any existing information about the agent.

        Args:
            agent_informations (dict): Dictionary of agent characteristics
                to use in generating the biography.

        Returns:
            str: A generated biography for the agent.
        """
        prompt = Agent._generate_prompt_to_generate_bio(**agent_informations)

        response = llm_client.chat.completions.create(
            model=f"{config.llm_provider}:{config.llm_model}",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
        )

        return response.choices[0].message.content

    @cache_w_checkpoint_manager
    def act(self) -> str:
        """
        Generate and execute the agent's next action based on their current state.

        This method:
        1. Generates a self-introduction based on agent's characteristics and history
        2. Creates a prompt combining the self-introduction and available actions
        3. Uses the language model to decide the next action
        4. Parses and executes the chosen action

        The agent's decision is based on:
        - Their characteristics (personality, role, etc.)
        - Their interaction history
        - Available actions in their action space

        Returns:
            Dict[str, Any]: A dictionary containing the action results, including:
                - 'action': The name of the executed action
                - Additional keys depending on the specific action executed

        Raises:
            RuntimeError: If no actions are available or if the chosen action is invalid
        """

        if len(self._actions) == 0:
            raise RuntimeError("No actions available for the agent to perform")

        self_introduction = self._self_introduction_prompt.format(
            agent_informations=self.agent_informations,
            interactions=self.get_interactions(),
        )

        prompt = self._act_prompt.format(
            self_introduction=self_introduction,
            actions="\n".join([f"{action.get_format()}: {action.description if action.description else ''}" for action in self._actions.values()]),
            list_of_actions=list(self._actions.keys()),
        )

        response = llm_client.chat.completions.create(
            model=f"{config.llm_provider}:{config.llm_model}",
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )

        regex_result = re.search(r"<ACTION>(.*?)</ACTION>", response.choices[0].message.content, re.DOTALL).group(1).strip()
        action_name, *args = [value.replace("[", "").replace("]", "").strip() for value in regex_result.split("]")]

        if action_name not in self._actions:
            logging.error(f"Received an invalid action: '{action_name=}' in the output: {response.choices[0].message.content}")
            raise RuntimeError(f"Invalid action received: '{action_name}'.")

        return self._actions[action_name].function(*args, agent=self) # we pass the agent to the action function to allow it to use the agent's methods

    def dump(self) -> dict:
        """
        Dump the agent's state to a dictionary.
        """

        return {
            "agent_id": self.agent_id,
            "agent_informations": self.agent_informations,
            "interactions": [interaction.dump() for interaction in self._interaction_manager._agent_private_interactions[self.agent_id]],
        }

    def __str__(self) -> str:
        """
        Get a string representation of the agent.

        Returns:
            str: A formatted string containing all the agent's characteristics.
        """
        return "\n".join([f"{key.capitalize()}: {value}" for key, value in self.agent_informations.items()])

    def __repr__(self) -> str:
        """
        Get a string representation of the agent, same as __str__.

        Returns:
            str: A formatted string containing all the agent's characteristics.
        """
        return Agent.__str__(self)

    def get_interactions(self) -> List[Interaction]:
        """
        Retrieve all interactions involving this agent.

        Returns:
            List[Interaction]: A list of all interactions where this agent
                was either the sender or receiver.
        """
        return self._interaction_manager.get_agent_interactions(self)

    def ask(self, message: str) -> None:
        """
        Ask the agent a question and receive a contextually aware response.

        The agent considers its characteristics and interaction history when formulating
        the response, maintaining consistency with its persona.

        Note: The agent will not save the question nor the response in its interaction history.

        Args:
            message (str): The question to ask the agent.

        Returns:
            str: The agent's response to the question.
        """

        prompt = self._self_introduction_prompt.format(
            agent_informations=self.agent_informations,
            interactions=self.get_interactions(),
        )

        prompt += f"\nYou are asked the following question: {message}. Answer the question as best as you can."

        response = llm_client.chat.completions.create(
            model=f"{config.llm_provider}:{config.llm_model}",
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )

        return response.choices[0].message.content

    def add_action(self, action: Action) -> None:
        """
        Add a new action to the agent's capabilities.

        This method allows extending an agent's behavior by adding custom actions. Each action consists of:
        1. A descriptor that tells the agent how to use the action
        2. A function that implements the action's behavior

        Args:
            action_descriptor (dict[str, str]): A dictionary describing the action with these required keys:
                - "format": Format string showing action syntax. Must start with [ACTION_NAME] in caps,
                           followed by parameter placeholders in brackets. Example: "[CHATGPT][message]"
                - "prompt": Human-readable description of what the action does
                - "example": Concrete example showing how to use the action
            action_function (Callable[[Agent, str], str | dict]): Function implementing the action.
                - First parameter must be the agent instance
                - Remaining parameters should match the format string
                - Can return either a string or a dictionary
                - If returning a dict, the 'action' key is reserved and will be overwritten
                - If returning a non-dict value, it will be stored under the 'output' key

        Raises:
            RuntimeError: If the action_descriptor is missing required keys or if the action
                         name conflicts with an existing action

        Example:
            ```python
            # Adding a ChatGPT integration action
            agent.add_action(
                action_descriptor={
                    "format": "[CHATGPT][Your message here]",
                    "prompt": "Use ChatGPT to have a conversation or ask questions.",
                    "example": "[CHATGPT][What's the weather like today?]"
                },
                action_function=use_chatgpt
            )

            # The action function could look like:
            def use_chatgpt(agent: Agent, message: str) -> dict:
                response = call_chatgpt_api(message)
                return {
                    "message": message,
                    "response": response
                }  # Will be automatically formatted to include "action": "CHATGPT"
            ```

        Notes:
            - The action name is extracted from the first bracket pair in the format string
            - The action function's output will be automatically standardized to include the action name
            - Any 'action' key in the function's output dictionary will be overwritten
        """

        if action.name in self._actions:
            raise RuntimeError(f"Invalid action: {action.name}, action already exists in the agent's action space")

        self._actions[action.name] = action

    def execute_action(self, action_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Manually execute an action by name.

        Args:
            name: Name of the action to execute
            *args, **kwargs: Arguments to pass to the action function

        Returns:
            Dict containing the action results
        """

        if action_name not in self._actions:
            raise RuntimeError(f"Invalid action: {action_name}, action does not exist in the agent's action space")

        return self._actions[action_name].function(*args, **kwargs, agent=self)

    def remove_action(self, action_name: str) -> None:
        """
        Remove an action from the agent's action space.
        """
        if action_name not in self._actions:
            raise RuntimeError(f"Invalid action: {action_name}, action does not exist in the agent's action space")

        del self._actions[action_name]

    def talk_to(self, agent: Agent, message: str) -> None:
        """
        Send a message from one agent to another and record the interaction.
        """

        if "talk" not in self._actions:
            # Did you really removed the default "talk" action and expect the talk_to method to work?
            raise RuntimeError("Talk action not found in the agent's action space.")

        self.execute_action("talk", agent.agent_id, message)

    def think(self, message: str) -> None:
        """
        Make the agent think about a message.
        """

        if "think" not in self._actions:
            raise RuntimeError("Think action not found in the agent's action space.")

        self.execute_action("think", message)

    def reset(self) -> None:
        """
        Reset the agent's state.
        """
        self._interaction_manager.reset_agent(self)
        self.storage = {}


if __name__ == "__main__":

    interaction = Interaction(
        sender=Agent.create_agent(name="Alice", bio="Alice is a software engineer."),
        receiver=Agent.create_agent(name="Bob", bio="Bob is a data scientist."),
        message="Hello Bob! I heard you're working on some interesting data science projects."
    )

    print(interaction)

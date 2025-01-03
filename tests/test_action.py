import pytest
from agentarium import Action, Agent

def test_action_creation():
    """Test creating an action with valid parameters."""
    def test_function(*args, **kwargs):
        return {"result": "success"}

    action = Action(
        name="test",
        description="A test action",
        parameters=["param1", "param2"],
        function=test_function
    )

    assert action.name == "test"
    assert action.description == "A test action"
    assert action.parameters == ["param1", "param2"]
    assert action.function is not None

def test_action_single_parameter():
    """Test creating an action with a single parameter string."""
    def test_function(*args, **kwargs):
        return {"result": "success"}

    # Test with a single parameter string
    action = Action(
        name="test",
        description="A test action",
        parameters="param1",
        function=test_function
    )

    assert action.parameters == ["param1"]

    # Test with a list of parameters
    action = Action(
        name="test",
        description="A test action",
        parameters=["param1"],
        function=test_function
    )

    assert action.parameters == ["param1"]


def test_invalid_action_name():
    """Test that action creation fails with invalid name."""
    def test_function(*args, **kwargs):
        return {"result": "success"}

    with pytest.raises(ValueError):
        Action(
            name="",
            description="A test action",
            parameters=["param1"],
            function=test_function
        )


def test_invalid_parameters():
    """Test that action creation fails with invalid parameters."""
    def test_function(*args, **kwargs):
        return {"result": "success"}

    # Test empty parameter name
    with pytest.raises(ValueError):
        Action(
            name="test",
            description="A test action",
            parameters=[""],
            function=test_function
        )

    # Test non-string parameter
    with pytest.raises(ValueError):
        Action(
            name="test",
            description="A test action",
            parameters=[123],
            function=test_function
        )


def test_action_format():
    """Test the action format string generation."""
    def test_function(*args, **kwargs):
        return {"result": "success"}

    action = Action(
        name="test",
        description="A test action",
        parameters=["param1", "param2"],
        function=test_function
    )

    expected_format = "[test][param1][param2]"
    assert action.get_format() == expected_format


def test_action_execution():
    """Test executing an action with an agent."""
    def test_function(*args, **kwargs):
        agent = kwargs["agent"]
        return {"message": f"Action executed by {agent.name}"}

    action = Action(
        name="test",
        description="A test action",
        parameters=["param"],
        function=test_function
    )

    agent = Agent.create_agent(name="TestAgent")
    result = action.function("test_param", agent=agent)

    assert result["action"] == "test"
    assert "message" in result
    assert "TestAgent" in result["message"]


def test_action_without_agent():
    """Test that action execution fails without agent in kwargs."""
    def test_function(*args, **kwargs):
        return {"result": "success"}

    action = Action(
        name="test",
        description="A test action",
        parameters=["param"],
        function=test_function
    )

    with pytest.raises(RuntimeError):
        action.function("test_param")

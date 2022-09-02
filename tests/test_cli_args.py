import pytest
import logging
from unittest.mock import patch, call
from tests.data import basic_terra_py, basic_terra_factory_py

pytest_plugins = [
    str("_pytest.pytester"),
]

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

data = [
    {"binary": "terraform", "tfdir": "foo", "command": "plan", "skip_teardown": True},
    {"binary": "terraform", "tfdir": "bar", "command": "apply", "skip_teardown": False},
]

params = [
    pytest.param(basic_terra_py, data, id="terra"),
    pytest.param(basic_terra_factory_py, data, id="terra_factory"),
]


@pytest.mark.parametrize("content,data", params)
@patch("tftest.TerraformTest.execute_command")
def test_skip_teardown(mock_execute_command, pytester, content, data):
    """Ensure that the --skip-tf-destroy flag is valid"""

    pytester.makepyfile(content.format(data))
    pytester.inline_run("--skip-teardown=true")
    log.info("Assert that terraform destroy command was not called")

    assert (
        call("destroy", "-auto-approve", "-no-color")
        not in mock_execute_command.call_args_list
    )

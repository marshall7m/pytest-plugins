import logging
from unittest.mock import patch, call, DEFAULT
import pytest
import os
from terra_fixt import _execute_command
pytest_plugins = [
    str("_pytest.pytester"),
]

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

tf_cmds = ["setup", "plan", "apply", "output"]


@pytest.mark.parametrize("terra", [{"binary": "terragrunt", "tfdir": "roo", "skip_teardown": True}], indirect=True)
@pytest.mark.parametrize("params", [
    {"color": True},
    {os.getcwd() + "/roo": {"color": True}}
])
@pytest.mark.parametrize("cmd", tf_cmds)
def test__execute_command_with_cache(request, terra, params, cmd):
    log.info("Clearing pytest cache")
    request.config.cache.clear_cache(request.config.cache._cachedir)

    with patch.multiple("tftest.TerragruntTest", **{cmd: DEFAULT for cmd in tf_cmds}) as mock_cmd:
        
        mock_cmd[cmd].return_value = "mock-" + cmd
        setattr(request, "param", params)

        _execute_command(request, terra, cmd)
        _execute_command(request, terra, cmd)

        if terra.tfdir in params.keys():
            params = params[terra.tfdir]

        assert mock_cmd[cmd].call_args_list == [call(**params)]

@pytest.mark.parametrize("terra", [{"binary": "terragrunt", "tfdir": "roo", "skip_teardown": True}], indirect=True)
@pytest.mark.parametrize("params", [
    {"color": True},
    {os.getcwd() + "/roo": {"color": True}}
])
@pytest.mark.parametrize("cmd", tf_cmds)
def test__execute_command_without_cache(request, terra, params, cmd):
    log.info("Clearing pytest cache")
    request.config.cache.clear_cache(request.config.cache._cachedir)

    with patch.multiple("tftest.TerragruntTest", **{cmd: DEFAULT for cmd in tf_cmds}) as mock_cmd:
        
        mock_cmd[cmd].return_value = "mock-" + cmd
        setattr(request, "param", params)

        _execute_command(request, terra, cmd)

        log.info("Clearing pytest cache")
        request.config.cache.clear_cache(request.config.cache._cachedir)

        _execute_command(request, terra, cmd)

        if terra.tfdir in params.keys():
            params = params[terra.tfdir]

        assert mock_cmd[cmd].call_args_list == [call(**params), call(**params)]
import logging
from unittest.mock import patch, call
import pytest
from tests.data import kwargs, basic_terra_factory_py

pytest_plugins = [
    str("_pytest.pytester"),
]

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

@patch("tftest.TerraformTest")
@patch("terra_fixt.TfTestCache")
def test_factory_kwargs(mock_cache, mock_tftest, pytester):
    pytester.makepyfile(basic_terra_factory_py.format(kwargs))
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)


@patch("terra_fixt.TfTestCache.get_cache")
@patch("tftest.TerraformTest.execute_command")
def test_use_cache(mock_execute, mock_get_cache, terra_factory, pytester):
    params = [
        {"binary": "terraform", "use_cache": True, "tfdir": "foo", "command": "plan"},
        {"binary": "terraform", "use_cache": False, "tfdir": "foo", "command": "apply"},
    ]
    pytester.makepyfile(basic_terra_factory_py.format(params))
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)

    for param in params:
        if param["use_cache"]:
            assert call(param["command"]) in mock_get_cache.call_args_list
        else:
            assert call(param["command"]) not in mock_get_cache.call_args_list


@patch("terra_fixt.TfTestCache.get_cache")
@patch("tftest.TerraformTest.execute_command")
def test_skip_teardown(mock_execute, mock_get_cache, pytester):
    params = [
        {
            "binary": "terraform",
            "use_cache": True,
            "tfdir": "foo",
            "command": "plan",
            "skip_teardown": True,
        },
        {
            "binary": "terraform",
            "use_cache": True,
            "tfdir": "foo",
            "command": "plan",
            "skip_teardown": False,
        },
    ]
    pytester.makepyfile(basic_terra_factory_py.format(params))
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)
    assert mock_execute.call_args_list == [
        call("destroy", "-auto-approve", "-no-color")
    ]

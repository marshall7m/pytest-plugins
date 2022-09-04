import logging
from unittest.mock import patch, call
from tests.data import all_kwargs, basic_terra_factory_py

pytest_plugins = [
    str("_pytest.pytester"),
]

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@patch("tftest.TerraformTest.execute_command")
def test_factory_kwargs(mock_execute_command, pytester):
    pytester.makepyfile(basic_terra_factory_py.format(all_kwargs))
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)


@patch("tftest.TerraformTest.plan")
def test_get_cache(mock_plan, pytester):
    params = [
        {
            "binary": "terraform",
            "put_cache": True,
            "skip_teardown": True,
            "get_cache": True,
            "tfdir": "foo",
            "command": "plan",
        },
        {
            "binary": "terraform",
            "get_cache": True,
            "skip_teardown": True,
            "tfdir": "foo",
            "command": "plan",
        },
    ]
    pytester.makepyfile(basic_terra_factory_py.format(params))
    pytester.inline_run()

    assert len(mock_plan.call_args_list) == 1


@patch("tftest.TerraformTest.destroy")
@patch("tftest.TerraformTest.execute_command")
def test_skip_teardown(mock_execute, mock_destroy, pytester):
    params = [
        {
            "binary": "terraform",
            "get_cache": True,
            "tfdir": "foo",
            "command": "plan",
            "skip_teardown": True,
        },
        {
            "binary": "terraform",
            "get_cache": True,
            "tfdir": "foo",
            "command": "plan",
            "skip_teardown": False,
        },
    ]
    pytester.makepyfile(basic_terra_factory_py.format(params))
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)
    assert mock_destroy.call_args_list == [call(auto_approve=True)]

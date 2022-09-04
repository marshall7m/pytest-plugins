import logging
from unittest.mock import patch
from tests.data import all_kwargs, basic_terra_py

pytest_plugins = [
    str("_pytest.pytester"),
]

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@patch("terra_fixt.TfTestCache")
def test_kwargs(mock_tftest_cache, pytester):
    pytester.makepyfile(basic_terra_py.format(all_kwargs))
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=len(all_kwargs))


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
    pytester.makepyfile(basic_terra_py.format(params))
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=2)
    assert len(mock_plan.call_args_list) == 1


@patch("terra_fixt.TfTestCache.run")
@patch("tftest.TerraformTest.destroy")
def test_skip_teardown(mock_destroy, mock_run, pytester):
    kwargs = [
        {
            "binary": "terraform",
            "get_cache": True,
            "tfdir": "foo",
            "command": "plan",
            "skip_teardown": True,
        }
    ]
    pytester.makepyfile(basic_terra_py.format(kwargs))
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)
    assert mock_destroy.call_args_list == []

import logging
from unittest.mock import patch, call
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


@patch("terra_fixt.TfTestCache.get_cache")
@patch("tftest.TerraformTest.destroy")
@patch("tftest.TerraformTest.apply")
def test_use_cache(mock_apply, mock_destroy, mock_get_cache, pytester):
    params = [
        {"binary": "terraform", "use_cache": True, "tfdir": "foo", "command": "plan"},
        {"binary": "terraform", "use_cache": False, "tfdir": "foo", "command": "apply"},
    ]
    pytester.makepyfile(basic_terra_py.format(params))
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=2)
    for kwargs in params:
        if kwargs["use_cache"]:
            assert call(kwargs["command"]) in mock_get_cache.call_args_list
        else:
            assert call(kwargs["command"]) not in mock_get_cache.call_args_list


@patch("terra_fixt.TfTestCache.get_cache")
@patch("tftest.TerraformTest.destroy")
def test_skip_teardown(mock_destroy, mock_get_cache, pytester):
    kwargs = [
        {
            "binary": "terraform",
            "use_cache": True,
            "tfdir": "foo",
            "command": "plan",
            "skip_teardown": True,
        }
    ]
    pytester.makepyfile(basic_terra_py.format(kwargs))
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)
    assert mock_destroy.call_args_list == []

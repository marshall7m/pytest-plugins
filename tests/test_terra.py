import pytest
import logging
from unittest.mock import patch, call
from tests.data import kwargs, basic_terra_py

pytest_plugins = [
    str("_pytest.pytester"),
]

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

kwargs_params = [pytest.param(param, id=p_id) for p_id, param in kwargs.items()]


@patch("terra_fixt.TfTestCache")
@pytest.mark.parametrize("params", kwargs_params)
def test_kwargs(mock_tftest_cache, pytester, params):
    pytester.makepyfile(basic_terra_py.format(params))
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)


@patch("terra_fixt.TfTestCache.get_cache")
@patch("tftest.TerraformTest.destroy")
def test_use_cache(mock_destroy, mock_get_cache, pytester):
    kwargs = [
        {"binary": "terraform", "use_cache": True, "tfdir": "foo", "command": "plan"}
    ]
    pytester.makepyfile(basic_terra_py.format(kwargs))
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)
    assert mock_get_cache.call_args_list == [call(kwargs["command"])]


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

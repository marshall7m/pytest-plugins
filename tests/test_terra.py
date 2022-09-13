import logging
from unittest.mock import patch

pytest_plugins = [
    str("_pytest.pytester"),
]

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

basic_terra_py = """
import pytest
import logging
import sys
import tftest

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)


@pytest.mark.parametrize("terra", {}, indirect=['terra'])
def test_terra_param(terra):
    log.debug(terra)
"""


@patch("tftest.TerraformTest.destroy")
def test_kwargs(mock_destroy, pytester):
    params = [
        {
            "binary": "terraform",
            "basedir": "/fixture",
            "tfdir": "bar",
            "env": {},
            "skip_teardown": False,
        },
        {
            "binary": "terragrunt",
            "basedir": "/fixture",
            "tfdir": "bar",
            "env": {},
            "skip_teardown": False,
            "tg_run_all": True,
        },
    ]
    pytester.makepyfile(basic_terra_py.format(params))
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=len(params))


@patch("tftest.TerraformTest.destroy")
def test_skip_teardown_param(mock_destroy, pytester):
    params = [
        {
            "binary": "terraform",
            "tfdir": "foo",
            "skip_teardown": True,
        },
        {
            "binary": "terragrunt",
            "tfdir": "foo",
            "skip_teardown": True,
        },
    ]
    pytester.makepyfile(basic_terra_py.format(params))
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=len(params))
    assert mock_destroy.call_args_list == []


@patch("tftest.TerraformTest.destroy")
def test_skip_teardown_flag(mock_destroy, pytester):
    """Ensure that the --skip-tf-destroy flag is valid"""

    pytester.makepyfile(
        basic_terra_py.format(
            [
                {
                    "binary": "terraform",
                    "tfdir": "foo",
                    "skip_teardown": True,
                },
                {
                    "binary": "terraform",
                    "tfdir": "foo",
                    "skip_teardown": False,
                },
                {
                    "binary": "terragrunt",
                    "tfdir": "foo",
                    "skip_teardown": True,
                },
                {
                    "binary": "terragrunt",
                    "tfdir": "foo",
                    "skip_teardown": False,
                },
            ]
        )
    )
    pytester.inline_run("--skip-teardown=true")

    log.info("Assert that terraform destroy command was not called")
    assert mock_destroy.call_args_list == []

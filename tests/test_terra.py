import pytest
import logging
from unittest.mock import patch, call
from tests.data import kwargs

pytest_plugins = [
    str("_pytest.pytester"),
]

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

basic_example = """
import pytest
import logging
import sys
import tftest

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)


@pytest.mark.parametrize("terra", [{}], indirect=['terra'])
def test_terra_param(terra):
    log.debug(terra)
"""
kwargs_params = [pytest.param(param, id=p_id) for p_id, param in kwargs.items()]
@patch("tftest.TerragruntTest")
@patch("tftest.TerraformTest")
@pytest.mark.parametrize("params",kwargs_params)
def test_kwargs(mock_tf, mock_tg, pytester, params):
    pytester.makepyfile(basic_example.format(params))
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)
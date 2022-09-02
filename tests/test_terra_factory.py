import logging
from unittest.mock import patch, call
import tftest
import pytest
from tests.data import kwargs

pytest_plugins = [
    str("_pytest.pytester"),
]

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

kwargs_params = [pytest.param(param, id=p_id) for p_id, param in kwargs.items()]
@pytest.mark.parametrize("kwargs", kwargs_params)
@patch("tftest.TerraformTest")
def test_factory_kwargs(terra_factory, kwargs):
    log.debug(terra_factory(**kwargs))


@patch("tftest.TerraformTest")
def test_factory_teardown(mock_tf, pytester):
    pytester.makepyfile(f"""
    import pytest
    import logging

    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)


    def test_terra_factory(terra_factory):
        terra_factory(binary="terraform", tfdir="foo", command="plan")

    """
    )
    reprec = pytester.inline_run()
    reprec.assertoutcome(passed=1)

    assert mock_tf.return_value.destroy.call_count == 1

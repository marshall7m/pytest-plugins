from unittest import mock
import pytest
import logging
import sys
import os
from unittest.mock import patch, call
from pytest import Pytester
import tftest


pytest_plugins = [
    str('_pytest.pytester'),
]

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)

def test_factory_return_value(tf_factory, terraform_version):
    tf = tf_factory("./")
    assert isinstance(tf, tftest.TerraformTest)


@patch("tftest.TerraformTest")
def test_factory_kwargs(mock_tftest, tf_factory):
    tf_factory(tf_dir="./fixture", base_dir="./", binary="terraform", env={"foo": "bar"})
    assert mock_tftest.call_args_list == [call(tf_dir='./fixture', base_dir='./', binary='terraform', env={'foo': 'bar'})]


@patch("tftest.TerraformTest")
def test_factory_args(mock_tftest, tf_factory):
    tf_factory("./fixture", "./", "terraform", {"foo": "bar"})
    assert mock_tftest.call_args_list == [call("./fixture", "./", "terraform", {"foo": "bar"})]


@patch("tftest.TerraformTest")
def test_factory_teardown(mock_tftest, pytester, tf_factory):
    count = 5
    pytester.makepyfile(f"""
    import pytest
    import logging
    import sys

    log = logging.getLogger(__name__)
    stream = logging.StreamHandler(sys.stdout)
    log.addHandler(stream)
    log.setLevel(logging.DEBUG)


    @pytest.mark.parametrize("terraform_version", ["latest"], indirect=True)
    def test_tf(tf_factory, terraform_version):
        tfs = [tf_factory('./fixtures-%'.format(n)) for n in range({count})]

    """)

    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)

    assert mock_tftest.return_value.destroy.call_count == count

    
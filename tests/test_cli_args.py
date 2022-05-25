from unittest import mock
import pytest
import logging
import sys
import os
import json
from unittest.mock import patch, call
from pytest import Pytester
pytest_plugins = [
    str('_pytest.pytester'),
]

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)

test_content = [
    pytest.param("""
    import pytest
    import logging
    import sys

    log = logging.getLogger(__name__)
    stream = logging.StreamHandler(sys.stdout)
    log.addHandler(stream)
    log.setLevel(logging.DEBUG)


    @pytest.mark.parametrize("terraform_version", ["latest"], indirect=True)
    @pytest.mark.parametrize("tf", ['./'], indirect=True)
    def test_tf(tf, terraform_version):
        log.debug(tf)

        tf.apply(auto_approve=True)
    """, id='tf'),
    pytest.param("""
    import pytest
    import logging
    import sys

    log = logging.getLogger(__name__)
    stream = logging.StreamHandler(sys.stdout)
    log.addHandler(stream)
    log.setLevel(logging.DEBUG)


    @pytest.mark.parametrize("terraform_version", ["latest"], indirect=True)
    def test_tf(tf_factory, terraform_version):
        tf = tf_factory('./')

        tf.apply(auto_approve=True)
    """, id='tf_factory')
]


@patch("tftest.TerraformTest")
@pytest.mark.parametrize('content', test_content)
def test_skip_init(mock_tftest, pytester, content):
    '''Ensure that the --skip-tf-init flag is valid'''
    pytester.makepyfile(content)
    reprec = pytester.inline_run("--skip-tf-init")

    reprec.assertoutcome(passed=1)

    mock_tftest.return_value.setup.assert_not_called()

@patch("tftest.TerraformTest")
@pytest.mark.parametrize('content', test_content)
def test_skip_destroy(mock_tftest, pytester, content):
    '''Ensure that the --skip-tf-destroy flag is valid'''

    pytester.makefile(".tf", json.dumps("""
    output "foo" {
        value = "bar"
    }
    """))
    pytester.makepyfile(content)
    reprec = pytester.inline_run("--skip-tf-destroy")

    reprec.assertoutcome(passed=1)

    log.info('Assert correct tf.setup() arguments were passed')
    setup_call = mock_tftest.return_value.setup.call_args
    log.debug(f'Args:\n{setup_call}')
    assert setup_call.kwargs['cleanup_on_exit'] == False

    log.info('Assert tf.destroy() was not called')
    mock_tftest.return_value.destroy.assert_not_called()


@pytest.mark.parametrize('content', test_content)
def test_skip_destroy_backend_preserved(pytester, content):
    '''
    Ensure that the tf fixture's associated local terraform.tfstate file
    is preserved when the --skip-tf-destroy flag is passed
    '''

    log.info('Creating Terraform configurations')
    data = """
output "foo" {
    value = "bar"
}
    """
    with open(f"{str(pytester.path)}/main.tf", "w+") as f:
        f.writelines(data)

    pytester.makepyfile(content)
    reprec = pytester.inline_run("--skip-tf-destroy")

    reprec.assertoutcome(passed=1)
    
    log.info('Assert terraform.tfstate file still exists')
    state_path = pytester.path / 'terraform.tfstate'
    assert state_path.exists() is True

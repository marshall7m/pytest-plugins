import pytest
import logging
import sys
from unittest.mock import patch
import tftest

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)

def pytest_generate_tests(metafunc):
    if 'tf' in metafunc.fixturenames:
        metafunc.parametrize('tf', ['module'], indirect=True, scope='session')
    if 'terraform_version' in metafunc.fixturenames:
        tf_versions = [pytest.param('latest')]
        metafunc.parametrize('terraform_version', tf_versions, indirect=True, scope='session', ids=[f'tf_{v.values[0]}' for v in tf_versions])

@pytest.mark.usefixtures('tf', 'terraform_version')
def test_plan(tf_plan):
    response = tf_plan()
    response['output'].outputs['foo'] == 'bar'

@pytest.mark.usefixtures('tf', 'terraform_version')
def test_apply(tf_apply):
    tf_apply()

@pytest.mark.usefixtures('tf', 'terraform_version')
def test_output(tf_apply, tf_output):
    log.debug('Running Terraform apply')
    tf_apply()

    log.debug(f'Terraform Output:\n{tf_output}')
    assert tf_output['foo'] == 'bar'
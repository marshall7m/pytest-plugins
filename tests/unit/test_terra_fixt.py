import pytest
import logging
import sys

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)

def pytest_generate_tests(metafunc):
    if 'tf' in metafunc.fixturenames:
        metafunc.parametrize('tf', ['fixtures'], indirect=True, scope='session')
    if 'terraform_version' in metafunc.fixturenames:
        tf_versions = [pytest.param('latest')]
        metafunc.parametrize('terraform_version', tf_versions, indirect=True, scope='session', ids=[f'tf_{v.values[0]}' for v in tf_versions])

def test_plan(tf, terraform_version, tf_plan):
    assert tf_plan.outputs['foo'] == 'bar'

def test_apply(tf, terraform_version, tf_apply):
    assert tf_apply != None

def test_output(tf, terraform_version, tf_output):
    log.debug(f'Terraform Output:\n{tf_output}')
    assert tf_output['foo'] == 'bar'
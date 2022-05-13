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
        metafunc.parametrize('tf', ['fixtures'], indirect=True, scope='session')
    if 'terraform_version' in metafunc.fixturenames:
        tf_versions = [pytest.param('latest')]
        metafunc.parametrize('terraform_version', tf_versions, indirect=True, scope='session', ids=[f'tf_{v.values[0]}' for v in tf_versions])

@pytest.mark.usefixtures('terraform_version')
def test_plan(tf, tf_plan):
    with patch.object(tf, 'plan', wraps=tf.plan) as wrap_plan:
        response = tf_plan()
        assert response['output'].outputs['foo'] == 'bar'
        assert tf_plan(update=False) == response
        assert wrap_plan.call_count == 1

@pytest.mark.usefixtures('terraform_version')
def test_apply(tf, tf_apply):
    with patch.object(tf, 'apply', wraps=tf.apply) as wrap_apply:
        response = tf_apply()
        assert tf_apply(update=False) == response
        assert wrap_apply.call_count == 1

@pytest.mark.usefixtures('tf', 'terraform_version')
def test_output(tf_apply, tf_output):
    log.debug('Running Terraform apply')
    tf_apply()

    log.debug(f'Terraform Output:\n{tf_output}')
    assert tf_output['foo'] == 'bar'
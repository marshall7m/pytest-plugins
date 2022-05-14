from numpy import kaiser
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
    '''Ensure that the fixture runs tf.plan() and returns the plan output'''
    with patch.object(tf, 'plan', wraps=tf.plan) as wrap_plan:
        response = tf_plan()

        log.info('Assert that fixture return value is valid')
        assert response['output'].outputs['doo'] == 'roo'
        assert tf_plan(update=False) == response

        #Ensure that the `update=False` argumet prevents the fixture from calling the Terraform command but asserting that tftest method was called once
        log.info('Assert that the tf.plan() command was called only once')
        assert wrap_plan.call_count == 1

@pytest.mark.usefixtures('terraform_version')
def test_apply(tf, tf_apply):
    '''Ensure that the fixture runs tf.apply()'''
    with patch.object(tf, 'apply', wraps=tf.apply) as wrap_apply:
        response = tf_apply()
        assert tf_apply(update=False) == response

        #Ensure that the `update=False` argumet prevents the fixture from calling the Terraform command but asserting that tftest method was called once
        log.info('Assert that the tf.apply() command was called only once')
        assert wrap_apply.call_count == 1

@pytest.mark.usefixtures('tf', 'terraform_version')
def test_output(tf_apply, tf_output):
    '''Ensure that the fixture returns the output of tf.outputs()'''
    log.debug('Running Terraform apply')
    tf_apply()

    log.info('Assert that fixture return value is valid')
    log.debug(f'Terraform Output:\n{tf_output}')
    assert tf_output['foo'] == 'bar'


@pytest.mark.usefixtures('tf', 'terraform_version')
def test_plan_tf_vars(tf_plan):
    '''Ensure that the tf_vars argument is properly passed to the tf.plan() method'''
    tf_vars = {
        'foo': 'bar',
        'baz': [
            {
                'string_attr': 'zoo',
                'number_attr': 1,
                'bool_attr': False
            }
        ]
    }
    response = tf_plan(**tf_vars)

    for var in tf_vars.keys():
        assert response['output'].outputs[var] == tf_vars[var]

@pytest.mark.usefixtures('tf', 'terraform_version')
def test_apply_tf_vars(tf, tf_apply):
    '''Ensure that the tf_vars argument is properly passed to the tf.apply() method'''
    tf_vars = {
        'foo': 'bar',
        'baz': [
            {
                'string_attr': 'zoo',
                'number_attr': 1,
                'bool_attr': False
            }
        ]
    }
    tf_apply(**tf_vars)


    tf_output = tf.output()

    for var in tf_vars.keys():
        assert tf_output[var] == tf_vars[var]
import pytest
import logging
import sys
import os

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)

@pytest.mark.usefixtures("terraform_version")
@pytest.mark.parametrize('tf_plan', [f'{os.path.dirname(__file__)}/fixtures'], indirect=True)
def test_plan_param(tf, tf_plan):
    """Ensure that the fixture runs tf.plan() and returns the plan output"""
    log.debug(f'Plan:\n{tf_plan}')

    log.info('Assert that the parametrized fixture is not callable as a factory fixture')
    with pytest.raises(TypeError):
        tf_plan()


@pytest.mark.usefixtures("terraform_version")
@pytest.mark.parametrize('tf_apply', [f'{os.path.dirname(__file__)}/fixtures'], indirect=True)
def test_apply_param(tf_apply):
    """Ensure that the parametrized fixture runs tf.apply() and returns the apply output"""
    log.debug(f'Apply:\n{tf_apply}')

    log.info('Assert that the parametrized fixture is not callable as a factory fixture')
    with pytest.raises(TypeError):
        tf_apply()


@pytest.mark.usefixtures("terraform_version")
@pytest.mark.parametrize('tf_output', [f'{os.path.dirname(__file__)}/fixtures'], indirect=True)
def test_output_param(tf_output):
    """Ensure that the fixture runs tf.output() and returns the output"""
    log.debug(f'Output:\n{tf_output}')

    log.info('Assert that the parametrized fixture is not callable as a factory fixture')
    with pytest.raises(TypeError):
        tf_output()
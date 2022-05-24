import pytest
from unittest.mock import patch
import logging
import sys

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)


@pytest.mark.usefixtures("terraform_version")
def test_plan_update(tf, tf_plan):
    """
    Ensure that the first call of the factory fixture runs tf.plan() and
    returns a valid plan output and the second call returns the cached output
    """
    with patch.object(tf, "plan", wraps=tf.plan) as wrap_plan:
        response = tf_plan()

        log.info("Assert that fixture return value is valid")
        assert response.outputs["doo"] == "roo"

        log.info("Assert both calls output are identical")
        assert tf_plan(update=False) == response

        log.info("Assert that Terraform command was called only once")
        assert wrap_plan.call_count == 1


@pytest.mark.usefixtures("terraform_version")
def test_apply_update(tf, tf_apply):
    """
    Ensure that the first call of the factory fixture runs tf.apply() and
    returns a valid apply output and the second call returns the cached output
    """
    with patch.object(tf, "apply", wraps=tf.apply) as wrap_apply:
        tf.init()
        response = tf_apply()

        log.info("Assert both calls output are identical")
        assert tf_apply(update=False) == response

        log.info("Assert that Terraform command was called only once")
        assert wrap_apply.call_count == 1


@pytest.mark.usefixtures("tf", "terraform_version")
def test_output_update(tf, tf_apply, tf_output):
    """
    Ensure that the first call of the factory fixture runs tf.output() and
    returns a valid output and the second call returns the cached output
    """
    log.info("Running Terraform Apply")
    tf_apply()

    with patch.object(tf, "output", wraps=tf.output) as wrap_output:
        response = tf_output()

        log.info("Assert that fixture return value is valid")
        assert response["foo"] == "bar"

        log.info("Assert both calls output are identical")
        assert tf_output(update=False) == response

        log.info("Assert that Terraform command was called only once")
        assert wrap_output.call_count == 1

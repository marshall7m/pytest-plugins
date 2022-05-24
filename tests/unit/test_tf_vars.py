import pytest
import logging
import sys

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)

@pytest.mark.usefixtures("tf", "terraform_version")
def test_plan_tf_vars(tf_plan):
    """Ensure that the tf_vars argument is properly passed to tf.plan()"""
    tf_vars = {
        "foo": "bar",
        "baz": [{"string_attr": "zoo", "number_attr": 1, "bool_attr": False}],
    }
    response = tf_plan(**tf_vars)

    for var in tf_vars.keys():
        assert response.outputs[var] == tf_vars[var]


@pytest.mark.usefixtures("tf", "terraform_version")
def test_apply_tf_vars(tf, tf_apply):
    """Ensure that the tf_vars argument is properly passed to tf.apply()"""
    tf_vars = {
        "foo": "bar",
        "baz": [{"string_attr": "zoo", "number_attr": 1, "bool_attr": False}],
    }
    tf_apply(**tf_vars)
    tf_output = tf.output()

    for var in tf_vars.keys():
        assert tf_output[var] == tf_vars[var]

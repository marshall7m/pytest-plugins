import pytest
import os
import logging
import sys
from pytest_jsonreport.plugin import JSONReport
from unittest.mock import patch

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)


@patch("tftest.TerraformTest")
def test_skip_tf_plan(mock_tf_test):
    """
    Ensures that the `terraform plan` command is not executed and
    tests that depend on and/or use the tf_plan fixture are skipped
    """
    plugin = JSONReport()
    os.chdir(f"{os.path.dirname(__file__)}/fixtures")
    pytest.main(
        ["--skip-tf-plan", "--json-report-file=none", "test_tf.py"],
        plugins=[plugin],
    )
    summary = plugin.report["summary"]
    log.debug(f"Test Summary:\n{summary}")

    mock_tf_test.plan.assert_not_called()
    assert summary["skipped"] == 1


@patch("tftest.TerraformTest")
def test_skip_tf_apply(mock_tf_test):
    """
    Ensures that the `terraform apply` command is not executed
    and tests that depend on and/or use the tf_apply fixture are skipped
    """
    plugin = JSONReport()
    os.chdir(f"{os.path.dirname(__file__)}/fixtures")
    pytest.main(
        ["--skip-tf-apply", "--json-report-file=none", "test_tf.py"],
        plugins=[plugin],
    )
    summary = plugin.report["summary"]
    log.debug(f"Test Summary:\n{summary}")

    mock_tf_test.apply.assert_not_called()
    # skips tf.apply() in test_apply() and test_output()
    assert summary["skipped"] == 2


@patch("tftest.TerraformTest")
def test_skip_tf_destroy(mock_tf_test):
    """
    Ensures that the `terraform destroy` command
    is not executed on teardown
    """
    # patch tf plan resource attr within test_plan()
    mock_tf_plan = mock_tf_test.return_value.plan.return_value
    mock_tf_plan.outputs.__getitem__.return_value = "bar"

    # patch tf output within test_output()
    mock_tf_test.return_value.output.return_value = {"foo": "bar"}
    plugin = JSONReport()
    os.chdir(f"{os.path.dirname(__file__)}/fixtures")

    pytest.main(
        ["--skip-tf-destroy", "--json-report-file=none", "test_tf.py"],
        plugins=[plugin],
    )
    summary = plugin.report["summary"]
    log.debug(f"Test Summary:\n{summary}")

    mock_tf_test.destroy.assert_not_called()
    assert summary["skipped"] == 0


def test_skip_tf_destroy_backend_preserved():
    """
    Ensures that the Terraform configuration's tfstate file
    still exists after the Pytest execution is finished
    """
    tf_dir = f"{os.path.dirname(__file__)}/fixtures"
    expected_tf_state_path = (
        f"{os.path.dirname(__file__)}" "/fixtures/module/terraform.tfstate"
    )
    os.chdir(tf_dir)
    try:
        pytest.main(
            [
                "--skip-tf-destroy",
                "--json-report-file=none",
                "test_tf.py",
            ]
        )
        log.info(f"Assert tfstate file exists: {expected_tf_state_path}")
        assert os.path.exists(expected_tf_state_path) is True
    except Exception as e:
        log.error(e, exc_info=True)
        raise e
    finally:
        log.info(f"Removing file: {expected_tf_state_path}")
        os.remove(expected_tf_state_path)

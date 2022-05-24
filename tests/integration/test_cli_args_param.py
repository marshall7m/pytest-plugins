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
    Ensures that the `terraform plan` command is not executed
    and tests that depend on and/or use the tf_plan fixture are skipped
    """
    plugin = JSONReport()
    os.chdir(f"{os.path.dirname(__file__)}/fixtures")
    pytest.main(
        ["--skip-tf-plan", "--json-report-file=none", "test_tf_param.py"],
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
        ["--skip-tf-apply", "--json-report-file=none", "test_tf_param.py"],
        plugins=[plugin],
    )
    summary = plugin.report["summary"]
    log.debug(f"Test Summary:\n{summary}")

    mock_tf_test.apply.assert_not_called()
    assert summary["skipped"] == 1
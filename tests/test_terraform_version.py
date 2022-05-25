from unittest import mock
import pytest
import logging
import sys
import os
from unittest.mock import patch, call
from pytest import Pytester
pytest_plugins = [
    str('_pytest.pytester'),
]

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)

basic_example = """
import pytest
import logging
import sys
import subprocess
import json

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)


@pytest.mark.parametrize("terraform_version", {}, indirect=True)
def test_version(terraform_version):
    log.debug('Terraform Version %'.format(terraform_version))

    actual_version = json.loads(subprocess.run(
        ["terraform", "--version", "-json"],
        capture_output=True, text=True
    ).stdout)['terraform_version']
    assert actual_version == terraform_version
"""

def test_terraform_version(pytester):
    '''Ensure that the terraform_version fixture changes the Terraform version being used'''
    versions = ['1.0.0', '0.15.0', 'non-existent-version']
    pytester.makepyfile(basic_example.format(versions))
    reprec = pytester.inline_run()
    reprec.assertoutcome(passed=2, failed=1)
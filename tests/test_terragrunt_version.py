import logging
import sys

pytest_plugins = [
    str("_pytest.pytester"),
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
import re

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)


@pytest.mark.parametrize(
    "terragrunt_version",
    ["0.38.0", "0.37.4", "non-existent-version"],
    indirect=True
)
def test_version(terragrunt_version):
    log.debug(f'Expected Terragrunt version {terragrunt_version}')

    parsed_version = re.search(
        r'(?<=v)[0-9]+\\.[0-9]+\\.[0-9]+',
        subprocess.run(
            ["terragrunt", "--version"],
            capture_output=True, text=True
        ).stdout
    )
    log.debug(f'Parsed actual version: {parsed_version}')

    assert parsed_version.group(0) == terragrunt_version
"""


def test_terragrunt_version(pytester):
    """
    Ensure that the terragrunt_version fixture changes the
    terragrunt version being used
    """
    pytester.makepyfile(basic_example)
    reprec = pytester.inline_run()
    reprec.assertoutcome(passed=2, failed=1)

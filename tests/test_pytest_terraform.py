import pytest
import logging
import sys

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)

@pytest.mark.parametrize('tf', ['fixtures'], indirect=True)
@pytest.mark.parametrize('terraform_version', ['latest'], indirect=True)
def test_plan(tf, terraform_version, tf_plan):
    tf_plan()
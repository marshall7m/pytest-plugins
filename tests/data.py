all_kwargs = [
    {
        "binary": "terraform",
        "basedir": "/fixture",
        "tfdir": "bar",
        "env": {},
        "command": "apply",
        "skip_teardown": False,
        "get_cache": False,
        "extra_args": {"auto_approve": True},
    },
    {
        "binary": "terragrunt",
        "basedir": "/fixture",
        "tfdir": "bar",
        "env": {},
        "tg_run_all": False,
        "command": "apply",
        "skip_teardown": False,
        "get_cache": False,
        "extra_args": {"auto_approve": True},
    },
]


basic_terra_py = """
import pytest
import logging
import sys
import tftest

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)


@pytest.mark.parametrize("terra", {}, indirect=['terra'])
def test_terra_param(terra):
    log.debug(terra)
"""

basic_terra_factory_py = """
import pytest
import logging
import sys
import tftest

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)

data = {}

def test_terra_factory(terra_factory):
    for param in data:
        terra_factory(**param)
"""

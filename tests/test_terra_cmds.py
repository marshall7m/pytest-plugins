import logging
from unittest.mock import patch, call
import tftest
import pytest
import os
import json
from terra_fixt import OverrideTfTest

pytest_plugins = [
    str("_pytest.pytester"),
]

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def pytest_generate_tests(metafunc):
    if "terra" not in metafunc.fixturenames:
        metafunc.fixturenames.append("terra")
    metafunc.parametrize("terra", [
        {
            "binary": "terraform",
            "tfdir": os.path.dirname(__file__) + "/tfdir"
        },
        {
            "binary": "terragrunt",
            "tfdir": os.path.dirname(__file__) + "/tfdir"
        }
    ], indirect=True)


def test_terra(terra):
    pass

def test_terra_setup(terra_setup):
    assert type(terra_setup) == str

@pytest.mark.parametrize("terra_plan", [{"output": True}], indirect=True)
def test_terra_plan(terra_plan):
    assert isinstance(terra_plan, OverrideTfTest)
    assert hasattr(terra_plan, "outputs")
    assert hasattr(terra_plan, "resources")


def test_terra_apply(terra_apply):
    assert type(terra_apply) == str


def test_terra_output(terra_output):
    assert isinstance(terra_output, tftest.TerraformValueDict)
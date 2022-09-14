import logging
import tftest
import pytest
import os

pytest_plugins = [
    str("_pytest.pytester"),
]

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def pytest_generate_tests(metafunc):
    metafunc.parametrize(
        "terra",
        [
            {"binary": "terraform", "tfdir": os.path.dirname(__file__) + "/tfdir"},
            {"binary": "terragrunt", "tfdir": os.path.dirname(__file__) + "/tfdir"},
        ],
        indirect=True,
    )


@pytest.mark.usefixtures("terra")
class TestTerraCommands:
    def test_terra_setup(self, terra_setup):
        assert type(terra_setup) == str

    @pytest.mark.parametrize("terra_plan", [{"output": True}], indirect=True)
    def test_terra_plan(self, terra_plan):
        assert isinstance(terra_plan, tftest.TerraformPlanOutput)

    def test_terra_apply(self, terra_apply):
        assert type(terra_apply) == str

    def test_terra_output(self, terra_output):
        assert isinstance(terra_output, tftest.TerraformValueDict)

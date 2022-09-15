import logging
import os

pytest_plugins = [
    str("_pytest.pytester"),
]

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# asserts tftest.TerraformTest method outputs are returned
test_without_cache_file = """
import tftest
import pytest
import os

def pytest_generate_tests(metafunc):
    metafunc.parametrize("terra",{terra_param},indirect=True,)


@pytest.mark.usefixtures("terra")
class TestTerraCommands:
    def test_terra_setup(self, terra_setup):
        assert type(terra_setup) == str

    @pytest.mark.parametrize("terra_plan", [{{"output": True}}], indirect=True)
    def test_terra_plan(self, terra_plan):
        assert isinstance(terra_plan, tftest.TerraformPlanOutput)

    def test_terra_apply(self, terra_apply):
        assert type(terra_apply) == str

    def test_terra_output(self, terra_output):
        assert isinstance(terra_output, tftest.TerraformValueDict)
"""

# asserts tftest.TerraformTest method outputs are returned and there associated
# patches are not called
test_with_cache_file = """
import tftest
import pytest
import os
from unittest.mock import patch

def pytest_generate_tests(metafunc):
    metafunc.parametrize("terra",{terra_param},indirect=True,)


@pytest.mark.usefixtures("terra")
class TestTerraCommands:
    # tftest.TerragruntTest methods don't need to be patched since
    # it uses tftest.TerraformTest methods
    @patch("tftest.TerraformTest.setup")
    def test_terra_setup(self, mock_setup, terra_setup):
        assert type(terra_setup) == str
        assert mock_setup.call_args_list == []

    @pytest.mark.parametrize("terra_plan", [{{"output": True}}], indirect=True)
    @patch("tftest.TerraformTest.plan")
    def test_terra_plan(self, mock_plan, terra_plan):
        assert isinstance(terra_plan, tftest.TerraformPlanOutput)
        assert mock_plan.call_args_list == []

    @patch("tftest.TerraformTest.apply")
    def test_terra_apply(self, mock_apply, terra_apply):
        assert type(terra_apply) == str
        assert mock_apply.call_args_list == []


    @patch("tftest.TerraformTest.output")
    def test_terra_output(self, mock_output, terra_output, terra):
        assert isinstance(terra_output, tftest.TerraformValueDict)
        assert mock_output.call_args_list == []
"""


def test_terra_fixt_without_cache(pytester):
    """Ensure terra command fixtures run without error"""
    pytester.makepyfile(
        test_without_cache_file.format(
            terra_param=[
                {
                    "binary": "terraform",
                    "tfdir": os.path.dirname(__file__) + "/fixtures",
                },
                {
                    "binary": "terragrunt",
                    "tfdir": os.path.dirname(__file__) + "/fixtures",
                },
            ]
        )
    )
    log.info("Running test file without cache")
    reprec = pytester.inline_run("--cache-clear")
    reprec.assertoutcome(passed=sum(reprec.countoutcomes()))


def test_terra_fixt_with_cache(pytester):
    """Ensure cache is used for subsequent pytest session"""
    log.info("Running test file without cache")
    pytester.makepyfile(
        test_without_cache_file.format(
            terra_param=[
                {
                    "binary": "terraform",
                    "tfdir": os.path.dirname(__file__) + "/fixtures",
                },
                {
                    "binary": "terragrunt",
                    "tfdir": os.path.dirname(__file__) + "/fixtures",
                },
            ]
        )
    )
    # --cache-clear removes .pytest_cache cache files
    reprec = pytester.inline_run("--cache-clear")
    reprec.assertoutcome(passed=sum(reprec.countoutcomes()))

    log.info("Running test file with cache")
    pytester.makepyfile(
        test_with_cache_file.format(
            terra_param=[
                {
                    "binary": "terraform",
                    "tfdir": os.path.dirname(__file__) + "/fixtures",
                },
                {
                    "binary": "terragrunt",
                    "tfdir": os.path.dirname(__file__) + "/fixtures",
                },
            ]
        )
    )
    reprec = pytester.inline_run()
    reprec.assertoutcome(passed=sum(reprec.countoutcomes()))

import pytest
import logging
import sys
from unittest.mock import patch, call

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
import tftest

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)


@pytest.mark.parametrize("terraform_version", ["latest"], indirect=True)
@pytest.mark.parametrize("tf", [{}], indirect=['tf'])
def test_tf(tf):
    log.debug(tf)
"""


@patch("tftest.TerraformTest")
@pytest.mark.parametrize(
    "params,expected_call",
    [
        pytest.param(
            ["./fixtures", "./", "terraform", {"bar": "foo"}],
            call("./fixtures", "./", "terraform", {"bar": "foo"}),
            id="args",
        ),
        pytest.param(
            {
                "tf_dir": "./fixtures",
                "base_dir": "./",
                "binary": "terraform",
                "env": {"bar": "foo"},
            },
            call(
                tf_dir="./fixtures",
                base_dir="./",
                binary="terraform",
                env={"bar": "foo"},
            ),
            id="kwargs",
        ),
        pytest.param("'./fixtures'", call("./fixtures"), id="arg"),
    ],
)
def test_fixt_arguments(mock_tftest, pytester, params, expected_call):
    pytester.makepyfile(basic_example.format(params))
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)

    assert mock_tftest.call_args_list == [expected_call]

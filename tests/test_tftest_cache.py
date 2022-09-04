import pytest
from unittest.mock import patch
from terra_fixt import TfTestCache


@pytest.mark.parametrize("cmd", ["plan", "apply", "destroy", "init", "state_pull"])
def test_get_cache(cmd):

    cache = TfTestCache(binary="terraform", tfdir="foo")
    with patch(f"tftest.TerraformTest.{cmd}") as mock_cmd:
        output = cache.run(cmd)
        cached_output = cache.run(cmd, get_cache=True)

        assert output == cached_output

        mock_cmd.called_once()

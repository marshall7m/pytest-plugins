# pytest-terra-fixt
 
With the use of this plugin, users can run Terragrunt and Terraform commands within parametrizable Pytest fixtures. Under the hood, the fixtures within this plugin use the awesome [tftest](https://github.com/GoogleCloudPlatform/terraform-python-testing-helper) Python package. In addition, given the lengthy time it takes to set up Terraform configurations, the fixtures use the PyTest built-in [config.cache](https://docs.pytest.org/en/7.1.x/how-to/cache.html#cache) fixture to cache Terraform results that can be accessed across PyTest sessions.

## Fixtures

All fixtures below can be parametrized via (`@pytest.mark.parametrize()`)

`terra`:
   - Scope: Session
   - Parameters [Required]:
      - `binary`: Path to binary (must end with `terraform` or `terragrunt)
      - `tfdir`: Absolute or relative path to `basedir`
      - `basedir`: Base directory for `tfdir` (defaults to cwd)
      - `env`: Environment variables to pass to the command
      - `skip_teardown`: Skips running fixture's teardown logic
   - Yield: Either the `tftest.TerragruntTest` or `tftest.TerraformTest` class depending on the `binary` parameter
   - Teardown: Runs `terraform destroy -auto-approve` on the `tfdir` directory if `skip_teardown` is set to `False`

`terra_setup`
   - Scope: Function
   - Parameters [Optional]: 
      A: Dictionary of keyword arguments to passed to the `tftest.TerraformTest.setup()` method
      B: Dictionary of terra directories and their respective keyword arguments to pass to the method mentioned above
   - Returns: The `terra` fixture's associated setup output

`terra_plan`
   - Scope: Function
   - Parameters [Optional]: 
      A: Dictionary of keyword arguments to passed to the `tftest.TerraformTest.plan()` method
      B: Dictionary of terra directories and their respective keyword arguments to pass to the method mentioned above
   - Returns: The `terra` fixture's associated plan output

`terra_apply`
   - Scope: Function
   - Parameters [Optional]: 
      A: Dictionary of keyword arguments to passed to the `tftest.TerraformTest.apply()` method
      B: Dictionary of terra directories and their respective keyword arguments to pass to the method mentioned above
   - Returns: The `terra` fixture's associated apply output

`terra_output`
   - Scope: Function
   - Parameters [Optional]:
      A: Dictionary of keyword arguments to passed to the `tftest.TerraformTest.output()` method
      B: Dictionary of terra directories and their respective keyword arguments to pass to the method mentioned above
   - Returns: The `terra` fixture's associated output

## CLI Arguments

`--skip-teardown`: Skips running `terraform destroy -auto-approve` on teardown and preserves the Terraform backend tfstate for future testing. This flag is useful for checking out the Terraform resources within the cloud provider console or for running experimental tests without having to wait for the resources to spin up after every Pytest invocation.
 
   ```
   NOTE: To continually preserve the Terraform tfstate, the `--skip-teardown` flag or the `"skip_teardown": True` attribute within the `terra` fixture parameters needs to be always present. If not, the `terra` fixture's teardown may destroy the Terraform resources and remove the tfstate files.
   ```
 
## Examples

`conftest.py`
```
import pytest

def pytest_generate_tests(metafunc):
    if "terra" in metafunc.fixturenames:
        metafunc.parametrize(
            "terra",
            [
                pytest.param(
                    {
                        "binary": "terraform",
                        "skip_teardown": True,
                        "env": {
                           "TF_VAR_foo": "bar"
                        },
                        "tfdir": "fixtures",
                    },
                )
            ],
            indirect=True,
            scope="session",
        )
```

`test_tf.py`
```
import pytest

@pytest.mark.usefixtures("terra_setup", "terra_apply")
class TestModule:

   @pytest.mark.parametrize("terra_plan", [{"extra_files": ["plan.tfvars"]}])
   def test_plan(self, terra, terra_plan):
      assert terra_plan["bar"] == "zoo"

   def test_out(self, terra, terra_output):
      assert terra_output["doo"] == "foo"
```

## Installation

Install via Pip:
```
pip install pytest-terra-fixt
```
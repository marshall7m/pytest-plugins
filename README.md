# pytest-terra-fixt
 
With the use of this plugin, users can run Terragrunt and Terraform commands within Pytest fixtures. Under the hood, the fixtures within this plugin use the awesome [tftest](https://github.com/GoogleCloudPlatform/terraform-python-testing-helper) Python package. 

## Fixtures

`terra`:
   - Scope: Function
   - Input: (passed within `pytest.mark.parametrize("terra", [{<input>}]))
      - `command`: Terraform or Terragrunt command to run (e.g. init, plan, apply)
      - `binary`: Path to binary (must end with `terraform` or `terragrunt)
      - `tfdir`: Absolute or relative path to `basedir`
      - `basedir`: Base directory for `tfdir` (defaults to cwd)
      - `env`: Environment variables to pass to the command
      - `skip_teardown`: Skips running fixture's teardown logic
      - `get_cache`: If `True`, gets command output from `terra_cache` fixture
      - `extra_args`: Dictionary of extra arguments to pass to the command
   - Setup: Updates cache with selected kwargs provided
   - Yield: If `get_cache` is `True`, yields output for the input `command` from the `terra_cache` fixture. If `get_cache` is `False`, yields output from the execution of the command
   - Teardown: Runs `terraform destroy -auto-approve` on the input `tfdir` directory

`terra_factory`: 
   - Scope: Session
   - Input: (passed within `pytest.mark.parametrize("terra", [{<input>}]))
      - `command`: Terraform or Terragrunt command to run (e.g. init, plan, apply)
      - `binary`: Path to binary (must end with `terraform` or `terragrunt)
      - `tfdir`: Absolute or relative path to `basedir`
      - `basedir`: Base directory for `tfdir` (defaults to cwd)
      - `env`: Environment variables to pass to the command
      - `skip_teardown`: Skips running fixture's teardown logic
      - `get_cache`: If `True`, gets command output from `terra_cache` fixture
      - `extra_args`: Dictionary of extra arguments to pass to the command
   - Setup: Updates cache with selected kwargs provided
   - Yield: If `get_cache` is `True`, yields output for the input `command` from the `terra_cache` fixture. If `get_cache` is `False`, yields output from the execution of the command
   - Teardown: Runs `terraform destroy -auto-approve` on every factory instance's input `tfdir` directory
 
`terra_cache`: 
   - Scope: Session
   - Setup: Runs `terraform init` on the specified directory
   - Yield: Factory fixture that returns a `tftest.TerraformTest` or `tftest.TerragruntTest` object that can run subsequent methods with
   - Teardown: Clears cache dictionary

## CLI Arguments

`--skip-teardown`: Skips running `terraform destroy -auto-approve` on teardown and preserves the Terraform backend tfstate for future testing. This flag is useful for checking out the Terraform resources within the cloud provider console or for running experimental tests without having to wait for the resources to spin up after every Pytest invocation.
 
   ```
   NOTE: To continually preserve the Terraform tfstate, the --skip-teardown flag needs to be always present, or else the `terra` or `terra_factory` fixtures' teardown may destroy the Terraform resources and remove the tfstate file.
   ```
 
## Examples

### Returns tftest object

`terra`
```
import pytest

@pytest.mark.parametrize("terra", [
   {
      "binary": "terraform",
      "tfdir": "bar",
      "env": {
         "TF_LOG": "DEBUG"
      },
      "skip_teardown": False,
   }
], indirect=['terra'])
def test_terra_param(terra):
   terra.apply(auto_approve=True)
   output = terra.output()
   assert output["doo"] == "foo"
```

### Run commands within fixture:

`terra`
```
import pytest

@pytest.mark.parametrize("terra", [
   {
      "binary": "terraform",
      "command": "apply",
      "tfdir": "bar",
      "env": {
         "TF_LOG": "DEBUG"
      },
      "skip_teardown": False,
      "get_cache": False,
      "extra_args": {"state_out": "/foo"},
   }
], indirect=['terra'])
def test_terra_param(terra):
   assert terra == "zoo"
```

`terra_factory`
```
def test_terra_param(terra):
   plan = terra_factory(binary="terraform", command="plan", tfdir="bar", skip_teardown=True)
   assert plan["doo"] == "zoo"
```

## Installation

Install via Pip:
```
pip install pytest-terra-fixt
```

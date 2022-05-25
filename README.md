# pytest-terra-fixt
 
With the use of this plugin, users can run Terraform commands in a unit/integration test fashion using the Pytest framework. The fixtures within this plugin use the awesome [tftest](https://github.com/GoogleCloudPlatform/terraform-python-testing-helper) Python package. Tftest is a simple Python wrapper that runs and parses the output of Terraform commands.

## Fixtures

`terraform_version`:
   - Scope: Session
   - Return: Installs and/or sets the Terraform version to be used via [tfenv](https://github.com/tfutils/tfenv)

`tf`: 
   - Scope: Session
   - Setup: Runs `terraform init` on the specified directory
   - Yield: `tftest.TerraformTest` object that can run subsequent Terraform commands with
   - Teardown: Runs `terraform destroy -auto-approve` on the specified directory
 
`tf_factory`: 
   - Scope: Session
   - Setup: Runs `terraform init` on the specified directory
   - Yield: Factory fixture that returns a `tftest.TerraformTest` object that can run subsequent Terraform commands with
   - Teardown: Runs `terraform destroy -auto-approve` on the specified directory
 
All fixtures within this module are session-scoped given that Terraform consists of downloading providers and modules and of course spinning up time-consuming and possibly expensive resources. Using a session scope means that the fixtures are only invoked once per session unless they are skipped using the CLI arguments described in the following section.
 
## CLI Arguments

`--skip-tf-init`:  Skips running `terraform init` within `tf` and/or `tf_factory` fixtures. Useful for local testing of large modules where refreshing Terraform modules and providers is not needed on every pytest invocation.

`--skip-tf-destroy`: Skips running `terraform destroy -auto-approve` on teardown and preserves the Terraform backend tfstate for future testing. This flag is useful for checking out the Terraform resources within the cloud provider console or for running experimental tests without having to wait for the resources to spin up after every Pytest invocation.
 
   ```
   NOTE: If the user wants to continually preserve the Terraform tfstate, the --skip-tf-destroy flag needs to be always present, or else the `tf` or `tf_factory` fixture teardown will destroy the Terraform resources and remove the tfstate file.
   ```
 
## Examples

`fixtures/main.tf`
 
```
output "foo" {
   value = "bar
}
```
 
`test_plan.py` via `tf`
```
 
import pytest
import logging
import os
 
@pytest.mark.parametrize('tf', [f'{os.path.dirname(__file__)}/fixtures'], indirect=True)
@pytest.mark.parametrize('terraform_version', ['latest', '0.15.0'], indirect=True)
def test_plan(tf, terraform_version):
   assert tf.plan().outputs['foo'] == 'bar'

```

`test_plan.py` via `tf_factory`
```
 
import pytest
import logging
import os
 
@pytest.mark.parametrize('terraform_version', ['latest', '0.15.0'], indirect=True)
def test_plan(tf, terraform_version):
   tf = tf_factory(f'{os.path.dirname(__file__)}/fixtures')
   assert tf.plan().outputs['foo'] == 'bar'

```
 
## Installation
 
 
Install via Pip:
```
pip install pytest-terra-fixt-marshall7m
```
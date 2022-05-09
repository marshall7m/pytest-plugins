# pytest-terra-fixt
 
With the use of this plugin, users can run the Terraform process in unit/integration test fashion using the Pytest framework. The fixtures within this plugin use the awesome [tftest](https://github.com/GoogleCloudPlatform/terraform-python-testing-helper) Python package. Tftest is a simple Python wrapper that runs and parses the output of Terraform commands. The plugin includes the following collection of fixtures that reflect the main Terraform commands:
 
`tf`: This is the main fixture that sets the Terraform directory and runs `terraform init`. All other fixtures depend upon this fixture.
 
`tf_plan`: Runs `terraform plan` and returns plan as a dictionary
 
`tf_apply`: Runs `terraform apply -auto-approve` and yields the apply results as a dictionary. Within the teardown of the fixture, `terraform destroy -auto-approve` is executed within the associated Terraform directory.
 
`tf_output`: Runs `terraform output` and returns the outputs as a dictionary
 
All fixtures within this module are session-scoped given that Terraform consists of downloading providers and modules and of course spinning up time-consuming and possibly expensive resources. Using a session scope means that the fixtures are only invoked once per session unless they are skipped using the CLI arguments described in the following section.
 
# CLI Arguments
 
`--skip-tf-init`:  Skips running `terraform init` but still passes the initial Terraform configurations to the subsequent fixtures
 
`--skip-tf-plan`: Skips running `terraform plan` and skips any fixtures and tests that depend on the `tf_plan` fixture. This flag is useful for users who are confident in their Terraform plan-related tests and are focused on testing the terraform apply results.
 
`--skip-tf-apply`: Skips running `terraform apply` and skips any fixtures and tests that depend on the `tf_apply` fixture
 
`--skip-tf-destroy`: Skips running `terraform destroy` within the `tf_apply` fixture's teardown and preserves the Terraform backend tfstate for future testing. This flag is useful for checking out the Terraform resources within the cloud provider console or for running experimental tests without having to wait for the resources to spin up after every Pytest execution.
 
   ```
   NOTE: If the user wants to continually preserve the Terraform tfstate, the --skip-tf-destroy flag needs to be always present, or else the `tf_apply` teardown will destroy the Terraform resources and remove the tfstate file.
   ```
 
# Examples
`fixtures/main.tf`
 
```
output "foo" {
   value = "bar
}
```
 
`test_plan.py`
```
 
import pytest
import logging
import os
 
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
 
@pytest.mark.parametrize('tf', [f'{os.path.dirname(__file__)}/fixtures'], indirect=True)
@pytest.mark.parametrize('terraform_version', ['latest', '0.15.0'], indirect=True)
def test_plan(tf, terraform_version, tf_plan):
   log.debug(f'Terraform plan:\n{tf_plan}')
   assert tf_plan.outputs['foo'] == 'bar'
```
 
# Installation
 
The plugin is currently not on PyPI and is only installable via GitHub. The plugin can be included via the `setup.py` configuration like so:
 
```
from setuptools import setup, find_packages
 
install_requires = [
   'pytest-terra-fixt @ git+https://github.com/marshall7m/pytest-terra-fixt@v0.1.0#egg=pytest-terra-fixt'
]
setup(
   name="terraform-module",
   install_requires=install_requires,
   packages=find_packages()
)
```


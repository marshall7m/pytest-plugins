import pytest
import subprocess
import os
import tftest
import logging
import shlex
import json

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
base_dir = os.path.dirname(os.path.dirname(__file__))


def pytest_addoption(parser):
    group = parser.getgroup("Terra-Fixt")
    group.addoption(
        "--skip-tf-init",
        action="store_true",
        help="skips initing testing Terraform module",
    )
    group.addoption(
        "--skip-tf-plan",
        action="store_true",
        help="skips planning testing Terraform module",
    )
    group.addoption(
        "--skip-tf-apply",
        action="store_true",
        help="skips applying testing Terraform module",
    )
    group.addoption(
        "--skip-tf-destroy",
        action="store_true",
        help="skips destroying testing Terraform module",
    )


def terra_version(binary: str, version: str, overwrite=False):

    """
    Installs Terraform via tfenv or Terragrunt via tgswitch.
    If version='min-required' for Terraform installations, tfenv will scan
    the cwd for the minimum version required within Terraform blocks
    Arguments:
        binary: Binary to manage version for
        version: Semantic version to install and/or use
        overwrite: If true, version manager will install and/or switch to the
        specified version even if the binary is found in $PATH.
    """
    cmds = {
        "terraform": f"tfenv install {version} && tfenv use {version}",
        "terragrunt": f"tgswitch {version}",
    }

    if not overwrite:
        check_version = subprocess.run(
            shlex.split("{binary} --version"), capture_output=True, text=True
        )
        if check_version.returncode == 0:
            log.info(
                "Terraform found in $PATH -- " "skip tfenv Terraform install",
            )
            log.info(f"Terraform Version: {check_version.stdout}")
            return
        else:
            log.info("{binary} not found in $PATH -- installing {binary}")
    try:
        subprocess.run(
            cmds[binary],
            shell=True,
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        log.debug(e.stderr)
        raise e


def tf_vars_to_json(tf_vars: dict) -> dict:
    for k, v in tf_vars.items():
        if type(v) not in [str, bool, int, float]:
            tf_vars[k] = json.dumps(v)

    return tf_vars


@pytest.fixture(scope="session")
def terraform_version(request):
    """Terraform version that will be installed and used"""
    terra_version("terraform", request.param, overwrite=True)
    return request.param


@pytest.fixture(scope="session")
def tf(request, terraform_version: str):
    log.info(f"Terraform Version: {terraform_version}")
    tf = tftest.TerraformTest(request.param)

    if request.config.getoption("skip_tf_init"):
        log.info("--skip-tf-init is set -- skipping Terraform init")
    else:
        if request.config.getoption("skip_tf_destroy"):
            cleanup_on_exit = False
        else:
            cleanup_on_exit = True

        log.info("Running Terraform init")
        tf.setup(upgrade=True, cleanup_on_exit=cleanup_on_exit)

    yield tf
    
    log.info("Running Terraform init")
    tf.setup(upgrade=True, cleanup_on_exit=cleanup_on_exit)
    tf_destroy(request.config.getoption("skip_tf_destroy"), tf)


@pytest.fixture(scope="session")
def tf_plan(request, tf):
    if request.config.getoption("skip_tf_plan"):
        pytest.skip(
            "--skip-tf-plan is set -- "  # noqa: E501
            "skipping tests depending on terraform plan",  # noqa: E501
        )
    
    if hasattr(request, 'param'):
        tf_param = tftest.TerraformTest(request.param)
        yield tf_param.plan(output=True)
        # need return to separate parametrized fixture and factory fixture
        return

    response = []

    def _plan(update=True, **tf_vars):
        """
        Returns the Terraform plan output.
        Arguments:
            update: If True, runs the Terraform command and returns the output.
                    If False, returns the cached Terraform plan from the
                    previous function call.
        """
        if update:
            response.clear()
            response.append(
                tf.plan(
                    output=True,
                    tf_vars=tf_vars_to_json(tf_vars),
                )
            )
        return response[0]

    yield _plan


def tf_destroy(skip, tf):
    if skip:
        log.info("--skip-tf-destroy is set -- skipping Terraform destroy")
    else:
        log.info(
            "Cleaning up Terraform resources --"  # noqa: E501
            "running Terraform destroy"  # noqa: E501
        )
        tf.destroy(auto_approve=True)


@pytest.fixture(scope="session")
def tf_apply(request, tf):
    if request.config.getoption("skip_tf_apply"):
        pytest.skip(
            "--skip-tf-apply is set -- "  # noqa: E501
            "skipping tests depending on terraform apply"  # noqa: E501
        )
    
    if hasattr(request, 'param'):
        tf_param = tftest.TerraformTest(request.param)
        yield tf_param.apply(auto_approve=True)
        # need return to separate parametrized fixture and factory fixture
        return

    response = []

    def _apply(update=True, **tf_vars):
        """
        Returns the Terraform apply output.
        Arguments:
            update: If True, runs the Terraform command and returns the output.
                    If False, returns the cached Terraform apply output from
                    the previous function call.
        """

        if update:
            response.clear()
            response.append(
                tf.apply(auto_approve=True, tf_vars=tf_vars_to_json(tf_vars))
            )
        return response[0]

    yield _apply

@pytest.fixture(scope="session")
def tf_output(request, tf):
    if hasattr(request, 'param'):
        tf_param = tftest.TerraformTest(request.param)
        yield tf_param.output()
        # need return to separate parametrized fixture and factory fixture
        return

    response = []

    def _output(update=True):
        """
        Returns the Terraform plan output.
        Arguments:
            update: If True, runs the Terraform command and returns the output.
                    If False, returns the cached Terraform output from the
                    previous function call.
        """
        if update:
            response.clear()
            response.append(
                tf.output()
            )
        return response[0]

    yield _output

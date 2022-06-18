import pytest
import subprocess
import os
import tftest
import logging
import shlex
import requests

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
base_dir = os.path.dirname(os.path.dirname(__file__))


def pytest_addoption(parser):
    group = parser.getgroup("Terra-Fixt")
    group.addoption(
        "--skip-tf-init",
        action="store_true",
        help="skips initing Terraform configuration",
    )
    group.addoption(
        "--skip-tf-destroy",
        action="store_true",
        help="skips destroying Terraform configuration",
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

    if not overwrite:
        check_version = subprocess.run(
            shlex.split(f"{binary} --version"), capture_output=True, text=True
        )
        if check_version.returncode == 0:
            log.info(f"{binary} version: {check_version.stdout} " "found in $PATH")
            return
        else:
            log.info(f"{binary} version: {check_version.stdout} not found in $PATH")
    if binary == "terragrunt" and version == "latest":
        version = requests.get(
            "https://warrensbox.github.io/terragunt-versions-list/"
        ).json()["Versions"][0]

    cmds = {
        "terraform": f"tfenv install {version} && tfenv use {version}",
        "terragrunt": f"tgswitch {version}",
    }
    log.debug(f"Running command: {cmds[binary]}")
    try:
        subprocess.run(
            cmds[binary],
            shell=True,
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        log.error(e, exc_info=True)
        raise e


def _init(request, *args, **kwargs):
    tf = tftest.TerraformTest(*args, **kwargs)

    if request.config.getoption("skip_tf_init"):
        log.info("--skip-tf-init is set -- skipping Terraform init")
    else:
        if request.config.getoption("skip_tf_destroy"):
            cleanup_on_exit = False
        else:
            cleanup_on_exit = True

        log.info("Running Terraform init")
        tf.setup(upgrade=True, cleanup_on_exit=cleanup_on_exit)

    return tf


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
def terraform_version(request):
    """Terraform version that will be installed and used"""
    terra_version("terraform", request.param, overwrite=True)
    return request.param


@pytest.fixture(scope="session")
def terragrunt_version(request):
    """Terragrunt version that will be installed and used"""
    terra_version("terragrunt", request.param, overwrite=True)
    return request.param


@pytest.fixture(scope="session")
def tf_factory(request):
    tf_cfgs = []

    def _tf(*args, **kwargs):
        tf = _init(request, *args, **kwargs)
        tf_cfgs.append(tf)
        return tf

    yield _tf

    for tf in tf_cfgs:
        tf_destroy(request.config.getoption("skip_tf_destroy"), tf)


@pytest.fixture(scope="session")
def tf(request, terraform_version: str):
    log.info(f"Terraform Version: {terraform_version}")
    if type(request.param) == list:
        tf = _init(request, *request.param)
    elif type(request.param) == dict:
        tf = _init(request, **request.param)
    else:
        tf = _init(request, request.param)

    yield tf

    tf_destroy(request.config.getoption("skip_tf_destroy"), tf)

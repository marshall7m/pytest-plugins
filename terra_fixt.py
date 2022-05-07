import pytest
import subprocess
import shutil
import os
import tftest
import logging
import shlex

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
base_dir = os.path.dirname(os.path.dirname(__file__))

def pytest_addoption(parser):
    parser.addoption("--skip-tf-init", action="store_false", help="skips initing testing Terraform module")
    parser.addoption("--skip-tf-plan", action="store_true", help="skips planning testing Terraform module")
    parser.addoption("--skip-tf-apply", action="store_true", help="skips applying testing Terraform module")
    parser.addoption("--skip-tf-destroy", action="store_true", help="skips destroying testing Terraform module")

def terra_version(binary, version, overwrite=False):
    '''
    Installs Terraform via tfenv or Terragrunt via tgswitch.
    If version='min-required' for Terraform installations, tfenv will scan the cwd for the minimum version required within Terraform blocks
    Arguments:
        binary: Binary to manage version for
        version: Semantic version to install and/or use
        overwrite: If true, version manager will install and/or switch to the specified version even if the binary is found in $PATH.
    '''
    cmds = {
        'terraform': f'tfenv install {version} && tfenv use {version}',
        'terragrunt': f'tgswitch {version}'
    }

    if not overwrite:
        check_version = subprocess.run(shlex.split('{binary} --version'), capture_output=True, text=True)
        if check_version.returncode == 0:
            log.info('Terraform found in $PATH -- skip installing Terraform with tfenv')
            log.info(f'Terraform Version: {check_version.stdout}')
            return
        else:
            log.info('{binary} not found in $PATH -- installing {binary}')
    try:
        run = subprocess.run(cmds[binary], shell=True, capture_output=True, check=True, text=True)
    except subprocess.CalledProcessError as e:
        log.debug(e.stderr)
        raise e

tf_versions = [pytest.param('latest')]
@pytest.fixture(params=tf_versions, ids=[f'tf_{v.values[0]}' for v in tf_versions], scope='session')
def terraform_version(request):
    '''Terraform version that will be installed and used'''
    terra_version('terraform', request.param, overwrite=True)
    return request.param

@pytest.fixture(scope='session')
def tf(request, tmp_path_factory, terraform_version):
    fixture_dir = request.param
    fixture_prefix = os.path.basename(fixture_dir)
    tmp_tf_data_dir = str(tmp_path_factory.mktemp(f'{fixture_prefix}-backend-'))
    log.debug(f'Storing Terraform backend within tmp dir: {tmp_tf_data_dir}')

    tf = tftest.TerraformTest(fixture_dir, env={'TF_DATA_DIR': tmp_tf_data_dir})

    if request.config.getoption('skip_tf_init'):
        log.info('--skip-tf-init is set -- skipping Terraform init')
    else:
        log.info('Running Terraform init')
        tf.setup(upgrade=True)

    return tf

@pytest.fixture(scope='session')
def tf_plan(request, tf):
    if request.config.getoption('skip_tf_plan'):
        pytest.skip('--skip-tf-plan is set -- skipping tests depending on terraform plan')
    yield tf.plan()

@pytest.fixture(scope='session')
def tf_apply(request, tf):
    if request.config.getoption('skip_tf_apply'):
        pytest.skip('--skip-tf-apply is set -- skipping tests depending on terraform apply')
    yield tf.apply(auto_approve=True)

    if request.config.getoption('skip_tf_destroy'):
        log.info('--skip-tf-destroy is set -- skipping Terraform destroy')
    else:
        log.info('Cleaning up Terraform resources -- running Terraform destroy')
        tf.destroy(auto_approve=True)
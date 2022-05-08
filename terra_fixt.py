import pytest
import subprocess
import shutil
import os
import tftest
import logging
import shlex
import tempfile

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
base_dir = os.path.dirname(os.path.dirname(__file__))

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

@pytest.fixture(scope='session')
def terraform_version(request):
    '''Terraform version that will be installed and used'''
    terra_version('terraform', request.param, overwrite=True)
    return request.param

@pytest.fixture(scope='session')
def tf(request, tmp_path_factory, terraform_version):
    fixture_dir = request.param
    tf_data_dir = f'{tempfile.gettempdir()}/{os.path.basename(fixture_dir)}-backend'
    
    if os.path.exists(tf_data_dir):
        log.info('Using existing local Terraform backend')
    else:
        if request.config.getoption('skip_tf_destroy'):
            log.debug('Creating persistent Terraform backend')
            os.mkdir(tf_data_dir)
        else:
            log.debug('Creating temporary Terraform backend')
            tf_data_dir = str(tmp_path_factory.mktemp(f'{os.path.basename(fixture_dir)}-backend-'))

    log.debug(f'Storing Terraform backend within dir: {tf_data_dir}')

    tf = tftest.TerraformTest(fixture_dir, env={'TF_DATA_DIR': tf_data_dir})

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
    yield tf.plan(output=True)

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

        log.info(f'Removing Terraform backend directory: {tf.env["TF_DATA_DIR"]}')
        shutil.rmtree(tf.env['TF_DATA_DIR'], ignore_errors=True)

@pytest.fixture(scope='session')
def tf_output(request, tf):
    return tf.output()
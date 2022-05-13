import pytest
import subprocess
import os
import logging
import sys
from pytest_jsonreport.plugin import JSONReport
from unittest.mock import patch, call, PropertyMock

log = logging.getLogger(__name__)
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.DEBUG)


@patch('tftest.TerraformTest')
def test_skip_tf_plan(mock_tf_test):
    plugin = JSONReport()
    os.chdir(f'{os.path.dirname(__file__)}/fixtures')
    pytest.main(['--skip-tf-plan', '--json-report-file=none', 'test_tf.py'], plugins=[plugin])
    summary = plugin.report['summary']
    log.debug(f'Test Summary:\n{summary}')

    mock_tf_test.plan.assert_not_called()
    assert summary['skipped'] == 1

@patch('tftest.TerraformTest')
def test_skip_tf_apply(mock_tf_test):
    plugin = JSONReport()
    os.chdir(f'{os.path.dirname(__file__)}/fixtures')
    pytest.main(['--skip-tf-apply', '--json-report-file=none', 'test_tf.py'], plugins=[plugin])
    summary = plugin.report['summary']
    log.debug(f'Test Summary:\n{summary}')

    mock_tf_test.apply.assert_not_called()
    # skips tf.apply() in test_apply() and test_ouput()
    assert summary['skipped'] == 2

@patch('tftest.TerraformTest', autospec=True)
def test_skip_tf_destroy(mock_tf_test):
    
    #patch tf plan resource attr
    mock_tf_test.return_value.plan.return_value.outputs.__getitem__.return_value = 'bar'

    #patch tf output
    mock_tf_test.return_value.output.return_value = {'foo': 'bar'}
    plugin = JSONReport()
    os.chdir(f'{os.path.dirname(__file__)}/fixtures')

    pytest.main(['--skip-tf-destroy', '--json-report-file=none', 'test_tf.py'], plugins=[plugin])
    summary = plugin.report['summary']
    log.debug(f'Test Summary:\n{summary}')

    mock_tf_test.destroy.assert_not_called()
    assert summary['skipped'] == 0
import pytest
import tftest
import logging
import json
import pickle
from hashlib import sha1

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class OverrideTfTest(object):
    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, attr):
        return getattr(self.obj, attr)

def __getstate__(self): 
    return self.__dict__
def __setstate__(self, d): 
    self.__dict__.update(d)

def pytest_addoption(parser):
    parser.addoption(
        "--skip-teardown",
        action="store",
        help="skips teardown for every `terra` fixture",
    )


terra_kwargs = ["skip_teardown"]


@pytest.fixture(scope="session")
def terra(request):
    tftest_kwargs = {
        key: value for key, value in request.param.items() if key not in terra_kwargs
    }
    if request.param["binary"].endswith("terraform"):
        terra_cls = tftest.TerraformTest(**tftest_kwargs)
    elif request.param["binary"].endswith("terragrunt"):
        terra_cls = tftest.TerragruntTest(**tftest_kwargs)

    yield terra_cls

    if request.config.getoption("skip_teardown") is not None:
        skip = request.config.getoption("skip_teardown") == "true"
    else:
        skip = request.param.get("skip_teardown", False)

    if skip:
        log.info(f"Skipping teardown for {terra_cls.tfdir}")
    else:
        log.info(f"Tearing down: {terra_cls.tfdir}")
        terra_cls.destroy(auto_approve=True)


def _execute_command(request, terra, cmd):
    cmd_kwargs = getattr(request, "param", {}).get(
        terra.tfdir, getattr(request, "param", {})
    )
    params = {**terra.__dict__, **cmd_kwargs}
    # use json.dumps to preserve order in nested dict values
    param_hash = sha1(
        json.dumps(params, sort_keys=True, default=str).encode("utf_16")
    ).hexdigest()
    log.debug(f"Param hash: {param_hash}")

    cache_key = request.config.cache.makedir("terra") + (
        terra.tfdir + "/" + cmd + "-" + param_hash
    )
    log.debug(f"Cache key: {cache_key}")
    cache_value = request.config.cache.get(cache_key, None)

    if cache_value:
        log.info("Getting output from cache")
        return pickle.loads(cache_value.encode("utf_16"))
    else:
        log.info("Running command")
        out = getattr(terra, cmd)(**cmd_kwargs)
        if out:
            try:
                out_bytes = pickle.dumps(out)
            except KeyError as e:
                if e.args[0] == "__getstate__":
                    out.__getstate__ = __getstate__.__get__(out, tftest.TerraformPlanOutput)
                    out.__setstate__ = __setstate__.__get__(out, tftest.TerraformPlanOutput)
                    out = OverrideTfTest(out)
                    out_bytes = pickle.dumps(out)
            request.config.cache.set(cache_key, out_bytes.decode("utf_16"))
        return out


@pytest.fixture(scope="session")
def terra_setup(terra, request):
    return _execute_command(request, terra, "setup")


@pytest.fixture(scope="session")
def terra_plan(terra_setup, terra, request):
    return _execute_command(request, terra, "plan")


@pytest.fixture(scope="session")
def terra_apply(terra_setup, terra, request):
    return _execute_command(request, terra, "apply")


@pytest.fixture(scope="session")
def terra_output(terra, request):
    return _execute_command(request, terra, "output")

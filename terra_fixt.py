import pytest
import tftest
import logging
import json
from hashlib import sha1

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


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
    cmd_kwargs = getattr(request, "param", {}).get(terra.tfdir, getattr(request, "param", {}))
    params = {**terra.__dict__, **cmd_kwargs}
    log.debug(f"Hash dict:\n{params}")
    # use json.dumps to preserve order in nested dict values
    param_hash = sha1(
        json.dumps(params, sort_keys=True, default=str).encode()
    ).hexdigest()
    log.debug(f"Param hash: {param_hash}")

    cache_key = request.config.cache.makedir("terra") + (
        terra.tfdir + "/" + cmd + "-" + param_hash
    )
    log.debug(f"Cache key: {cache_key}")
    cache_value = request.config.cache.get(cache_key, None)

    if cache_value:
        log.info("Getting output from cache")
        return cache_value
    else:
        log.info("Running command")
        out = getattr(terra, cmd)(**cmd_kwargs)
        log.debug(out)
        request.config.cache.set(cache_key, out)
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

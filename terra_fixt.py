import pytest
import tftest
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def pytest_addoption(parser):
    parser.addoption(
        "--skip-teardown",
        action="store",
        help="skips teardown for every terra and terra_factory fixture",
    )


class TfTestCache:
    def __init__(self, **kwargs):
        if kwargs["binary"].endswith("terraform"):
            self.instance = tftest.TerraformTest(**kwargs)
        elif kwargs["binary"].endswith("terragrunt"):
            self.instance = tftest.TerragruntTest(**kwargs)

    def __getattr__(self, name):
        return self.instance.__getattribute__(name)

    def get_cache(self, cmd):
        return getattr(self, f"cached_{cmd}")

    def run_terra_cmd(self, cmd, **extra_args):
        cmd = cmd.replace(" ", "_")
        out = getattr(self, cmd)(**extra_args)
        setattr(self, f"cached_{cmd}", out)

        return out


@pytest.fixture(scope="session")
def terra_cache():
    terras = {}

    def _cache(**kwargs):
        if kwargs != {}:

            cache = TfTestCache(**kwargs)
            terras[cache.tfdir] = cache
            return cache

        else:
            return terras

    yield _cache

    terras = {}


terra_kwargs = ["command", "skip_teardown", "use_cache", "extra_args"]


@pytest.fixture
def terra(request, terra_cache):
    tftest_kwargs = {
        key: value for key, value in request.param.items() if key not in terra_kwargs
    }
    terra_cls = terra_cache(**tftest_kwargs)

    if request.param.get("command"):
        if request.param.get("use_cache", False):
            log.info("Getting results from cache")
            yield terra_cls.get_cache(request.param["command"])
        else:
            yield terra_cls.run_terra_cmd(
                request.param["command"], **request.param.get("extra_args", {})
            )
    else:
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


@pytest.fixture(scope="session")
def terra_factory(request, terra_cache):
    teardowns = []

    def _terra_factory(**cfg):
        tftest_kwargs = {
            key: value for key, value in cfg.items() if key not in terra_kwargs
        }
        terra_cls = terra_cache(**tftest_kwargs)

        if request.config.getoption("skip_teardown") is not None:
            skip = request.config.getoption("skip_teardown") == "true"
        else:
            skip = cfg.get("skip_teardown", False)
        if not skip:
            teardowns.append(terra_cls.tfdir)

        if cfg.get("command"):
            if cfg.get("use_cache", False):
                log.info("Getting results from cache")
                return terra_cls.get_cache(cfg["command"])
            else:
                return terra_cls.run_terra_cmd(
                    cfg["command"], **cfg.get("extra_args", {})
                )
        else:
            return terra_cls

    yield _terra_factory

    for path in teardowns:
        log.info(f"Tearing down: {path}")
        terra_cache()[path].destroy(auto_approve=True)

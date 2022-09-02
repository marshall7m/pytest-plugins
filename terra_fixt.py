import pytest
import tftest
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


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


@pytest.fixture(scope="session")
def terra(request, terra_cache):
    cfg = request.param
    cache_kwargs = [kwarg for kwarg in request.param if kwarg not in terra_kwargs]
    cache = terra_cache(cache_kwargs)
    if cfg.get("use_cache", False):
        log.debug("Getting results from cache")
        yield cache.get_cache(cfg["command"])
    else:
        yield cache.run_terra_cmd(cfg["command"], **cfg["extra_args"])

    if cfg.get("skip_teardown", False):
        log.debug(f"Skipping teardown for {cache.tfdir}")
    else:
        log.debug(f"Tearing down: {cache.tfdir}")
        cache.destroy(auto_approve=True)


@pytest.fixture(scope="session")
def terra_factory(terra_cache):
    teardowns = []

    def _terra_factory(**cfg):
        cache_kwargs = [kwarg for kwarg in cfg if kwarg not in terra_kwargs]
        cache = terra_cache(cache_kwargs)

        if not cfg.get("skip_teardown", False):
            teardowns.append(cache.tfdir)

        if cfg.get("use_cache", False):
            log.debug("Getting results from cache")
            return cache.get_cache(cfg["command"])
        else:
            return cache.run_terra_cmd(cfg["command"], **cfg["extra_args"])

    yield _terra_factory

    for path in teardowns:
        log.debug(f"Tearing down: {path}")
        terra_cache()[path].destroy(auto_approve=True)

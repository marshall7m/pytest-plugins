import pytest
import tftest
import logging
import os

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
        self.cache = {}
        if kwargs["binary"].endswith("terraform"):
            self.instance = tftest.TerraformTest(**kwargs)
        elif kwargs["binary"].endswith("terragrunt"):
            self.instance = tftest.TerragruntTest(**kwargs)

    def __getattr__(self, name):
        return self.instance.__getattribute__(name)

    def run(self, command, put_cache=True, get_cache=False, **extra_args):
        command = command.replace(" ", "_")
        if get_cache:
            if command in self.cache:
                return self.cache[command]

        out = getattr(self, command)(**extra_args)

        if put_cache:
            self.cache[command] = out

        return out


@pytest.fixture(scope="session")
def terra_cache():
    terras = {}

    def _cache(**kwargs):
        if kwargs != {}:
            if not kwargs["tfdir"].startswith("/"):
                kwargs["tfdir"] = os.path.join(
                    kwargs.get("basedir", os.getcwd()), kwargs["tfdir"]
                )

            if kwargs["tfdir"] in terras.keys():
                cache_cls = terras[kwargs["tfdir"]]
                for key, value in kwargs.items():
                    setattr(cache_cls, key, value)
                log.debug(cache_cls.binary)
            else:
                terras[kwargs["tfdir"]] = TfTestCache(**kwargs)

            return terras[kwargs["tfdir"]]

        else:
            return terras

    yield _cache

    terras = {}


terra_kwargs = ["command", "skip_teardown", "get_cache", "put_cache", "extra_args"]


@pytest.fixture
def terra(request, terra_cache):
    tftest_kwargs = {
        key: value for key, value in request.param.items() if key not in terra_kwargs
    }
    terra_cls = terra_cache(**tftest_kwargs)

    if request.param.get("command"):
        yield terra_cls.run(
            command=request.param["command"],
            put_cache=request.param.get("put_cache"),
            get_cache=request.param.get("get_cache"),
            **request.param.get("extra_args", {}),
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
            return terra_cls.run(
                command=cfg["command"],
                put_cache=cfg.get("put_cache"),
                get_cache=cfg.get("get_cache"),
                **cfg.get("extra_args", {}),
            )
        else:
            return terra_cls

    yield _terra_factory
    for path in teardowns:
        log.info(f"Tearing down: {path}")
        terra_cache()[path].destroy(auto_approve=True)

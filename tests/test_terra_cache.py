pytest_plugins = [
    str("_pytest.pytester"),
]


def test_initial_cache(pytester):
    pytester.makepyfile(
        """

    def test_foo(terra_cache):
        assert terra_cache() == {}
    """
    )
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)


def test_add_cache(pytester):
    pytester.makepyfile(
        """
    from terra_fixt import TfTestCache
    def test_foo(terra_cache):
        data = {
            "binary": "terraform",
            "tfdir": "bar",
            "basedir": "foo"
        }
        terra_cache(**data)
        assert isinstance(terra_cache()["foo/bar"], TfTestCache)
    """
    )
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)


def test_update_cache(pytester):
    pytester.makepyfile(
        """
    def test_foo(terra_cache):
        data = {
            "binary": "terraform",
            "tfdir": "bar",
            "basedir": "foo"
        }
        terra_cache(**data)

        updated_env = {"baz": "doo"}
        data["env"] = updated_env
        terra_cache(**data)

        assert terra_cache()["foo/bar"].env == updated_env
    """
    )
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)

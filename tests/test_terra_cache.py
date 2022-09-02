import pytest

pytest_plugins = [
    str("_pytest.pytester"),
]

def test_initial_cache(pytester):
    pytester.makepyfile("""
    
    def test_foo(terra_cache):
        assert terra_cache() == {}
    """)
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)

def test_add_cache(pytester):
    pytester.makepyfile("""
    from terra_fixt import TfTestCache
    def test_foo(terra_cache):
        data = {
            "binary": "terraform",
            "tfdir": "bar",
            "basedir": "foo"
        }
        terra_cache(**data)
        assert isinstance(terra_cache()["foo/bar"], TfTestCache)
    """)
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)

def test_update_cache(pytester):
    pytester.makepyfile("""
    from tftest import TerragruntTest
    def test_foo(terra_cache):
        data = {
            "binary": "terraform",
            "tfdir": "bar",
            "basedir": "foo"
        }
        terra_cache(**data)
        
        data["binary"] = "terragrunt"
        terra_cache(**data)

        assert isinstance(terra_cache()["foo/bar"].instance, TerragruntTest)
    """)
    reprec = pytester.inline_run()

    reprec.assertoutcome(passed=1)
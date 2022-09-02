kwargs = {
    "tf_all": {
        "binary": "terraform",
        "basedir": "fixture",
        "tfdir": "bar",
        "env": {},
        "tg_run_all": False,
        "command": "apply",
        "skip_teardown": False,
        "consolidate_teardown": True,
        "use_cache": False,
        "extra_args": "-auto-approve",
    },
    "tg_all": {
        "binary": "terragrunt",
        "basedir": "fixture",
        "tfdir": "bar",
        "env": {},
        "tg_run_all": False,
        "command": "apply",
        "skip_teardown": False,
        "consolidate_teardown": True,
        "use_cache": False,
        "extra_args": {
            "auto_approve": True
        }
    }
}
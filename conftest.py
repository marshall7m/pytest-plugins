def pytest_addoption(parser):
    parser.addoption("--skip-tf-init", action="store_false", help="skips initing testing Terraform module")
    parser.addoption("--skip-tf-plan", action="store_true", help="skips planning testing Terraform module")
    parser.addoption("--skip-tf-apply", action="store_true", help="skips applying testing Terraform module")
    parser.addoption("--skip-tf-destroy", action="store_true", help="skips destroying testing Terraform module")

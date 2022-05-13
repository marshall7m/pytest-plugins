provider "null" {}

resource "null_resource" "this" {}

output "foo" {
    value = "bar"
}
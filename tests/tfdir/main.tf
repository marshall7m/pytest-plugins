locals {
    foo = "doo"
}

output "foo" { 
    value = local.foo
}
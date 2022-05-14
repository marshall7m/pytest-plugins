variable "foo" {
    type = string
    default = "bar"
}

variable "baz" {
    type = list(object({
        string_attr = string
        number_attr = number
        bool_attr = bool
    }))
    default = []
}
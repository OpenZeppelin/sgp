from typing import Any


def string_from_snake_to_camel_case(input: str) -> str:
    """
    #TODO: add docstring
    """

    if not input:
        return input
    if "_" not in input:
        return input
    s = input.split("_")
    return s[0] + "".join(i.title() for i in s[1:])

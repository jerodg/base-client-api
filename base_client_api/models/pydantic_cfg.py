#!/usr/bin/env python3.9
"""Base Client API -> Models -> Pydantic Config
Copyright © 2019-2021 Jerod Gawne <https://github.com/jerodg/>

This program is free software: you can redistribute it and/or modify
it under the terms of the Server Side Public License (SSPL) as
published by MongoDB, Inc., either version 1 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
SSPL for more details.

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

You should have received a copy of the SSPL along with this program.
If not, see <https://www.mongodb.com/licensing/server-side-public-license>."""
from pydantic import BaseModel as PydanticBaseModel
from rapidjson import dumps, loads

CASE_TYPES = ['flat', 'flat_upper', 'camel', 'pascal', 'snake', 'snake_pascal', 'snake_camel', 'kebab', 'train', 'underscore_camel']


def pascal_case(value) -> str:
    """Convert Case

    Converts snake case to pascal case for JSON

    Args:
        value (str):

    References:
        https://stackoverflow.com/questions/17326185/what-are-the-different-kinds-of-cases

    Raises:
        ValueError

    Returns:
        (str)"""
    words = value.split('_')
    new_words = [words[0]]
    [new_words.append(x.capitalize()) for x in words[1:]]

    return ''.join(new_words)


class BaseModel(PydanticBaseModel):
    class Config:
        """MyConfig

        Pydantic configuration"""
        alias_generator = pascal_case
        json_loads = loads
        json_dumps = dumps

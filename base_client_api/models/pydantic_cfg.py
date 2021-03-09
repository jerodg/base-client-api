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


def convert_case(var_name: str, from_type: str = 'snake', to_type: str = 'pascal') -> str:
    """Convert Case

    Converts variable names between case types

    Args:
        var_name (str):
        from_type (str):
        to_type (str):

    References:
        https://stackoverflow.com/questions/17326185/what-are-the-different-kinds-of-cases

    Raises:
        ValueError

    Returns:
        new_var (str)"""

    # todo: handle additional case types
    # todo: add automatic detection of source type

    # @validator('from_type', 'to_type')
    # def check_types(cls, value) -> str:
    #     """Check Types
    #
    #     Validates parameters
    #
    #     Args:
    #         cls (class):
    #         value (str):
    #
    #     Raises:
    #          ValueError
    #
    #     Returns:
    #         value (str)"""
    #     if value in CASE_TYPES:
    #         return value
    #     else:
    #         raise ValueError(f'Case types must be one of: {CASE_TYPES}')

    if from_type == 'snake':
        words = var_name.split('_')
    else:
        words = None

    if to_type == 'pascal':
        return f'{words[0].lower()}{"".join(words[1:]).capitalize()}'


class BaseModel(PydanticBaseModel):
    class Config:
        """MyConfig

        Pydantic configuration"""
        alias_generator = convert_case
        json_loads = loads
        json_dumps = dumps

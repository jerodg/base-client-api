#!/usr/bin/env python3.8
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

from base_client_api.utils import pascal_case


class Base(PydanticBaseModel):
    """Base Model

    Used for pydantic configuration"""

    class Config:
        """Config

        Pydantic configuration"""
        allow_population_by_field_name = True
        alias_generator = pascal_case
        anystr_strip_whitespace = True
        case_sensitive = True
        json_dumps = dumps
        json_loads = loads

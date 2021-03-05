#!/usr/bin/env python3.9
"""Base Client API -> Init
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

from loguru import logger

from .base_client import BaseClientApi
from .exceptions import InvalidOptionError
from .models import Record, Results, sort_dict
from .utils import bprint, convert_case, flatten, generate_password, tprint, vprint

__version__ = '1.4.0'

# Because this is a library; use logger.enable('base_client_api) in script to see log msgs.
logger.add(__name__)
logger.disable(__name__)

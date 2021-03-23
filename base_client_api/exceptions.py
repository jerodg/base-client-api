#!/usr/bin/env python3.8
"""Base Client API -> Exceptions
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
from typing import Sized

from loguru import logger

from base_client_api.utils import vprint


class InvalidOptionError(Exception):
    """Invalid Option Error
       - For when a field can only be one of available options."""

    def __init__(self, var: Sized, options: list):
        super().__init__(options)
        self.var = var
        self.message = options

    def __str__(self):
        if type(self.message) is list:
            msg = '\n'.join(self.message)
        else:
            msg = str(self.message)

        logger.error(f'Invalid Option for {vprint(self.var)}; should be one of:\n\t->{msg}')

    def __repr__(self):
        if type(self.message) is list:
            msg = '\n'.join(self.message)
        else:
            msg = str(self.message)

        logger.error(f'\nInvalid Option for {vprint(self.var)}; should be one of:\n\t->{msg}')


if __name__ == '__main__':
    print(__doc__)

#!/usr/bin/env python3.9
"""Base Client API -> Tests -> Models -> Test Request
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
from dataclasses import dataclass
from typing import Union

from base_client_api.models import Record


@dataclass
class ListBooks(Record):
    limit: int = 5
    q: str = 'book'
    offset: int = 0

    @property
    def endpoint(self) -> str:
        """Endpoint

        The suffix end of the URI

        Returns:
            (str)"""
        return 'http://openlibrary.org/search/lists.json'

    @property
    def method(self) -> Union[str, None]:
        """Method

        The HTTP verb to be used

        Returns:
            (str)"""
        return 'GET'

    @property
    def params(self) -> Union[dict, None]:
        """URL Parameters

        If you need to pass parameters in the URL

        Returns:
            (Union[dict, None])"""
        return self.dict()

    @property
    def data_key(self) -> Union[str, None]:
        """Data Key

        This is the key used in the return dict that holds the primary data

        Returns:
            (Union[str, None])"""
        return 'docs'

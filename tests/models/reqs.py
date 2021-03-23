#!/usr/bin/env python3.8
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
from typing import Optional

from base_client_api.models.record import Record


class BooksListAll(Record):
    """Books -> List All"""
    q: str
    limit: Optional[int]
    offset: Optional[int]

    @property
    def method(self) -> str:
        """Method

        The HTTP verb to be used
         - Must be a valid HTTP verb as listed above in METHODS

        Returns:
            (str)"""
        return 'GET'

    @property
    def parameters(self) -> Optional[dict]:
        """URL Parameters

        If you need to pass parameters in the URL

        Returns:
            (dict)"""
        return self.dict()

    @property
    def headers(self) -> Optional[dict]:
        """Headers

        If you need to pass non-default headers

        Returns:
            (dict)"""
        return None

    @property
    def json_body(self) -> Optional[str]:
        """Request Body"""
        return None

    @property
    def endpoint(self) -> str:
        """Endpoint

        The suffix end of the URI

        Returns:
            (str)"""
        return 'http://openlibrary.org/search/lists.json'

    @property
    def response_key(self) -> Optional[str]:
        """Data Key

        This is the key used in the return dict that holds the primary responses

        Returns:
            (Union[str, None])"""
        return 'docs'

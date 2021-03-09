#!/usr/bin/env python3.9
"""Base Client API -> Models -> Record
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
from typing import Any, Optional

from base_client_api.models.pydantic_cfg import BaseModel
from base_client_api.utils import sort_dict

METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']


class Record(BaseModel):
    """Generic Record"""

    def dict(self, *,
             include: set = None,
             exclude: set = None,
             by_alias: bool = True,
             skip_defaults: bool = None,
             exclude_unset: bool = False,
             exclude_defaults: bool = False,
             exclude_none: bool = True,
             cleanup: Optional[bool] = True,
             sort_order: Optional[str] = 'asc') -> dict[str, Any]:
        """Dictionary

        Args:
            include (Union['AbstractSetIntStr', 'MappingIntStrAny']):
            exclude (Union['AbstractSetIntStr', 'MappingIntStrAny']):
            by_alias (bool):
            skip_defaults (bool):
            exclude_unset (bool):
            exclude_defaults (bool):
            exclude_none (bool):
            cleanup (bool):
            sort_order (str): ['asc', 'desc']

        Returns:
            dct (Dict[str, Any])"""
        dct = super().dict(include=include,
                           exclude=exclude,
                           by_alias=by_alias,
                           skip_defaults=skip_defaults,
                           exclude_unset=exclude_unset,
                           exclude_defaults=exclude_defaults,
                           exclude_none=exclude_none)

        if cleanup:
            dct = {k: v for k, v in dct.items() if v is not None}

        if sort_order:
            dct = sort_dict(dct, reverse=True if sort_order.lower() == 'desc' else False)

        try:
            del dct['cleanup']
        except KeyError:
            pass

        try:
            del dct['sort_field']
        except KeyError:
            pass

        try:
            del dct['sort_order']
        except KeyError:
            pass

        return dct

    @property
    def endpoint(self) -> str:
        """Endpoint

        The suffix end of the URI

        Returns:
            (str)"""
        return ''

    @property
    def data_key(self) -> str:
        """Data Key

        This is the key used in the return dict that holds the primary responses

        Returns:
            (str)"""
        return ''

    @property
    def method(self) -> str:
        """Method

        The HTTP verb to be used
         - Must be a valid HTTP verb as listed above in METHODS

        Returns:
            (str)"""
        return ''

    @property
    def file(self) -> str:
        """File

        A file path as a str

        Returns:
            (str)"""
        return ''

    @property
    def params(self) -> dict:
        """URL Parameters

        If you need to pass parameters in the URL

        Returns:
            (dict)"""
        return self.dict()

    @property
    def headers(self) -> dict:
        """Headers

        If you need to pass non-default headers

        Returns:
            (dict)"""
        return {}

    @property
    def body(self) -> str:
        """Request Body"""
        return self.json(by_alias=True, exclude_none=True)


if __name__ == '__main__':
    print(__doc__)

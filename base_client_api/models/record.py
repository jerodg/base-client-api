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
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, List, NoReturn, Optional, Union

from loguru import logger

METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']


def sort_dict(dct: dict, reverse: Optional[bool] = False) -> dict:
    """Sort a dictionary, recursively, by keys.

    Args:
        dct (dict):
        reverse (bool):

    Returns:
        dct (dict)"""
    items: List[List[Any]] = [[k, v] for k, v in sorted(dct.items(), key=lambda x: x[0], reverse=reverse)]

    for item in items:
        if isinstance(item[1], dict):
            item[1] = sort_dict(item[1], reverse=reverse)

    return dict(items)


@dataclass
class Record:
    """Generic Record"""
    cleanup: bool = False
    sort_field: Optional[str] = None
    sort_order: Optional[str] = None

    def __post_init__(self):
        if self.method.upper() not in METHODS:
            logger.error(f'Method ({self.method}) is not a valid HTTP verb, '
                         f'it must be one of the following\n-> {", ".join(METHODS)}')

    def clear(self) -> NoReturn:
        """Clear
        Sets all record values to None

        Returns:
            (NoReturn)"""
        for k, v in self.__dict__.items():
            self.__dict__[k] = None

    def dict(self, cleanup: Optional[bool] = True, dct: Optional[dict] = None, sort_order: Optional[str] = 'asc') -> dict:
        """
        Args:
            cleanup (Optional[bool]):
            dct (Optional[dict]):
            sort_order (Optional[str]): ASC | DESC

        Returns:
            dict (dict):"""
        if not dct:
            dct = deepcopy(self.__dict__)

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

    def load(self, **entries):
        """Populates dataclass"
        Notes:
            Only works on top-level dicts"""
        # todo: get this working with multi-level dicts
        self.__dict__.update(entries)

    @property
    def endpoint(self) -> str:
        """Endpoint

        The suffix end of the URI

        Returns:
            (str)"""
        return '/'

    @property
    def data_key(self) -> Union[str, None]:
        """Data Key

        This is the key used in the return dict that holds the primary data

        Returns:
            (Union[str, None])"""
        return None

    @property
    def method(self) -> Union[str, None]:
        """Method

        The HTTP verb to be used

        Returns:
            (str)"""
        return None

    @property
    def file(self) -> Union[str, None]:
        """File

        A file path as a str

        Returns:
            (Union[str, None])"""
        return None

    @property
    def params(self) -> Union[dict, None]:
        """URL Parameters

        If you need to pass parameters in the URL

        Returns:
            (Union[dict, None])"""
        return None


if __name__ == '__main__':
    print(__doc__)

#!/usr/bin/env python3.9
"""Base Client API: Models.Record
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
import logging
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


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

    def clear(self):
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

        return dct

    def load(self, **entries):
        """Populates dataclass"
        Notes:
            Only works on top-level dicts"""
        self.__dict__.update(entries)

    @property
    def end_point(self):
        return '/'

    @property
    def data_key(self):
        return None


if __name__ == '__main__':
    print(__doc__)

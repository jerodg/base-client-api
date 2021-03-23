#!/usr/bin/env python3.8
"""Base Client API -> Models -> Results
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
from typing import Any, List, NoReturn

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class Results:
    """Results from aio.ClientRequest(s)"""
    responses: Any
    success: List[dict] = Field(default_factory=list)
    failure: List[dict] = Field(default_factory=list)

    @property
    def dict(self) -> dict:
        """Dict

        Provides a dictionary with success/failure results

        Returns:
            (dict)"""
        return {'success': self.success, 'failure': self.failure}

    def cleanup(self, sort_order: str = 'asc') -> NoReturn:
        """Cleanup

        Removes keys that have a null value and optionally sorts

        Args:
            sort_order ():

        Returns:
            (NoReturn)"""
        success = []
        for rec in self.success:
            d = {k: v for k, v in rec.items() if v is not None}
            d = dict(sorted(d.items(), reverse=True if sort_order.lower() == 'desc' else False))
            success.append(d)

        self.success = success
        del success


if __name__ == '__main__':
    print(__doc__)

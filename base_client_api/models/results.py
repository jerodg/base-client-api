#!/usr/bin/env python3.9
"""Base Client API: Models.Results
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
from dataclasses import dataclass, field
from typing import List

logger = logging.getLogger(__name__)


@dataclass
class Results:
    """Results from aio.ClientRequest(s)"""
    data: List[dict]
    success: List[dict] = field(default_factory=list)
    failure: List[dict] = field(default_factory=list)

    @property
    def dict(self) -> dict:
        return {'success': self.success, 'failure': self.failure}

    def cleanup(self, sort_order: str = 'asc', keep_request_id: bool = False):
        success = []
        for rec in self.success:
            if not keep_request_id:
                del rec['request_id']

            d = {k: v for k, v in rec.items() if v is not None}
            d = dict(sorted(d.items(), reverse=True if sort_order.lower() == 'desc' else False))
            success.append(d)

        self.success = success
        del success


if __name__ == '__main__':
    print(__doc__)

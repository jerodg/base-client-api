#!/usr/bin/env python3.8
"""Base Client API -> Test Process Results
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
import pytest
import time
from os.path import realpath

from base_client_api.base_client import BaseClientApi
from base_client_api.models.results import Results
from base_client_api.utils import bprint, tprint
from .models.reqs import BooksListAll


@pytest.mark.asyncio
async def test_make_request():
    ts = time.perf_counter()
    bprint('Test: Make Request/Process Results', 'top')

    async with BaseClientApi(cfg=realpath('./examples/config.toml')) as bca:
        results = await bca.make_request(BooksListAll(q='book',
                                                      limit=25,
                                                      offset=0))

        assert type(results) is Results
        assert results.success is not None
        assert not results.failure

        tprint(results, top=5)

    bprint(f'Completed in {(time.perf_counter() - ts):f} seconds.', 'bottom')


@pytest.mark.asyncio
async def test_request_debug():
    ts = time.perf_counter()
    bprint('Test: Request Debug', 'top')

    async with BaseClientApi() as bca:
        await bca.make_request(BooksListAll(q='book',
                                            limit=25,
                                            offset=0), debug=True)

    bprint(f'Completed in {(time.perf_counter() - ts):f} seconds.', 'bottom')

#!/usr/bin/env python3.9
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
import asyncio
import time

import pytest

from base_client_api import BaseClientApi, bprint, tprint
from base_client_api.models import Results
from .models import ListBooks


@pytest.mark.asyncio
async def test_process_results():
    ts = time.perf_counter()
    bprint('Test: Process Results', 'top')

    async with BaseClientApi() as bca:
        lb = ListBooks()
        results = await asyncio.gather(*[asyncio.create_task(bca.request(lb))])

        res = await bca.process_results(results=Results(data=results), data_key=lb.data_key)

        assert type(res) is Results
        assert res.success is not None
        assert not res.failure

        tprint(res, top=5)

    bprint(f'Completed in {(time.perf_counter() - ts):f} seconds.', 'bottom')


@pytest.mark.asyncio
async def test_request_debug():
    ts = time.perf_counter()
    bprint('Test: Request Debug', 'top')

    async with BaseClientApi() as bca:
        lb = ListBooks()
        results = await asyncio.gather(*[asyncio.create_task(bca.request(lb))])

        results = await bca.request_debug(results[0]['response'])
        print(results)

    bprint(f'Completed in {(time.perf_counter() - ts):f} seconds.', 'bottom')

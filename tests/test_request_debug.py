#!/usr/bin/env python3.9
"""Base Client API: Test Request Debug
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
import time

import aiohttp as aio
import pytest

from base_client_api import BaseClientApi, bprint


@pytest.mark.asyncio
async def test_request_debug():
    ts = time.perf_counter()
    bprint('Test: Request Debug')

    async with BaseClientApi() as bac:
        async with aio.ClientSession() as session:
            response = await session.get('https://www.google.com', ssl=False)

        results = await bac.request_debug(response=response)

        assert type(results) is str

        print('Results:\n', results)

    bprint(f'-> Completed in {(time.perf_counter() - ts):f} seconds.')

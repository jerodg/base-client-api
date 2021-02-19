#!/usr/bin/env python3.9
"""Base Client API: Test Process Results
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


@pytest.mark.asyncio
async def test_process_results():
    ts = time.perf_counter()
    bprint('Test: Process Results')

    async with BaseClientApi() as bac:
        tasks = [asyncio.create_task(bac.request(method='get',
                                                 endpoint='http://openlibrary.org/search/lists.json',
                                                 params={'limit':  5,
                                                         'q':      'book',
                                                         'offset': 0}))]
        results = Results(data=await asyncio.gather(*tasks))

        assert type(results) is Results
        assert results.success is not None
        assert not results.failure

        processed_results = await bac.process_results(results, data_key='docs')
        tprint(processed_results, top=5)

    bprint(f'-> Completed in {(time.perf_counter() - ts):f} seconds.')

#!/usr/bin/env python3.9
"""Base Client API -> Test Banner Print
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

import pytest
from rich import print

from base_client_api.utils import bprint, pascal_case


@pytest.mark.asyncio
async def test_banner_print():
    ts = time.perf_counter()
    bprint('Test: Top Print', location='top')
    bprint('Test: Center Print')
    bprint(f'Completed in {(time.perf_counter() - ts):f} seconds.', location='bottom')


@pytest.mark.asyncio
async def test_pascal_case():
    ts = time.perf_counter()
    bprint('Test: Pascal Case', location='top')

    source = 'body'
    result = pascal_case(source)
    print(f'From: {source} \n  To: {result}')
    assert result == 'body'

    source = 'client_id'
    result = pascal_case(source)
    print(f'From: {source} \n  To: {result}')
    assert result == 'clientId'

    source = 'activation_code_validity'
    result = pascal_case(source)
    print(f'From: {source} \n  To: {result}')
    assert result == 'activationCodeValidity'

    bprint(f'Completed in {(time.perf_counter() - ts):f} seconds.', location='bottom')

#!/usr/bin/env python3.9
"""Base Client API: Utils
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
from random import choice, shuffle
from string import ascii_letters, ascii_lowercase, ascii_uppercase, digits
from typing import Any, Generator, NoReturn, Optional, Union

from base_client_api.models import Results


def bprint(message) -> NoReturn:
    """ Deprecated

    Args:
        message (str):

    Returns:
        (NoReturn)
    """
    msg = f'\n▃▅▇█▓▒░۩۞۩ {message.center(58)} ۩۞۩░▒▓█▇▅▃\n'
    print(msg)


def banner(message: str, location: str = None) -> str:
    """Build a banner

    Args:
        message (str):
        location (str): ['top', 'above', None]

    Returns:
        (str)"""
    len_msg = len(message)
    if len_msg > 126:
        m = list(message)
        message = f'{"".join(m[:123])}...'

    len_banner = 132 - len_msg
    half = int(len_banner / 2)

    if len_banner % 2 == 0:
        hlf0, hlf1 = half, half
    else:
        hlf0, hlf1 = half, half + 1

    if location in ['top', 'above']:
        return f'▛{"▘" * hlf0} {message} {"▝" * hlf1}▜'
    elif location in ['bottom', 'bot', 'below']:
        return f'▙{"▖" * hlf0} {message} {"▗" * hlf1}▟'
    else:
        return f'(ノಠ益ಠ)ノ彡 {message.center(132 - 19, " ")} ¯\\(◉◡◔)/¯'


def flatten(itr: Union[tuple, list]) -> Generator:
    """Reduce embedded lists/tuples into a single list (generator)

    Args:
        itr (Union[tuple, list]):

    Returns:
        (Generator)"""
    for item in itr:
        if isinstance(item, (tuple, list)):
            yield from flatten(item)
        else:
            yield item


def generate_password(min_len=15, max_length=24) -> str:
    """Generate a Password

    Args:
        min_len (int): 15
        max_length (int): 24

    Returns:
        pwd (str)"""
    chars = list(flatten(['@', '#', '$', list(ascii_letters), list(digits)]))
    shuffle(chars)
    length = choice(range(min_len, max_length))

    pwd = list(f'{choice(ascii_uppercase)}{choice(ascii_lowercase)}{choice(digits)}{choice(["@", "#", "$"])}')
    pwd.extend([choice(chars) for _ in range((length - len(pwd)))])
    shuffle(pwd)
    pwd = ''.join(pwd)

    # Just to be sure the password meets requirements
    assert not length - len(pwd)  # Password is of desired length
    assert any(pwd) in ['@', '#', '$']
    assert any(pwd) in ascii_letters
    assert any(pwd) in digits

    return pwd


def tprint(results: Results, requests: Optional[Any] = None, top: Optional[Union[int, None]] = None) -> NoReturn:
    """Test Print

    Args:
        results (Results):
        requests (Optional[Any]):
        top (int):

    Returns:
        (NoReturn)"""
    top_hdr = f'Top {top} ' if top else ''

    print(f'\n{top_hdr}Success Result{"s" if len(results.success) > 1 else ""}: {len(results.success)}')
    if top:
        print(*results.success[:top], sep='\n')
    else:
        print(*results.success, sep='\n')

    print(f'\n{top_hdr}Failure Result{"s" if len(results.failure) > 1 else ""}: {len(results.failure)}')
    if top:
        print(*results.failure[:top], sep='\n')
    else:
        print(*results.failure, sep='\n')

    if requests:
        print(f'\n{top_hdr}Requests Result{"s" if len(results.success) > 1 else ""}: {len(requests)}')
        if top:
            print(*requests[:top], sep='\n')
        else:
            print(*requests, sep='\n')


if __name__ == '__main__':
    print(__doc__)

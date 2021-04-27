#!/usr/bin/env python3.8
"""Base Client API -> Utils
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
import inspect
from os.path import realpath
from random import choice, shuffle
from string import ascii_letters, ascii_lowercase, ascii_uppercase, digits
from typing import Any, Generator, List, NoReturn, Optional, Sized, Union

from aiofiles import open
from devtools import debug
from loguru import logger
from rich import inspect, print

from base_client_api.models.results import Results


def bprint(message: str, location: str = None) -> NoReturn:
    """Build a banner

    Args:
        message (str):
        location (str): ['top', 'above', None]

    Returns:
        msg (str)"""
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
        msg = f'\n▛{"▘" * hlf0} {message} {"▝" * hlf1}▜'
    elif location in ['bottom', 'bot', 'below']:
        msg = f'▙{"▖" * hlf0} {message} {"▗" * hlf1}▟\n'
    else:
        msg = f'▌{" " * hlf0} {message} {" " * hlf1}▐'

    print(msg)

    return


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


def tprint(results: Results, requests: Optional[Any] = None, top: Optional[int] = None) -> NoReturn:
    """Test Print

    Args:
        results (Results):
        requests (Optional[Any]):
        top (int):

    Returns:
        (NoReturn)"""
    # todo: if no text response received, return response status in response.failure instead of ''
    top_hdr = f'Top {top} ' if top else '1'

    print(
            f'\n{top_hdr if len(results.success) > 1 else ""}[bold green]Success Result{"s" if len(results.success) > 1 else ""}['
            f'/bold green] of {len(results.success)} Returned:')
    if top:
        debug(results.success[:top])
    else:
        debug(results.success)

    print(f'\n{top_hdr if len(results.failure) > 1 else ""}[bold red]Failure Result{"s" if len(results.failure) > 1 else ""}'
          f'[/bold red] of {len(results.failure)} Returned:')

    if top:
        debug(results.failure[:top])
    else:
        debug(results.failure)

    if requests:
        print(f'\n{top_hdr}Requests Result{"s" if len(results.success) > 1 else ""}: {len(requests)}')

        if top:
            debug(requests[:top])
        else:
            debug(requests)

    return


# todo: This needs testing (errors) when trying classes
def vprint(var: Sized, str_output: bool = True) -> Optional[str]:
    """Variable Printer
       - Prints the name of the variable, length, and value.
       -- [<variable_name>] (<variable_length>): <variable_content>

    NOTE: Not all objects support length

    Args:
        var (object)
        str_output (bool): If false will print instead of returning a string

    Returns:
        output (str)"""
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()

    for var_name, var_val in callers_local_vars:
        if var_val is var:
            t = str(type(var))
            typ = t[t.index("'") + 1:-2]

            try:
                length = len(var)
            except TypeError:
                length = 'N/A'

            if t is list:
                output = f'{var_name}: {typ} = ({length}):'
                output += [f'\t{i}' for i in var_val]
            elif t is dict:
                output = f'{var_name}: {typ} = ({length}):'
                output += [f'\t{k}: {v}' for k, v in var_val.items()]
            else:
                output = f'{var_name}: {typ} = ({length}) {var_val}'

            if str_output:
                return output
            else:
                print(output)
                return
        else:
            logger.error('var_val is not var')


def sort_dict(dct: dict, reverse: Optional[bool] = False) -> dict:
    """Sort a dictionary, recursively, by keys.

    Args:
        dct (dict):
        reverse (bool):

    Returns:
        (dict)"""
    items: List[List[dict]] = [[k, v] for k, v in sorted(dct.items(), key=lambda x: x[0], reverse=reverse)]

    for item in items:
        if isinstance(item[1], dict):
            item[1] = sort_dict(item[1], reverse=reverse)

    return dict(items)


async def file_streamer(file_path: str) -> bytes:
    """File Streamer

    Streams a file from disk.

    Args:
        file_path (str):

    Returns:
        chunk (bytes)"""
    async with open(realpath(file_path), 'rb') as f:
        while chunk := await f.read(1024):
            yield chunk


def pascal_case(value) -> str:
    """Convert Case

    Converts snake case to pascal case for JSON

    Args:
        value (str):

    References:
        https://stackoverflow.com/questions/17326185/what-are-the-different-kinds-of-cases

    Raises:
        ValueError

    Returns:
        (str)"""
    words = value.split('_')
    new_words = [words[0]]
    [new_words.append(x.capitalize()) for x in words[1:]]

    return ''.join(new_words)


if __name__ == '__main__':
    print(__doc__)

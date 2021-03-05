#!/usr/bin/env python3.9
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
from random import choice, shuffle
from string import ascii_letters, ascii_lowercase, ascii_uppercase, digits
from typing import Any, Generator, NoReturn, Optional, Sized, Union

from loguru import logger
from pydantic import validator

from base_client_api.models import Results

CASE_TYPES = ['flat', 'flat_upper', 'camel', 'pascal', 'snake', 'snake_pascal', 'snake_camel', 'kebab', 'train', 'underscore_camel']


@logger.catch
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


@logger.catch
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


@logger.catch
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


@logger.catch
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

    return


@logger.catch
def vprint(var: Sized, str_output: bool = True) -> Union[str, NoReturn]:
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


@logger.catch()
def convert_case(var_name: str, from_type: str = 'snake', to_type: str = 'camel') -> str:
    """Convert Case

    Converts variable names between case types

    Args:
        var_name (str):
        from_type (str):
        to_type (str):

    References:
        https://stackoverflow.com/questions/17326185/what-are-the-different-kinds-of-cases

    Raises:
        ValueError

    Returns:
        new_var (str)"""

    # todo: handle additional case types
    # todo: add automatic detection of source type

    @validator('from_type', 'to_type')
    def check_types(cls, value) -> str:
        """Check Types

        Validates parameters

        Args:
            cls (class):
            value (str):

        Raises:
             ValueError

        Returns:
            value (str)"""
        if value in CASE_TYPES:
            return value
        else:
            raise ValueError(f'Case types must be one of: {CASE_TYPES}')

    if from_type == 'snake':
        words = var_name.split('_')
    else:
        raise ValueError('The casing provided is not handled at this time.')

    return f'{words[0].lower()}{"".join(words[1:]).capitalize()}'


if __name__ == '__main__':
    print(__doc__)

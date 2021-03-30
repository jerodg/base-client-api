#!/usr/bin/env python3.8
"""Base Client API -> Models -> Record
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
from typing import Any, Callable, Optional

from base_client_api.models.base import Base


class Record(Base):
    """Generic Record"""
    body: Optional[Base]

    def dict(self, *,
             include: set = None,
             exclude: set = None,
             by_alias: bool = False,
             skip_defaults: bool = None,
             exclude_unset: bool = False,
             exclude_defaults: bool = False,
             exclude_none: bool = True) -> dict:
        """Dictionary

        Args:
            include (set):
            exclude (set):
            by_alias (bool):
            skip_defaults (bool):
            exclude_unset (bool):
            exclude_defaults (bool):
            exclude_none (bool):

        Returns:
            dct (Dict[str, Any])"""
        return super().dict(include=include,
                            exclude=exclude,
                            by_alias=by_alias,
                            skip_defaults=skip_defaults,
                            exclude_unset=exclude_unset,
                            exclude_defaults=exclude_defaults,
                            exclude_none=exclude_none)

    def json(self, *,
             include: Optional[set] = None,
             exclude: set = None,
             by_alias: bool = True,
             skip_defaults: bool = None,
             exclude_unset: bool = False,
             exclude_defaults: bool = False,
             exclude_none: bool = True,
             encoder: Optional[Callable[[Any], Any]] = None,
             **dumps_kwargs: Any) -> str:
        """JSON as String

        Args:
            include (set):
            exclude (set):
            by_alias (bool):
            skip_defaults (bool):
            exclude_unset (bool):
            exclude_defaults (bool):
            exclude_none (bool):
            encoder (Callable):

        Returns:
            (str)"""
        return super().json(include=include,
                            exclude=exclude,
                            by_alias=by_alias,
                            skip_defaults=skip_defaults,
                            exclude_unset=exclude_unset,
                            exclude_defaults=exclude_defaults,
                            exclude_none=exclude_none,
                            encoder=encoder)

    @property
    def endpoint(self) -> str:
        """Endpoint

        The suffix end of the URI

        Returns:
            (str)"""
        return '/'

    @property
    def response_key(self) -> Optional[str]:
        """Data Key

        This is the key used in the return dict that holds the primary responses

        Returns:
            (str)"""
        return None

    @property
    def method(self) -> Optional[str]:
        """Method

        The HTTP verb to be used
         - Must be a valid HTTP verb as listed above in METHODS

        Returns:
            (str)"""
        return None

    @property
    def parameters(self) -> Optional[str]:
        """URL Parameters

        If you need to pass parameters in the URL

        Returns:
            (dict)"""
        return self.json(exclude={'body'})

    @property
    def headers(self) -> Optional[dict]:
        """Headers

        If you need to pass non-default headers

        Returns:
            (dict)"""
        return None

    @property
    def json_body(self) -> Optional[dict]:
        """Request Body"""
        if self.body:
            return self.body.dict()

        return self.dict()

    # todo: implement
    # @staticmethod
    # def form_data(file: Optional[str]) -> Optional[dict]:
    #     """Request Body
    #        - Multipart Form or Form URL Encoded"
    #
    #     Args:
    #         file (str): Full path of file
    #
    #     Returns:
    #         (Optional[dict])
    #     """
    #     data = None
    #     if file:
    #         data = {**data, 'file': file_streamer(file)}
    #
    #     return data if data else {}


if __name__ == '__main__':
    print(__doc__)

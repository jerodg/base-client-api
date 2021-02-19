#!/usr/bin/env python3.9
"""Base Client API
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
from asyncio import Semaphore
from json.decoder import JSONDecodeError
from logging import DEBUG, WARNING
from os import getenv
from os.path import basename, realpath
from ssl import create_default_context, Purpose, SSLContext
from typing import List, NoReturn, Optional, Union
from uuid import uuid4

import aiofiles
import aiohttp as aio
import rapidjson
import toml
from loguru import logger
from multidict import MultiDict
from tenacity import after_log, before_sleep_log, retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from .models import Results

logger.add(basename(__file__)[:-3])
logger.disable(basename(__file__)[:-3])  # Because this is a library; use logger.enable('base_client') in script to see log msgs.


class BaseClientApi(object):
    """ Base Client API"""
    HDR: dict = {'Content-Type': 'application/json; charset=utf-8'}
    SEM: int = 15  # This defines the number of parallel requests to make.

    def __init__(self, cfg: Optional[Union[str, dict]] = None):
        self.debug: bool = False
        self.cfg: Union[dict, None] = None
        self.proxy: Union[str, None] = None
        self.proxy_auth: Union[aio.BasicAuth, None] = None
        self.sem: Union[Semaphore, None] = None
        self.session: Union[aio.ClientSession, None] = None
        self.ssl: Union[SSLContext, None] = None

        cfg = self.__load_config_data(cfg)
        self.process_config(cfg)
        self.session_config(cfg)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def __load_config_data(self, cfg_data: Union[str, dict]) -> dict:
        """Load Configuration Data

        Args:
            cfg_data (Union[str, dict): str; path to config file [toml|json]
                                   dict; dictionary matching config example
                Values expressed in example config can be overridden by OS
                environment variables.

        Returns:
            cfg (dict)"""
        if type(cfg_data) is dict:
            cfg = cfg_data
        elif type(cfg_data) is str:
            if cfg_data.endswith('.toml'):
                cfg = toml.load(cfg_data)
            elif cfg_data.endswith('.json'):
                cfg = rapidjson.loads(open(cfg_data).read(), ensure_ascii=False)
            else:
                logger.error(f'Unknown configuration file type: {cfg_data.split(".")[1]}\n-> Valid Types: .toml | .json')
                raise NotImplementedError
        else:
            cfg = None

        if env_auth_user := getenv('Auth_Username'):
            cfg['Auth']['Username'] = env_auth_user

        if env_auth_pass := getenv('Auth_Password'):
            cfg['Auth']['Password'] = env_auth_pass

        if env_auth_header := getenv('Auth_Header'):
            cfg['Auth']['Header'] = env_auth_header

        if env_auth_token := getenv('Auth_Token'):
            cfg['Auth']['Token'] = env_auth_token

        if env_uri_base := getenv('URI_Base'):
            cfg['URI']['Base'] = env_uri_base

        if env_opt_ca := getenv('Options_CAPath'):
            cfg['Options']['CAPath'] = env_opt_ca

        if env_opt_ssl := getenv('Options_VerifySSL'):
            cfg['Options']['VerifySS:'] = env_opt_ssl

        if env_opt_dbg := getenv('Options_Debug'):
            cfg['Options']['Ddebug'] = env_opt_dbg

        if env_opt_sem := getenv('Options_SEM'):
            cfg['Options']['SEM'] = env_opt_sem

        if env_prxy_uri := getenv('Proxy_URI'):
            cfg['Proxy']['URI'] = env_prxy_uri

        if env_prxy_port := getenv('Proxy_Port'):
            cfg['Proxy']['Port'] = env_prxy_port

        if env_prxy_user := getenv('Proxy_Username'):
            cfg['Proxy']['Username'] = env_prxy_user

        if env_prxy_pass := getenv('Proxy_Password'):
            cfg['Proxy']['Password'] = env_prxy_pass

        self.cfg = cfg

        return cfg

    def process_config(self, cfg_data: dict) -> NoReturn:
        """Process Configuration

        Args:
            cfg_data (dict):

        Returns:
            N/A (NoReturn)"""
        try:
            if cfg_data['Options']['Debug']:
                self.debug = True
        except (KeyError, TypeError):
            self.debug = False

        try:
            proxy_uri = cfg_data['Proxy']['URI']
        except (KeyError, TypeError):
            proxy_uri = None

        try:
            proxy_port = cfg_data['Proxy']['Port']
        except (KeyError, TypeError):
            proxy_port = ''

        try:
            proxy_user = cfg_data['Proxy']['Username']
        except (KeyError, TypeError):
            proxy_user = None

        try:
            proxy_pass = cfg_data['Proxy']['Password']
        except (KeyError, TypeError):
            proxy_pass = None

        if proxy_uri:
            self.proxy = f'{proxy_uri}{":" if proxy_port else ""}{proxy_port}'

        if proxy_user:
            self.proxy_auth = aio.BasicAuth(login=proxy_user, password=proxy_pass)

        try:
            sem = cfg_data['Options']['SEM']
        except (KeyError, TypeError):
            sem = self.SEM

        self.sem = asyncio.Semaphore(sem)

        try:
            ca_key = cfg_data['Options']['CAPath']
        except (KeyError, TypeError):
            ca_key = None

        try:
            verify_ssl = cfg_data['Options']['VerifySSL']
        except (KeyError, TypeError):
            verify_ssl = False

        if ca_key:
            self.ssl = create_default_context(purpose=Purpose.CLIENT_AUTH, capath=ca_key)
        else:
            self.ssl = verify_ssl

    def session_config(self, cfg: dict) -> NoReturn:
        """Session Configuration

        Args:
            cfg (dict):

        Returns:
            N/A (NoReturn)"""
        # Auth
        try:
            username = cfg['Auth']['Username']
        except (KeyError, TypeError):
            username = None

        try:
            password = cfg['Auth']['Password']
        except (KeyError, TypeError):
            password = None

        if username or password:
            auth = aio.BasicAuth(login=username, password=password)
        else:
            auth = None

        # Cookies; Can't be overwridden by env_vars; Must be a dct
        try:
            cookies = cfg['Cache']['Cookies']
        except (KeyError, TypeError):
            cookies = None

        # Cookie Jar
        try:
            cookie_jar_unsafe = cfg['Options']['CookieJar_Unsafe']
        except (KeyError, TypeError):
            cookie_jar_unsafe = False

        # Headers
        try:
            auth_hdr = cfg['Auth']['Header']
        except (KeyError, TypeError):
            auth_hdr = None

        try:
            auth_tkn = cfg['Auth']['Token']
        except (KeyError, TypeError):
            auth_tkn = None

        try:
            content_type = cfg['Options']['Content_type']
        except (KeyError, TypeError):
            content_type = 'application/json; charset=utf-8'

        if auth_hdr and auth_tkn:
            hdrs = {'Content-Type': content_type, auth_hdr: auth_tkn}
        else:
            hdrs = self.HDR

        self.session = aio.ClientSession(auth=auth,
                                         cookies=cookies,
                                         cookie_jar=aio.CookieJar(unsafe=cookie_jar_unsafe),
                                         headers=hdrs,
                                         json_serialize=rapidjson.dumps,
                                         timeout=aio.ClientTimeout(total=300))

    @staticmethod
    async def request_debug(response: aio.ClientResponse) -> str:
        """Request Debug

        Args:
            response (aio.ClientResponse):

        Returns:
            (str)"""
        hdr = '\n\t\t'.join(f'{k}: {v}' for k, v in response.headers.items())
        try:
            j = rapidjson.dumps(await response.json(content_type=None), ensure_ascii=False)
            t = None
        except JSONDecodeError:
            j = None
            t = await response.text()

        return f'\nHTTP/{response.version.major}.{response.version.minor}, {response.method}-{response.status}[{response.reason}]' \
               f'\n\tRequest-URL: \n\t\t{response.url}\n' \
               f'\n\tHeader: \n\t\t{hdr}\n' \
               f'\n\tResponse-JSON: \n\t\t{j}\n' \
               f'\n\tResponse-TEXT: \n\t\t{t}\n'

    async def process_results(self, results: Results,
                              data_key: Optional[str] = None,
                              cleanup: bool = False,
                              sort_field: Optional[str] = None,
                              sort_order: Optional[str] = None,
                              remove_request_id: bool = True) -> Results:
        """Process Results from aio.ClientRequest(s)

        Args:
        results (List[Union[dct, aio.ClientResponse]]):
        success (List[dct]):
        failure (List[dct]):
        data_key (Optional[str]):
        cleanup (Optional[bool]): Default: True
            Removes raw results, Removes empty (None) keys, and Sorts Keys of each record.
        sort_field (Optional[str]): Top incident_level dictionary key to sort on
        sort_order (Optional[str]): Direction to sort ASC | DESC (any case)
            Performs generic sort if sort_field not specified.

        Returns:
            results (Results): """
        for result in results.data:
            rid = {'request_id': result['request_id']}
            status = result['response'].status

            try:
                if result['response'].headers['Content-Type'].startswith('application/jwt'):
                    response = {'token': await result['response'].text(encoding='utf-8'), 'token_type': 'Bearer'}
                elif result['response'].headers['Content-Type'].startswith('application/json'):
                    response = await result['response'].json(encoding='utf-8', loads=rapidjson.loads)
                elif result['response'].headers['Content-Type'].startswith('application/javascript'):
                    response = await result['response'].json(encoding='utf-8', loads=rapidjson.loads,
                                                             content_type='application/javascript')
                elif result['response'].headers['Content-Type'].startswith('text/javascript'):
                    response = await result['response'].json(encoding='utf-8', loads=rapidjson.loads,
                                                             content_type='text/javascript')
                elif result['response'].headers['Content-Type'].startswith('text/plain'):
                    response = {'text_plain': await result['response'].text(encoding='utf-8')}
                elif result['response'].headers['Content-Type'].startswith('text/html'):
                    response = {'text_html': await result['response'].text(encoding='utf-8')}
                else:
                    logger.error(f'Content-Type: {result["response"].headers["Content-Type"]}, not currently handled.')
                    raise NotImplementedError
            except KeyError as ke:  # fixme: (improve this note) This shouldn't happen too often.
                logger.warning(ke)
                response = await result['response'].text(encoding='utf-8')

            # This is for when the 'Content-Type' is specified as JSON but is actually returned as a string by the API.
            if type(response) == str:
                response = {'text_plain': await result['response'].text(encoding='utf-8')}

            if 200 <= status <= 299:
                try:
                    d = response[data_key]
                    if type(d) is list:
                        data = [{**r, **rid} for r in d]
                    else:
                        data = response
                except (KeyError, TypeError):
                    if type(response) is list:
                        data = [{**r, **rid} for r in response]
                    elif type(response) is int:
                        data = [response]
                    else:
                        data = {**response, **rid}

                if type(data) is list:
                    results.success.extend(data)
                else:
                    results.success.append(data)

            elif status > 299:
                try:
                    results.failure.append({**response, **rid})
                except TypeError:
                    results.failure.append(response)

        if cleanup:
            del results.data
            results.success = [dict(sorted({k: v for k, v in rec.items() if v is not None}.items())) for rec in results.success]

        if sort_order:
            sort_order = sort_order.lower()

        if sort_field:
            results.success.sort(key=lambda k: k[sort_field], reverse=True if sort_order == 'desc' else False)
        elif sort_order:
            results.success.sort(reverse=True if sort_order == 'desc' else False)

        if remove_request_id:
            for result in results.success:
                if not type(result) is int:
                    del result['request_id']

        return results

    @staticmethod
    async def file_streamer(file_path: str) -> bytes:
        """File Streamer

        Streams a file from disk.

        Args:
            file_path (str):

        Returns:
            chunk (bytes)"""

        async with aiofiles.open(realpath(file_path), 'rb') as f:
            while chunk := await f.read(1024):
                yield chunk

    @retry(retry=retry_if_exception_type(aio.ClientError),
           wait=wait_random_exponential(multiplier=1.25, min=3, max=60),
           after=after_log(logger, DEBUG),
           stop=stop_after_attempt(5),
           before_sleep=before_sleep_log(logger, WARNING))
    async def request(self, method: str, end_point: str,
                      request_id: Optional[str] = None,
                      data: Optional[Union[dict, aio.FormData]] = None,
                      json: Optional[dict] = None,
                      params: Optional[Union[List[tuple], dict, MultiDict]] = None,
                      file: Optional[str] = None,
                      debug: Optional[bool] = False) -> dict:
        """Multi-purpose aiohttp request function
        Args:
            file (Optional[str]): A valid file-path
            method (str): A valid HTTP Verb in [GET, POST]
            end_point (str): REST Endpoint; e.g. /devices/query
            request_id (str): Unique Identifier used to associate request with response
            data (Optional[dct]):
            json (Optional[dct]):
            params (Optional[Union[List[tuple], dct, MultiDict]]):
            debug (Optional[bool]):

        References:
            https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods

        Raises:
            NotImplementedError

        Returns:
            (dict)"""
        if not request_id:
            request_id = uuid4().hex

        if file:
            data = {**data, 'file': self.file_streamer(file)}

        try:
            base = self.cfg['URI']['Base']
        except TypeError:
            base = ''

        async with self.sem:
            if method == 'get':
                response = await self.session.get(url=f'{base}{end_point}',
                                                  ssl=self.ssl,
                                                  proxy=self.proxy,
                                                  proxy_auth=self.proxy_auth,
                                                  params=params)
            elif method == 'patch':
                response = await self.session.patch(url=f'{base}{end_point}',
                                                    ssl=self.ssl,
                                                    proxy=self.proxy,
                                                    proxy_auth=self.proxy_auth,
                                                    data=data,
                                                    json=json,
                                                    params=params)
            elif method == 'post':
                response = await self.session.post(url=f'{base}{end_point}',
                                                   ssl=self.ssl,
                                                   proxy=self.proxy,
                                                   proxy_auth=self.proxy_auth,
                                                   data=data,
                                                   json=json,
                                                   params=params)
            elif method == 'put':
                response = await self.session.put(url=f'{base}{end_point}',
                                                  ssl=self.ssl,
                                                  proxy=self.proxy,
                                                  proxy_auth=self.proxy_auth,
                                                  data=data,
                                                  json=json,
                                                  params=params)
            elif method == 'delete':
                response = await self.session.delete(url=f'{base}{end_point}',
                                                     ssl=self.ssl,
                                                     proxy=self.proxy,
                                                     proxy_auth=self.proxy_auth,
                                                     data=data,
                                                     json=json,
                                                     params=params)
            else:
                logger.error(f'Request-Method: {method}, not currently handled.')
                raise NotImplementedError

            if self.debug or debug:
                print(await self.request_debug(response))

            try:
                assert not response.status > 499
            except AssertionError:
                logger.error(self.request_debug(response))
                raise aio.ClientError

            return {'request_id': request_id, 'response': response}


if __name__ == '__main__':
    print(__doc__)

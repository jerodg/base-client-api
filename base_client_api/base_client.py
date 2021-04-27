#!/usr/bin/env python3.8
"""Base Client API -> Base Client
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
from pprint import pformat
from ssl import create_default_context, Purpose, SSLContext
from typing import List, NoReturn, Optional, Union
from urllib.parse import unquote_plus

import aiohttp as aio
import rapidjson
import toml
from loguru import logger
from rich import print
from tenacity import after_log, before_sleep_log, retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from base_client_api.models.record import Record
from base_client_api.models.results import Results


# todo: handle form data
# todo: add AWS secrets manager to config load
# todo: cleanup/refactor config load
# todo: switch to pydantic settings loader?


class BaseClientApi:
    """Base Client API"""
    HDR: dict = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
    SEM: int = 5  # This defines the number of parallel requests to make.

    def __init__(self, cfg: Union[str, dict, List[Union[str, dict]]] = None):
        self.debug: bool = False
        self.auth: Optional[aio.BasicAuth] = None
        self.proxy: Optional[str] = None
        self.proxy_auth: Optional[aio.BasicAuth] = None
        self.sem: Optional[Semaphore] = None
        self.session: Optional[aio.ClientSession] = None
        self.ssl: Optional[SSLContext] = None
        self.cfg: Optional[dict] = None

        self.load_config_data(cfg)
        self.process_config(self.cfg)
        self.session_config(self.cfg)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def load_config_data(self, cfg_data: Union[str, dict, List[Union[str, dict]]]) -> NoReturn:
        """Load Configuration Data

        Args:
            cfg_data (Union[str, dict): str; path to config file [toml|json]
                                   dict; dictionary matching config example
                Values expressed in example config can be overridden by OS
                environment variables.

        Returns:
            (NoReturn)"""
        if type(cfg_data) is not list:
            cfg_data = [cfg_data]

        for c in cfg_data:
            if type(c) is dict:
                cfg = c
            if type(c) is str:
                if c.endswith('.toml'):
                    cfg = toml.load(c)
                elif c.endswith('.json'):
                    cfg = rapidjson.loads(open(cfg_data).read(), ensure_ascii=False)
                else:
                    logger.error(f'Unknown configuration file type: {c.split(".")[1]}\n-> Valid Types: .toml | .json')
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

            return

    def process_config(self, cfg_data: dict) -> bool:
        """Process Configuration

        Args:
            cfg_data (dict):

        Returns:
            (bool)"""
        try:
            if cfg_data['Options']['Debug']:
                self.debug = True
        except (KeyError, TypeError):
            self.debug = False

        try:
            if usr := cfg_data['Auth']['Username']:
                if pwd := cfg_data['Auth']['Password']:
                    self.auth = aio.BasicAuth(login=usr, password=pwd)
        except (KeyError, TypeError):
            pass  # If we don't have credentials we don't need to create this.

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

        return True

    def session_config(self, cfg: dict) -> bool:
        """Session Configuration

        Args:
            cfg (dict):

        Returns:
            (bool)"""
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

        return True

    @staticmethod
    async def request_debug(response: aio.ClientResponse) -> str:
        """Request Debug

        Args:
            response (aio.ClientResponse):

        Returns:
            (str)"""
        try:
            hdr = '\n\t\t'.join(f'{k}: {v}' for k, v in response.headers.items())
        except AttributeError as ae:
            logger.warning(ae)
            hdr = None

        try:
            json = await response.json(content_type=None)
            json = pformat(json, sort_dicts=False)
            text = None
        except JSONDecodeError:
            json = None
            text = await response.text()
        except AttributeError as ae:
            logger.warning(ae)
            json = None
            text = None
            print('response_error:', response)

        # todo: convert to a template
        return f'\n[bold yellow]HTTP[/bold yellow]/{response.version.major}.{response.version.minor}, {response.method}-' \
               f'{response.status}[{response.reason}]' \
               f'\n\t[bold yellow]Request-URL:[/bold yellow] \n\t\t{unquote_plus(f"{response.url}")}\n' \
               f'\n\t[bold yellow]Header:[/bold yellow] \n\t\t{hdr}\n' \
               f'\n\t[bold yellow]Response-JSON:[/bold yellow] \n{json}\n' \
               f'\n\t[bold yellow]Response-TEXT:[/bold yellow] \n\t\t{text}\n'

    async def process_results(self, results: Results,
                              model: Record,
                              cleanup: bool = False,
                              sort_field: Optional[str] = None,
                              sort_order: Optional[str] = None) -> Results:
        """Process Results from aio.ClientRequest(s)

        Args:
        results (List[Union[dct, aio.ClientResponse]]):
        success (List[dct]):
        failure (List[dct]):
        model   (Record):
        cleanup (Optional[bool]):
            Removes raw results, Removes empty (None) keys, and Sorts Keys of each record.
        sort_field (Optional[str]): Top incident_level dictionary key to sort on
        sort_order (Optional[str]): Direction to sort ASC | DESC (any case)
            Performs generic sort if sort_field not specified.

        Returns:
            results (Results): """
        for result in results.responses:
            status = result.status

            try:
                # todo: switch to pattern matching/case statement in python 3.10
                if result.headers['Content-Type'].startswith('application/jwt'):
                    response = {'token': await result.text(encoding='utf-8'), 'token_type': 'Bearer'}

                elif result.headers['Content-Type'].startswith('application/json'):
                    response = await result.json(encoding='utf-8', loads=rapidjson.loads)

                elif result.headers['Content-Type'].startswith('application/javascript'):
                    response = await result.json(encoding='utf-8', loads=rapidjson.loads,
                                                 content_type='application/javascript')

                elif result.headers['Content-Type'].startswith('text/javascript'):
                    response = await result.json(encoding='utf-8', loads=rapidjson.loads,
                                                 content_type='text/javascript')

                elif result.headers['Content-Type'].startswith('text/plain'):
                    response = {'text_plain': await result.text(encoding='utf-8')}

                elif result.headers['Content-Type'].startswith('text/html'):
                    response = {'text_html': await result.text(encoding='utf-8')}

                elif result.headers['Content-Type'].startswith('application/problem+json'):
                    response = await result.json(encoding='utf-8', loads=rapidjson.loads)
                    logger.error(await self.request_debug(response))

                else:
                    logger.error(f'Content-Type: {result.headers["Content-Type"]} is not currently handled.')
                    response = await result.text(encoding='utf-8')

            except KeyError as ke:  # No Content-Type returned
                logger.warning(ke)
                response = await result.text(encoding='utf-8')

            # This is for when the 'Content-Type' is specified as non-text but is actually returned as a string by the API.
            if type(response) == str and len(response):
                response = {'text_plain': await result.text(encoding='utf-8')}

            if 200 <= status <= 299:
                try:
                    d = model.response_key
                    if type(d) is list:
                        data = [{**r} for r in d]
                    else:
                        data = response
                except (KeyError, TypeError):
                    if type(response) is list:
                        data = [{**r} for r in response]
                    elif type(response) is int:
                        data = [response]
                    else:
                        data = {**response}

                if type(data) is list:
                    results.success.extend(data)
                else:
                    results.success.append(data)

            elif status > 299:
                try:
                    results.failure.append({**response})
                except TypeError:
                    results.failure.append(response)

        if cleanup:
            del results.responses
            results.success = [dict(sorted({k: v for k, v in rec.items() if v is not None}.items())) for rec in results.success]

        if sort_order:
            sort_order = sort_order.lower()

        if sort_field:
            results.success.sort(key=lambda k: k[sort_field], reverse=True if sort_order == 'desc' else False)
        elif sort_order:
            results.success.sort(reverse=True if sort_order == 'desc' else False)

        return results

    @retry(retry=retry_if_exception_type(aio.ClientError),
           wait=wait_random_exponential(multiplier=1.25, min=3, max=60),
           after=after_log(logger, DEBUG),
           stop=stop_after_attempt(5),
           before_sleep=before_sleep_log(logger, WARNING))
    async def request(self, model: Record, debug: Optional[bool] = False) -> aio.ClientResponse:
        """Multi-purpose aiohttp request function
        Args:
            model (dataclass): Optionally defined:
                               - file (Optional[str]): A valid file-path
                               - method (str): A valid HTTP Verb in [GET, POST]
                               - end_point (str): REST Endpoint; e.g. /devices/query
                               - data (Optional[dct]):
                               - json (Optional[dct]):
                               - params (Optional[Union[List[tuple], dct, MultiDict]]):
            debug (Optional[bool]):

        References:
            https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods

        Raises:
            InvalidOptionError
            NotImplementedError

        Returns:
            (Optional[dict])"""
        try:
            base = self.cfg['URI']['Base']
        except TypeError:
            base = ''

        async with self.sem:
            response = await self.session.request(auth=self.auth,
                                                  # data=model.form_data,  # todo: implement this
                                                  headers=model.headers or self.HDR,
                                                  json=model.json_body,
                                                  method=model.method,
                                                  params=model.parameters,
                                                  proxy=self.proxy,
                                                  proxy_auth=self.proxy_auth,
                                                  ssl=self.ssl,
                                                  url=f'{base}{model.endpoint}')

            # todo: change to template
            if self.debug or debug:
                print(f'auth: {self.auth}')
                print(f'headers: {model.headers}')
                print(f'json: {model.json_body}')
                print(f'params: {model.parameters}')
                print(f'proxy: {self.proxy}')
                print(f'proxy_auth: {self.proxy_auth}')
                print(await self.request_debug(response))

            try:
                assert not response.status > 499
            except AssertionError:
                logger.error(self.request_debug(response))
                raise aio.ClientError

            return response

    async def make_request(self, models: List[Record], debug: Optional[bool] = False) -> Results:
        """Make Request

        This is a convenience method to make calling easier.
        It can be overridden to provide additional functionality.

        Args:
            models (List[Record]): If sending a list of models they must be all of the same type
            debug (bool):

        Returns:
            results (Reults)"""
        if type(models) is not list:
            models = [models]

        results = await asyncio.gather(*[asyncio.create_task(self.request(m, debug=debug)) for m in models])
        return await self.process_results(results=Results(responses=results), model=models[0].__class__)


if __name__ == '__main__':
    print(__doc__)

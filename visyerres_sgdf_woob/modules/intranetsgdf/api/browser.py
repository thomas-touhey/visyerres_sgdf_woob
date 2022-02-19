#!/usr/bin/env python
# *****************************************************************************
# Copyright (C) 2022 Thomas Touhey <thomas@touhey.fr>
#
# This software is licensed as described in the file LICENSE, which you
# should have received as part of this distribution.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# *****************************************************************************
""" intranetsgdf API browser definition.

    This browser interacts with the intranet API, which renders some intranet
    data (although not all of it) accessible in a programmatic way for other
    applications to access.

    It however requires a client_id / client_secret pair, which are provided
    by the SGDF SI (Système d'Information) service, which haven't answered
    as of Jan. 2022 to my requests to get one for Vis'Yerres.
"""

from datetime import datetime as _datetime
from os import environ as _environ
from typing import Optional as _Optional

from woob.browser.browsers import (
    LoginBrowser as _LoginBrowser, StatesMixin as _StatesMixin, URL as _URL,
    need_login as _need_login,
)

from .pages import TokenPage as _TokenPage

__all__ = ['IntranetSGDFAPIBrowser']


class IntranetSGDFAPIBrowser(_LoginBrowser, _StatesMixin):
    """
    Browser for the intranet API.

    This class is inspired from the following class in the Java
    client implementation:

    https://gitlab.com/sgdf/api-intranet-java

    Most notably the following files:

    * src/main/java/fr/sgdf/intranetapi/ApiSession.java (auth & request)

    Which is probably quite inspired in design from some WebServices
    on the directaccess intranet, notably the ``Authentification.asmx``
    WebService.
    """

    __state__ = (
        'access_token', 'access_token_type', 'access_token_expires_at_s',
        'refresh_token',
    )

    BASEURL = _environ.get(
        'INTRANETAPI_BASEURL',
        'https://intranetapi.sgdf.fr',
    )

    client_id: _Optional[str] = None
    audience: _Optional[str] = None
    access_token: _Optional[str] = None
    access_token_type: _Optional[str] = None
    access_token_expires_at: _Optional[_datetime] = None
    refresh_token: _Optional[str] = None

    token_page = _URL(
        r'/oauth2/token',
        _TokenPage,
    )

    def __init__(self, config, *args, **kwargs):
        super(IntranetSGDFAPIBrowser, self).__init__(
            config['code'].get(),
            config['password'].get(),
            *args,
            **kwargs,
        )

        self.client_id = config['api_client_id'].get()
        self.audience = config['api_audience'].get()

        for attr in ('client_id', 'audience'):
            if not getattr(self, attr):
                raise ValueError(f'Missing configuration param {attr!r}.')

    def build_request(self, url, *args, **kwargs):
        headers = kwargs.setdefault('headers', {})

        if not self.token_page.match(url):
            headers['idAppelant'] = self.client_id

            if self.logged:
                headers['Authorization'] = (
                    f'{self.access_token_type or "Bearer"} {self.access_token}'
                )

        return super(IntranetSGDFAPIBrowser, self).build_request(
            url,
            *args,
            **kwargs,
        )

    @property
    def logged(self):
        return self.access_token and (
            not self.access_token_expires_at
            or self.access_token_expires_at < _datetime.utcnow()
        )

    @property
    def access_token_expires_at_s(self):
        value = self.access_token_expires_at
        if value is not None:
            value = value.isoformat()
        return value

    @access_token_expires_at_s.setter
    def access_token_expires_at_s(self, value):
        if isinstance(value, str):
            value = value.fromisoformat()
        self.access_token_expires_at = value

    def do_login(self):
        data = {
            'client_id': self.client_id,
            'audience': self.audience,
        }

        if self.refresh_token:
            data.update({
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'no_refresh': 'false',
            })
        else:
            data.update({
                'grant_type': 'password',
                'username': self.username,
                'password': self.password,
            })

        self.token_page.go(data=data)
        data = self.page.get_access_data()

        self.access_token = data._access_token
        self.access_token_type = data._access_token_type
        self.access_token_expires_at = data._access_token_expires_at
        self.refresh_token = data._refresh_token

# End of file.

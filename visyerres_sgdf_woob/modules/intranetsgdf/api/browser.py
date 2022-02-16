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
)

from .pages import TokenPage as _TokenPage

__all__ = ['IntranetSGDFAPIBrowser']


class IntranetSGDFAPIBrowser(_LoginBrowser, _StatesMixin):
    __state__ = (
        'access_token', 'access_token_type', 'access_token_expires_at_s',
        'refresh_token',
    )

    BASEURL = _environ.get(
        'INTRANETAPI_BASEURL',
        'https://intranetapi.sgdf.fr',
    )

    client_id: str
    audience: str
    access_token: _Optional[str] = None
    access_token_type: _Optional[str] = None
    access_token_expires_at: _Optional[_datetime] = None
    refresh_token: _Optional[str] = None

    token_page = _URL(
        r'/oauth2/token',
        _TokenPage,
    )

    def __init__(self, client_id, audience, *args, **kwargs):
        super(IntranetSGDFAPIBrowser, self).__init__(*args, **kwargs)

        self.client_id = client_id
        self.audience = audience

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

    def build_request(self, *args, **kwargs):
        headers = kwargs.setdefault('headers', {})
        if self.logged:
            headers['Authorization'] = (
                f'{self.access_token_type or "Bearer"} {self.access_token}'
            )

        return super(IntranetSGDFAPIBrowser, self).build_request(
            *args,
            **kwargs,
        )

    def do_login(self):
        if self.refresh_token:
            self.token_page.go(data={
                'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'audience': self.audience,
                'refresh_token': self.refresh_token,
                'no_refresh': 'false',
            })
        else:
            self.refresh_token(data={
                'grant_type': 'password',
                'client_id': self.client_id,
                'audience': self.audience,
                'username': self.username,
                'password': self.password,
            })

        data = self.page.get_access_data()

        self.access_token = data._access_token
        self.access_token_type = data._access_token_type
        self.access_token_expires_at = data._access_token_expires_at
        self.refresh_token = data._refresh_token

# End of file.

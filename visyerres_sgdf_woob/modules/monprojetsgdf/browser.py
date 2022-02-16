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
""" monprojetsgdf browser definition. """

from os import environ as _environ

from woob.browser.browsers import (
    LoginBrowser as _LoginBrowser, URL as _URL, need_login as _need_login,
)
from woob.exceptions import (
    BrowserHTTPError as _BrowserHTTPError,
    BrowserIncorrectPassword as _BrowserIncorrectPassword,
    BrowserUnavailable as _BrowserUnavailable,
)

from .pages import (
    CountriesPage as _CountriesPage, ErrorPage as _ErrorPage,
    LoginPage as _LoginPage, ProjectPage as _ProjectPage,
    ProjectsPage as _ProjectsPage, StructuresPage as _StructuresPage,
)

__all__ = ['MonProjetSGDFAPIBrowser']


class MonProjetSGDFAPIBrowser(_LoginBrowser):
    BASEURL = _environ.get(
        'MONPROJET_BASEURL',
        'https://monprojet.sgdf.fr',
    )

    login_page = _URL(
        r'/api/login',
        _LoginPage,
    )
    projects_page = _URL(
        r'/api/ddc-projets',
        _ProjectsPage,
    )
    project_page = _URL(
        r'/api/projets-annee/(?P<project_id>[0-9]+)',
        _ProjectPage,
    )
    structures_page = _URL(
        r'/api/structures',
        _StructuresPage,
    )
    countries_page = _URL(
        r'/api/tam-ref/pays',
        _CountriesPage,
    )

    def __init__(self, *args, **kwargs):
        super(MonProjetSGDFAPIBrowser, self).__init__(*args, **kwargs)

    def do_login(self):
        try:
            self.login_page.go(json={
                'numero': self.username,
                'password': self.password,
            })
        except _BrowserHTTPError as exc:
            error_page = _ErrorPage(self, exc.response)

            code = error_page.get_error_code()
            message = error_page.get_error_message()

            if code == 401:
                raise _BrowserIncorrectPassword(message)
            raise _BrowserUnavailable(f'[{code}] {message}')

        # TODO: error detection?
        # TODO: store userData since it is not accessible after login
        #       and stored in localStorage on the application.

        self.session.headers['Authorization'] = (
            f'Bearer {self.page.get_access_token()}'
        )

    @_need_login
    def iter_countries(self):
        self.countries_page.go()
        return self.page.iter_countries()

# End of file.

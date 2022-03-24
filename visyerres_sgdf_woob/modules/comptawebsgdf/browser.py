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
""" comptawebsgdf browser definition. """

from woob.browser.browsers import (
    LoginBrowser as _LoginBrowser, URL as _URL, need_login as _need_login,
)
from woob.exceptions import (
    BrowserIncorrectPassword as _BrowserIncorrectPassword,
)

from .pages import LoginPage as _LoginPage

__all__ = ['ComptaWebSGDFBrowser']


class ComptaWebSGDFBrowser(_LoginBrowser):
    BASEURL = 'https://comptaweb.sgdf.fr/'

    login_page = _URL(r'login', _LoginPage)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_login(self):
        self.login_page.go()
        self.page.do_login(self.username, self.password)

        if self.login_page.is_here():
            message = self.page.get_error_message()
            raise _BrowserIncorrectPassword(message)

        # TODO: what happens next?

    @_need_login
    def check_login(self):
        return  # TODO: not required other than for testing.

# End of file.

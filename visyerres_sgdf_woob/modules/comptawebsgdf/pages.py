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
"""comptawebsgdf pages definition."""

from woob.browser.filters.standard import CleanText as _CleanText
from woob.browser.pages import HTMLPage as _HTMLPage

__all__ = ['LoginPage']


class LoginPage(_HTMLPage):
    def do_login(self, username, password):
        form = self.get_form(name='login')
        form['_username'] = username
        form['_password'] = password
        form.submit()

    def get_error_message(self):
        message = _CleanText(
            '//div[contains(@class, "alert-danger")]',
            default='',
        )(self.doc)

        return message or None

# End of file.

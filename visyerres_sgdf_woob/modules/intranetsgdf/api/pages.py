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
"""intranetsgdf_api pages definition."""

from datetime import datetime as _datetime, timedelta as _timedelta

from woob.browser.elements import (
    ItemElement as _ItemElement, method as _method,
)
from woob.browser.filters.json import Dict as _Dict
from woob.browser.filters.standard import (
    CleanDecimal as _CleanDecimal, CleanText as _CleanText,
    Coalesce as _Coalesce,
)
from woob.browser.pages import JsonPage as _JsonPage
from woob.capabilities.base import BaseObject as _BaseObject

__all__ = ['TokenPage']


class TokenPage(_JsonPage):
    @_method
    class get_access_data(_ItemElement):
        klass = _BaseObject

        obj__access_token = _Coalesce(
            _CleanText(
                _Dict('access_token', default=''),
                default='',
            ),
            default=None,
        )

        obj__access_token_type = _Coalesce(
            _CleanText(
                _Dict('token_type', default=''),
                default='',
            ),
            default=None,
        )

        def obj__access_token_expires_at(self):
            seconds = _CleanDecimal.SI(
                _Dict('expires_in', default=''),
                default=None,
            )

            if not seconds:
                return None

            return _datetime.utcnow() + _timedelta(seconds=seconds)

        obj__refresh_token = _Coalesce(
            _CleanText(
                _Dict('refresh_token', default=''),
                default='',
            ),
            default=None,
        )

# End of file.

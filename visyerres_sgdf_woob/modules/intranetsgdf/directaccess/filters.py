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
""" Useful filters for the intranetsgdf woob module. """

from visyerres_sgdf_woob.utils import IID as _IID
from woob.browser.filters.base import Filter as _Filter, _NO_DEFAULT

__all__ = ['IIDLink']


class IIDLink(_Filter):
    """ Get an IID from a link.

        Extracts the IID and encodes it as an IID object.
    """

    def __init__(self, selector, arg: str = 'id', default=_NO_DEFAULT):
        super(IIDLink, self).__init__(selector, default=default)
        self.arg = arg

    def filter(self, data):  # noqa: A003
        if not data:
            return self.default_or_raise(ValueError(
                'expected an URL or HTML element',
            ))

        link = None
        raw = None

        if isinstance(data, (str, bytes)):
            raw = data
        else:
            link = data[0]

            if link.tag == 'td':
                al = link.xpath('./a')
                if al:
                    link = al[0]
                else:
                    al = link.xpath(
                        './input[(@type="radio" or @type="checkbox") '
                        'and (@value!="")]',
                    )
                    if al:
                        raw = al[0].attrib['value']

        if link is not None and raw is None:
            try:
                raw = link.attrib['href']
            except KeyError:
                raw = link.attrib['action']

        if raw is None:
            return self._default_or_raise(ValueError(
                f'expected a valid IID or IID link, got {data!r}',
            ))

        try:
            return _IID.fromurl(raw, self.arg)
        except (TypeError, ValueError) as exc:
            try:
                return _IID(raw)
            except Exception:
                return self._default_or_raise(exc)

# End of file.

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
"""Utilities for the Vis'Yerres SGDF Woob modules."""

from base64 import b64decode as _b64decode, b64encode as _b64encode
from urllib.parse import (
    parse_qs as _parse_qs, quote as _quote, unquote as _unquote,
    urlsplit as _urlsplit,
)

__all__ = ['IID']


class IID:
    """Identifier representing most resources on the intranet.

    Three formats are managed here:

    * A 16-byte sequence.
    * The equivalent base64-encoded, represented as 'bytes'.
    * The equivalent base64-encoded, represented as 'str'.
    """

    __slots__ = ('_val',)

    def __init__(self, value):
        if isinstance(value, IID):
            self._val = bytes(value)
            return

        if isinstance(value, str):
            value = _unquote(value)

            try:
                b = _b64decode(value)
            except Exception:
                raise ValueError(
                    'expected a valid base64 (eventually url encoded) '
                    f'iid, got {repr(value)}',
                )
        elif isinstance(value, bytes):
            if len(value) <= 16:
                # We have an IID directly, let's use it!
                b = value
            else:
                try:
                    # Maybe the source value is actually the URL-encoded
                    # version of the string, like above?
                    b = _b64decode(_unquote(value.decode('ASCII')))
                except Exception:
                    # Well that's not going to make it.
                    raise ValueError(
                        'expected a valid base64 (eventually url encoded) '
                        f'iid, got {value!r}',
                    )
        else:
            raise ValueError(f'unknown type for: {value!r}')

        if len(b) != 16:
            raise ValueError('result should be a 16-byte identifier')

        self._val = b

    def __str__(self):
        return _b64encode(self._val).decode('ASCII')

    def __repr__(self):
        return str(self)

    def __bytes__(self):
        return self._val

    def __hash__(self):
        return hash(self._val)

    def __eq__(self, other):
        if not isinstance(other, IID):
            return False

        return bytes(self) == bytes(other)

    def urlsafe(self):
        """Get a URL-safe version of the identifier."""

        return _quote(_b64encode(self._val))

    @classmethod
    def fromurl(cls, url: str, name: str = 'id'):
        """Get an IID out of an URL."""

        query_params = _parse_qs(_urlsplit(url).query)
        return cls(query_params.get(name, ('',))[0])


# End of file.

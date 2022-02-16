#!/usr/bin/env python
# *****************************************************************************
# Copyright (C) 2021-2022 Thomas Touhey <thomas@touhey.fr>
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
""" Errors defined by the application. """

from typing import Optional as _Optional

from woob.exceptions import (
    BrowserIncorrectPassword as _BrowserIncorrectPassword,
)

__all__ = [
    'IntranetError', 'IntranetInvalidPasswordError',
    'IntranetLoginError', 'IntranetUnauthorizedUserError',
    'IntranetUserNotFoundError',
]


class IntranetError(Exception):
    """ An error has occurred while following a procedure on the intranet. """

    pass


class IntranetLoginError(IntranetError, _BrowserIncorrectPassword):
    """ An error has occurred while logging in. """

    __slots__ = ('bad_fields',)

    def __init__(
        self,
        message: _Optional[str] = None,
        original_message: _Optional[str] = None,
        bad_fields=None,
    ):
        bad_fields = bad_fields or []
        message = message or original_message
        super().__init__(message)
        self.bad_fields = bad_fields


class IntranetUserNotFoundError(IntranetLoginError):
    """ The user was not found while trying to log in. """

    __slots__ = ('_login',)

    def __init__(self, login: _Optional[str] = None, *args, **kwargs):
        kwargs.setdefault('bad_fields', ['code'])
        super().__init__(
            'invalid user' + (f' {login!r}' if login is not None else ''),
            *args, **kwargs,
        )

        self._login = login

    @property
    def login(self):
        """ The login that was attempted. """

        return self._login


class IntranetInvalidPasswordError(IntranetLoginError):
    """ The password was found to be invalid while trying to log in. """

    __slots__ = ('_login', '_password')

    def __init__(
        self,
        login: _Optional[str] = None,
        password: _Optional[str] = None,
        *args, **kwargs,
    ):
        kwargs.setdefault('bad_fields', ['password'])
        super().__init__(
            'invalid password'
            + (f' for user {login!r}' if login is not None else '')
            + (f': {password!r}' if password is not None else ''),
            *args, **kwargs,
        )

        self._login = login
        self._password = password

    @property
    def login(self):
        """ The login that was attempted. """

        return self._login

    @property
    def password(self):
        """ The password that was attempted. """

        return self._password


class IntranetUnauthorizedUserError(IntranetLoginError):
    """ The user was found to be unauthorized to log in. """

    __slots__ = ('_login',)

    def __init__(self, login: _Optional[str] = None, *args, **kwargs):
        kwargs.setdefault('bad_fields', ['code'])
        super().__init__(
            'user' + (f' with identifier {login!r}' if login else '')
            + ' is not allowed to log in.',
        )

    @property
    def login(self):
        """ Get the login that was not allowed to log in. """

        return self._login


# End of file.

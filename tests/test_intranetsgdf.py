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
""" Test the backend based on what we know. """

from contextlib import contextmanager
import logging

import pytest
from visyerres_sgdf_woob import MODULES_PATH
from visyerres_sgdf_woob.mocker import RequestsMock
from visyerres_sgdf_woob.modules.intranetsgdf.direct.mock import (
    app as WSGIApp,
)
from woob.core.ouiboube import WebNip


@contextmanager
def get_woob():
    woob = WebNip(modules_path=MODULES_PATH)
    try:
        yield woob
    finally:
        woob.deinit()


class TestIntranetSGDF:
    @pytest.fixture(autouse=True)
    def set_log_level_to_debug(self, caplog):
        caplog.set_level(logging.DEBUG)

    @pytest.fixture(autouse=True)
    def intranet_mock(self):
        """ Mock the intranet using the mock WSGI application. """

        with RequestsMock() as responses:
            responses.add_wsgi('https://intranet.sgdf.fr', WSGIApp)

            yield

    @pytest.fixture
    def intranet(self):
        """ Intranet associated for a valid user with a valid password. """

        with get_woob() as woob:
            yield woob.build_backend('intranetsgdf', params={
                'code': '123456789',
                'password': 'validpass',
            })

    @pytest.fixture
    def intranet_invalid_password(self):
        """ Intranet associated for a valid user with an invalid password. """

        with get_woob() as woob:
            yield woob.build_backend('intranetsgdf', params={
                'code': '123456789',
                'password': 'wrongpass',
            })

    @pytest.fixture
    def intranet_unauthorized_user(self):
        """ Intranet associated with a forbidden user. """

        with get_woob() as woob:
            yield woob.build_backend('intranetsgdf', params={
                'code': '160000000',
                'password': 'testpass',
            })

    def test_intranet_login(self, intranet):
        intranet.check_login()

    def test_intranet_invalid_password_login(self, intranet_invalid_password):
        with pytest.raises(
            BrowserIncorrectPassword,
            match=r'invalid password',
        ):
            intranet_invalid_password.check_login()

    def test_intranet_unauthorized_user_login(
        self,
        intranet_unauthorized_user,
    ):
        with pytest.raises(
            BrowserIncorrectPassword,
            match=r'unauthorized',
        ):
            intranet_unauthorized_user.check_login()

# End of file.

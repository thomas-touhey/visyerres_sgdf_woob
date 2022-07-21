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
"""comptawebsgdf module definition."""

from woob.tools.value import ValueBackendPassword as _ValueBackendPassword

from visyerres_sgdf_woob.backend import Module as _Module

from .browser import ComptaWebSGDFBrowser as _ComptaWebSGDFBrowser

__all__ = ['ComptaWebSGDFModule']


class ComptaWebSGDFModule(_Module):
    NAME = 'comptawebsgdf'
    DESCRIPTION = 'ComptaWeb Scouts et Guides de France'
    MAINTAINER = 'Thomas Touhey'
    EMAIL = 'thomas@touhey.fr'
    LICENSE = 'Proprietary'

    BROWSER = _ComptaWebSGDFBrowser

    username = _ValueBackendPassword(
        label="Nom d'utilisateur",
        masked=False,
    )
    password = _ValueBackendPassword(
        label='Mot de passe',
        masked=True,
    )

    def create_default_browser(self):
        return self.create_browser(
            self.config['username'].get(),
            self.config['password'].get(),
            weboob=self.weboob,
        )

    def check_login(self):
        return self.direct_browser.check_login()

# End of file.

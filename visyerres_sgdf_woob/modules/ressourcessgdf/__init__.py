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
""" ressourcessgdf module definition.

    This module is used for interacting with ComptaWeb, accessible at
    https://comptaweb.sgdf.fr, the web application used by treasurers
    amongst the organization for matching transactions with bank account
    statements, and establishing budgets.
"""

from woob.tools.backend import (
    BackendConfig as _BackendConfig, Module as _Module,
)
from woob.tools.value import ValueBackendPassword as _ValueBackendPassword

from .directaccess import RessourcesSGDFBrowser as _RessourcesSGDFBrowser

__all__ = ['RessourcesSGDFModule']


class RessourcesSGDFModule(_Module):
    NAME = 'ressourcessgdf'
    DESCRIPTION = 'Ressources Scouts et Guides de France'
    MAINTAINER = 'Thomas Touhey'
    EMAIL = 'thomas@touhey.fr'
    LICENSE = 'Proprietary'
    VERSION = '3.0'

    BROWSER = _RessourcesSGDFBrowser
    CONFIG = _BackendConfig(
        _ValueBackendPassword(
            'username',
            label="Nom d'utilisateur",
            masked=False,
        ),
        _ValueBackendPassword(
            'password',
            label='Mot de passe',
            masked=True,
        ),
    )

    def create_default_browser(self):
        return self.create_browser(
            self.config['username'].get(),
            self.config['password'].get(),
            weboob=self.weboob,
        )

    def check_login(self):
        return self.browser.check_login()

# End of file.

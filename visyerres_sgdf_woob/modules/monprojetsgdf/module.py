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
""" monprojetsgdf module definition. """

from visyerres_sgdf_woob.backend import Module as _Module
from woob.tools.value import ValueBackendPassword as _ValueBackendPassword

from .browser import MonProjetSGDFBrowser as _MonProjetSGDFBrowser

__all__ = ['MonProjetSGDFModule']


class MonProjetSGDFModule(_Module):
    NAME = 'monprojetsgdf'
    DESCRIPTION = 'Mon Projet Scouts et Guides de France'
    MAINTAINER = 'Thomas Touhey'
    EMAIL = 'thomas@touhey.fr'
    LICENSE = 'Proprietary'

    BROWSER = _MonProjetSGDFBrowser

    code = _ValueBackendPassword(
        label="Numéro d'adhérent",
        regexp=r'[0-9]{9}',
        masked=False,
    )
    password = _ValueBackendPassword(
        label='Mot de passe',
        masked=True,
    )

    def create_default_browser(self):
        return self.create_browser(
            self.config['code'].get(),
            self.config['password'].get(),
            weboob=self.weboob,
        )

    def get_current_adherent(self):
        return self.browser.get_current_adherent()

    def iter_countries(self):
        return self.browser.iter_countries()

# End of file.

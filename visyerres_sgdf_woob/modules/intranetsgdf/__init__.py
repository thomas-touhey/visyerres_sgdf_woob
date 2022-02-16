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
""" intranetsgdf module definition.

    This module is used for interacting with the SGDF intranet, a derivative
    of the Intrassoc solution by Supralog edited and hosted by the same vendor.
    It is used by all associations to manage both the organization itself
    through defining people and related statuses, and provides a few
    ACM (Accueil Collectif de Mineurs) management tools such as an
    attendance registry, an event organizer, and insurance-related interfaces.

    Although the intranet used to manage camps and declarations, it has moved
    to monprojet for a few years now.
"""

from datetime import date as _date

from visyerres_sgdf_woob.capabilities import (
    BankAccount as _BankAccount, Person as _Person,
    Structure as _Structure,
)
from visyerres_sgdf_woob.utils import IID as _IID
from woob.tools.backend import (
    BackendConfig as _BackendConfig, Module as _Module,
)
from woob.tools.value import (
    ValueBackendPassword as _ValueBackendPassword,
    ValueBool as _ValueBool,
)

from .directaccess import IntranetSGDFBrowser as _IntranetSGDFBrowser

__all__ = ['IntranetSGDFModule']


class IntranetSGDFModule(_Module):
    NAME = 'intranetsgdf'
    DESCRIPTION = 'Intranet Scouts et Guides de France'
    MAINTAINER = 'Thomas Touhey'
    EMAIL = 'thomas@touhey.fr'
    LICENSE = 'Proprietary'
    VERSION = '3.0'

    BROWSER = _IntranetSGDFBrowser
    CONFIG = _BackendConfig(
        _ValueBackendPassword(
            'code',
            label="Numéro d'adhérent",
            regexp=r'[0-9]{9}',
            masked=False,
            required=False,
        ),
        _ValueBackendPassword(
            'password',
            label='Mot de passe',
            masked=True,
            required=False,
        ),
        _ValueBackendPassword(
            'api_client_id',
            label='Client ID',
            masked=True,
            required=False,
        ),
        _ValueBackendPassword(
            'api_client_secret',
            label='API client secret',
            masked=True,
            required=False,
        ),
        _ValueBackendPassword(
            'api_audience',
            label='Audience',
            masked=True,

            # Some kind of magic value found in the Java client.
            default='b27c656c0e534667b66404aace058215',
        ),
        _ValueBool(
            'interactive',
            default=True,
            transient=True,
        ),
    )

    def create_default_browser(self):
        return self.create_browser(
            self.config,
            weboob=self.weboob,
        )

    def request_code(
        self,
        last_name: str,
        first_name: str,
        birth_date: _date,
    ):
        return self.browser.request_code(
            last_name,
            first_name,
            birth_date,
        )

    def request_new_password(self, code: str):
        return self.browser.request_new_password(
            code,
        )

    def iter_people(self):
        return self.browser.iter_people()

    def iter_people_by_name(self, last_name: str, first_name: str):
        return self.browser.iter_people_by_name(last_name, first_name)

    def get_current_person_iid(self):
        return self.browser.get_person_iid()

    def get_current_person(self):
        iid = self.browser.get_person_iid()
        return self.browser.get_person(iid)

    def get_person(self, obj):
        if isinstance(obj, (_IID, str, bytes)):
            person = _Person()
            person.iid = obj

            obj = person

        return self.browser.get_person(person)

    def iter_delegations(self):
        return self.browser.iter_delegations()

    def iter_structures(self):
        return self.browser.iter_structures()

    def get_structure(self, obj):
        if isinstance(obj, (_IID, str, bytes)):
            structure = _Structure()
            structure.iid = obj

            obj = structure

        return self.browser.get_structure(obj)

    def get_structure_parent(self, obj):
        if isinstance(obj, (_IID, str, bytes)):
            structure = _Structure()
            structure.iid = obj

            obj = structure

        return self.browser.get_structure_parent(obj)

    def iter_structure_children(self, obj):
        if isinstance(obj, (_IID, str, bytes)):
            structure = _Structure()
            structure.iid = obj

            obj = structure

        return self.browser.iter_structure_children(obj)

    def iter_functions(self):
        return self.browser.iter_functions()

    def get_bank_account(self, obj):
        if isinstance(obj, (_IID, str, bytes)):
            account = _BankAccount()
            account.iid = obj

            obj = account

        return self.browser.get_bank_account(obj)

# End of file.

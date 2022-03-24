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
""" Module definition for intranetsgdf. """

from datetime import date as _date

from visyerres_sgdf_woob.backend import Module as _Module
from visyerres_sgdf_woob.capabilities import (
    BankAccount as _BankAccount, Person as _Person,
    Structure as _Structure,
)
from visyerres_sgdf_woob.utils import IID as _IID
from woob.tools.value import (
    Value as _Value, ValueBackendPassword as _ValueBackendPassword,
    ValueBool as _ValueBool,
)

from .api import IntranetSGDFAPIBrowser as _IntranetSGDFAPIBrowser
from .direct import IntranetSGDFBrowser as _IntranetSGDFBrowser

__all__ = ['IntranetSGDFModule']


class IntranetSGDFModule(_Module):
    NAME = 'intranetsgdf'
    DESCRIPTION = 'Intranet Scouts et Guides de France'
    MAINTAINER = 'Thomas Touhey'
    EMAIL = 'thomas@touhey.fr'
    LICENSE = 'Proprietary'

    code = _ValueBackendPassword(
        label="Numéro d'adhérent",
        regexp=r'[0-9]{9}',
        masked=False,
        required=False,
    )
    password = _ValueBackendPassword(
        label='Mot de passe',
        masked=True,
        required=False,
    )
    api_client_id = _ValueBackendPassword(
        label='Client ID',
        masked=True,
        required=False,
    )
    api_client_secret = _ValueBackendPassword(
        label='API client secret',
        masked=True,
        required=False,
    )
    interactive = _ValueBool(
        default=True,
        transient=True,
    )
    environment = _Value(
        label='Environnement technique',
        choices={
            'live': 'Production',
            'test': 'Recette',
        },
        default='live',
        required=False,
    )

    @property
    def direct_browser(self):
        self._direct_browser = self.create_browser(
            self.config,
            klass=_IntranetSGDFBrowser,
        )

        if hasattr(self._direct_browser, 'load_state'):
            self._direct_browser.load_state(self.storage.get(
                'direct_browser_state',
                default={},
            ))

        return self._direct_browser

    @property
    def api_browser(self):
        if not self.config['api_client_id'].get():
            return

        if not self._api_browser:
            self._api_browser = self.create_browser(
                self.config,
                klass=_IntranetSGDFAPIBrowser,
            )

            if hasattr(self._api_browser, 'load_state'):
                self.api_browser.load_state(self.storage.get(
                    'api_browser_state',
                    default={},
                ))

        return self._api_browser

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._direct_browser = None
        self._api_browser = None

    def dump_state(self):
        should_save = False

        if self._direct_browser and hasattr(self.direct_browser, 'dump_state'):
            self.storage.set(
                'direct_browser_state',
                self.direct_browser.dump_state(),
            )
            should_save = True

        if self._api_browser and hasattr(self.api_browser, 'dump_state'):
            self.storage.set(
                'api_browser_state',
                self.api_browser.dump_state(),
            )
            should_save = True

        if should_save:
            self.storage.save()

    def check_login(self):
        self.direct_browser.check_login()

    def request_code(
        self,
        last_name: str,
        first_name: str,
        birth_date: _date,
    ):
        return self.direct_browser.request_code(
            last_name,
            first_name,
            birth_date,
        )

    def request_new_password(self, code: str):
        return self.direct_browser.request_new_password(
            code,
        )

    def iter_people(self):
        return self.direct_browser.iter_people()

    def iter_people_by_name(self, last_name: str, first_name: str):
        return self.direct_browser.iter_people_by_name(last_name, first_name)

    def get_current_person_iid(self):
        return self.direct_browser.get_person_iid()

    def get_current_person(self):
        iid = self.direct_browser.get_person_iid()
        return self.get_person(iid)

    def get_person(self, obj):
        if isinstance(obj, (_IID, str, bytes)):
            person = _Person()
            person.iid = _IID(obj)

            obj = person

        return self.direct_browser.get_person(person)

    def iter_delegations(self):
        return self.direct_browser.iter_delegations()

    def iter_structures(self):
        return self.direct_browser.iter_structures()

    def get_structure(self, obj):
        if isinstance(obj, (_IID, str, bytes)):
            structure = _Structure()
            structure.iid = _IID(obj)

            obj = structure

        return self.direct_browser.get_structure(obj)

    def get_structure_parent(self, obj):
        if isinstance(obj, (_IID, str, bytes)):
            structure = _Structure()
            structure.iid = _IID(obj)

            obj = structure

        return self.direct_browser.get_structure_parent(obj)

    def iter_structure_children(self, obj):
        if isinstance(obj, (_IID, str, bytes)):
            structure = _Structure()
            structure.iid = _IID(obj)

            obj = structure

        return self.direct_browser.iter_structure_children(obj)

    def iter_functions(self):
        return self.browser.iter_functions()

    def get_bank_account(self, obj):
        if isinstance(obj, (_IID, str, bytes)):
            account = _BankAccount()
            account.iid = _IID(obj)

            obj = account

        return self.direct_browser.get_bank_account(obj)

# End of file.

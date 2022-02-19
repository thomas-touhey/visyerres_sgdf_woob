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
""" intranetsgdf directaccess browser definition.

    This module is used for interacting with the SGDF intranet directly,
    which is still useful for functions either not supported by the API,
    or when the API is not accessible by the client.
"""

from datetime import date as _date
from os import environ as _environ

from urllib.parse import urlparse as _urlparse
from visyerres_sgdf_woob.capabilities import (
    BankAccount as _BankAccount, Person as _Person, Structure as _Structure,
)
from visyerres_sgdf_woob.errors import (
    IntranetInvalidPasswordError as _IntranetInvalidPasswordError,
    IntranetLoginError as _IntranetLoginError,
    IntranetUnauthorizedUserError as _IntranetUnauthorizedUserError,
    IntranetUserNotFoundError as _IntranetUserNotFoundError,
)
from woob.browser.browsers import (
    LoginBrowser as _LoginBrowser, URL as _URL,
    need_login as _need_login,
)
from woob.capabilities.base import empty as _empty
from woob.exceptions import (
    BrowserForbidden as _BrowserForbidden,
    BrowserHTTPNotFound as _BrowserHTTPNotFound,
    BrowserIncorrectPassword as _BrowserIncorrectPassword,
    BrowserUnavailable as _BrowserUnavailable,
)

from .pages import (
    AdherentEditPage as _AdherentEditPage,
    AdherentInscriptionSearchPage as _AdherentInscriptionSearchPage,
    AdherentPage as _AdherentPage, AdherentSearchPage as _AdherentSearchPage,
    AdherentStructureListPage as _AdherentStructureListPage,
    BankAccountPage as _BankAccountPage, CampPage as _CampPage,
    FunctionsCompletionPage as _FunctionsCompletionPage,
    FunctionsPage as _FunctionsPage, HomePage as _HomePage,
    InsuredGoodCreatePage as _InsuredGoodCreatePage,
    InsuredGoodEditPage as _InsuredGoodEditPage,
    InsuredGoodPage as _InsuredGoodPage,
    InsuredGoodSearchPage as _InsuredGoodSearchPage,
    InsuredVehiclePage as _InsuredVehiclePage,
    InsuredVehicleSearchPage as _InsuredVehicleSearchPage,
    LoggedPage as _LoggedPage, LoginPage as _LoginPage,
    PersonEditPage as _PersonEditPage, PersonPage as _PersonPage,
    PersonSearchPage as _PersonSearchPage, PlacePage as _PlacePage,
    SecondaryFunctionsPage as _SecondaryFunctionsPage,
    StructureBankAccountsPage as _StructureBankAccountsPage,
    StructureCompletionPage as _StructureCompletionPage,
    StructureContactsPage as _StructureContactsPage,
    StructureDelegationsPage as _StructureDelegationsPage,
    StructureEventsPage as _StructureEventsPage,
    StructureHierarchyPage as _StructureHierarchyPage,
    StructureMarkersPage as _StructureMarkersPage,
    StructureSearchPage as _StructureSearchPage,
    StructureSpecialitiesPage as _StructureSpecialitiesPage,
    StructureSummaryPage as _StructureSummaryPage,
    TeamSearchPage as _TeamSearchPage,
    WebServiceErrorPage as _WebServiceErrorPage,
)

__all__ = ['IntranetSGDFBrowser']


class IntranetSGDFBrowser(_LoginBrowser):
    BASEURL = _environ.get(
        'INTRANET_BASEURL',
        'https://intranet.sgdf.fr',
    )
    TIMEOUT = 30.0

    login_page = _URL(
        r'/Specialisation/Sgdf/Default.aspx',
        r'/Default.aspx',
        _LoginPage,
    )
    home_page = _URL(
        r'/Specialisation/Sgdf/Accueil.aspx',
        r'/Accueil.aspx',
        _HomePage,
    )
    adherent_page = _URL(
        r'/Specialisation/Sgdf/adherents/ResumeAdherent.aspx',
        r'/adherents/ResumeAdherent.aspx',
        _AdherentPage,
    )
    adherent_edit_page = _URL(
        r'/Specialisation/Sgdf/adherents/ModifierAdherent.aspx',
        r'/adherents/ModifierAdherent.aspx',
        _AdherentEditPage,
    )
    adherent_inscription_search_page = _URL(
        r'/Specialisation/Sgdf/adherents/InscriptionSaisieNom.aspx',
        r'/adherents/InscriptionSaisieNom.aspx',
        _AdherentInscriptionSearchPage,
    )
    adherent_search_page = _URL(
        r'/Specialisation/Sgdf/adherents/RechercherAdherent.aspx',
        r'/adherents/RechercherAdherent.aspx',
        _AdherentSearchPage,
    )
    adherent_structure_list_page = _URL(
        r'/Specialisation/Sgdf/adherents/ListeAdherents.aspx',
        r'/adherents/ListeAdherents.aspx',
        _AdherentStructureListPage,
    )
    person_search_page = _URL(
        r'/Specialisation/Sgdf/adherents/RechercherPersonne.aspx',
        r'/adherents/RechercherPersonne.aspx',
        _PersonSearchPage,
    )
    person_page = _URL(
        r'/Specialisation/Sgdf/adherents/ResumePersonne.aspx',
        r'/adherents/ResumePersonne.aspx',
        _PersonPage,
    )
    person_edit_page = _URL(
        r'/Specialisation/Sgdf/adherents/ModifierPersonne.aspx',
        r'/adherents/ModifierPersonne.aspx',
        _PersonEditPage,
    )
    secondary_functions_page = _URL(
        r'/Specialisation/Sgdf/nominations/ListeDelegations.aspx',
        r'/nominations/ListeDelegations.aspx',
        _SecondaryFunctionsPage,
    )
    structure_hierarchy_page = _URL(
        r'/Specialisation/Sgdf/structures/ResumeStructure.aspx',
        r'/structures/ResumeStructure.aspx',
        _StructureHierarchyPage,
    )
    structure_summary_page = _URL(
        r'/Specialisation/Sgdf/structures/ResumeStructure.aspx',
        r'/structures/ResumeStructure.aspx',
        _StructureSummaryPage,
    )
    structure_specialities_page = _URL(
        r'/Specialisation/Sgdf/structures/ResumeStructure.aspx',
        r'/structures/ResumeStructure.aspx',
        _StructureSpecialitiesPage,
    )
    structure_delegations_page = _URL(
        r'/Specialisation/Sgdf/structures/ResumeStructure.aspx',
        r'/structures/ResumeStructure.aspx',
        _StructureDelegationsPage,
    )
    structure_contacts_page = _URL(
        r'/Specialisation/Sgdf/structures/ResumeStructure.aspx',
        r'/structures/ResumeStructure.aspx',
        _StructureContactsPage,
    )
    structure_bank_accounts_page = _URL(
        r'/Specialisation/Sgdf/structures/ResumeStructure.aspx',
        r'/structures/ResumeStructure.aspx',
        _StructureBankAccountsPage,
    )
    structure_markers_page = _URL(
        r'/Specialisation/Sgdf/structures/ResumeStructure.aspx',
        r'/structures/ResumeStructure.aspx',
        _StructureMarkersPage,
    )
    structure_events_page = _URL(
        r'/Specialisation/Sgdf/structures/ResumeStructure.aspx',
        r'/structures/ResumeStructure.aspx',
        _StructureEventsPage,
    )
    structure_search_page = _URL(
        r'/Specialisation/Sgdf/Popups/RechercheStructure.aspx',
        r'/Popups/RechercheStructure.aspx',
        _StructureSearchPage,
    )
    structure_completion_page = _URL(
        r'/Specialisation/Sgdf/WebServices/AutoComplete.asmx/GetStructures',
        r'/WebServices/AutoComplete.asmx/GetStructures',
        _StructureCompletionPage,
    )
    functions_page = _URL(
        r'/Specialisation/Sgdf/popups/RechercheFonction.aspx',
        r'/popups/RechercheFonction.aspx',
        _FunctionsPage,
    )
    functions_completion_page = _URL(
        r'/Specialisation/Sgdf/WebServices/AutoComplete.asmx/GetFonctions',
        r'/WebServices/AutoComplete.asmx/GetFonctions',
        _FunctionsCompletionPage,
    )
    team_search_page = _URL(
        (
            r'/Specialisation/Sgdf'
            r'/Formations/RechercherEquipeActionFormation.aspx'
        ),
        r'/Formations/RechercherEquipeActionFormation.aspx',
        _TeamSearchPage,
    )
    bank_account_page = _URL(
        r'/Specialisation/Sgdf/ComptesBancaires/ResumeCompteBancaire.aspx',
        r'/ComptesBancaires/ResumeCompteBancaire.aspx',
        _BankAccountPage,
    )
    insured_good_search_page = _URL(
        r'/Specialisation/Sgdf/BiensLocauxAssurances/RechercherBien.aspx',
        r'/BiensLocauxAssurances/RechercherBien.aspx',
        _InsuredGoodSearchPage,
    )
    insured_good_page = _URL(
        r'/Specialisation/Sgdf/BiensLocauxAssurances/ResumeBien.aspx',
        r'/BiensLocauxAssurances/ResumeBien.aspx',
        _InsuredGoodPage,
    )
    insured_good_edit_page = _URL(
        r'/Specialisation/Sgdf/BiensLocauxAssurances/ModifLocal.aspx',
        r'/BiensLocauxAssurances/ModifLocal.aspx',
        _InsuredGoodEditPage,
    )
    insured_good_create_page = _URL(
        r'/Specialisation/Sgdf/BiensLocauxAssurances/CreerLocal.aspx',
        r'/BiensLocauxAssurances/CreerLocal.aspx',
        _InsuredGoodCreatePage,
    )
    insured_vehicle_search_page = _URL(
        r'/Specialisation/Sgdf/BiensLocauxAssurances/RechercheVehicule.aspx',
        r'/BiensLocauxAssurances/RechercheVehicule.aspx',
        _InsuredVehicleSearchPage,
    )
    insured_vehicle_page = _URL(
        r'/Specialisation/Sgdf/BiensLocauxAssurances/CreerVehicule.aspx',
        r'/BiensLocauxAssurances/CreerVehicule.aspx',
        _InsuredVehiclePage,
    )
    camp_page = _URL(
        r'/Specialisation/Sgdf/camps/ConsulterModifierCamp.aspx',
        r'/camps/ConsulterModifierCamp.aspx',
        _CampPage,
    )
    place_page = _URL(
        r'/Specialisation/Sgdf/Commun/ResumeLieuActivite.aspx',
        r'/Commun/ResumeLieuActivite.aspx',
        _PlacePage,
    )

    def __init__(self, config, *args, **kwargs):
        super(IntranetSGDFBrowser, self).__init__(
            config['code'].get(),
            config['password'].get(),
            *args,
            **kwargs,
        )

        self.is_interactive = config['interactive'].get()
        self.session.hooks['response'].append(self.check_for_error_redirects)

    def raise_for_status(self, response):
        content_type = response.headers.get('Content-Type')
        if (
            400 <= response.status_code < 600
            and content_type.startswith('application/json')
        ):
            page = _WebServiceErrorPage(self, response)
            raise _BrowserUnavailable(page.get_error_message())

    def check_for_error_redirects(self, response, *args, **kwargs):
        if 300 <= response.status_code < 400:
            location = response.headers.get('Location')
            if location:
                path = _urlparse(location).path.casefold()

                # We want to avoid getting to the pages to yield
                # the errors they contain, which is always the same.

                if path.endswith('/erreurs/erreur.aspx'):
                    raise _BrowserUnavailable(
                        'Oups ! Une erreur est survenue.',
                    )
                elif path.endswith('/erreurs/404.aspx'):
                    raise _BrowserHTTPNotFound(
                        'Cette page est introuvable.',
                    )
                elif path.endswith('/erreurs/interdit.aspx'):
                    raise _BrowserForbidden(
                        "Vous n'avez pas les droits nécessaires pour "
                        'accéder à cette page.',
                    )

    def do_login(self):
        if not self.username or not self.password:
            raise _BrowserIncorrectPassword()

        self.login_page.go()
        self.page.do_login(self.username, self.password)

        if not self.login_page.is_here():
            return

        error = self.page.get_error_message()
        if not error:
            # No error message and no redirection? It seems that the
            # server has completely ignored us.

            raise _BrowserUnavailable()
        elif 'dentifiant invalide' in error:
            raise _IntranetUserNotFoundError(
                self.username,
                original_message=error,
            )
        elif 'passe invalide' in error:
            raise _IntranetInvalidPasswordError(
                self.username,
                self.password,
                original_message=error,
            )
        elif 'pas le droit' in error:
            raise _IntranetUnauthorizedUserError(
                self.username,
                original_message=error,
            )

        raise _IntranetLoginError(original_message=error)

    @_need_login
    def check_login(self):
        pass

    def request_code(
        self,
        last_name: str,
        first_name: str,
        birth_date: _date,
    ):
        self.login_page.go()
        self.page.request_code(last_name, first_name, birth_date)

        if not self.login_page.is_here():
            return

        error = self.page.get_error_message()
        if not error:
            return

        if 'as de r' in error:  # "Pas de résultat"
            raise _IntranetUserNotFoundError(original_message=error)

        raise _IntranetLoginError(original_message=error)

    def request_new_password(self, code: str):
        self.login_page.go()
        self.page.request_new_password(code)

        if not self.login_page.is_here():
            return

        error = self.page.get_error_message()
        if not error:
            return

        if 'invalide' in error:
            raise _IntranetUserNotFoundError(code, original_message=error)
        elif 'pas le droit' in error:
            raise _IntranetUnauthorizedUserError(code, original_message=error)

        raise _IntranetLoginError(original_message=error)

    @_need_login
    def get_person_iid(self):
        if not isinstance(self.page, _LoggedPage):
            self.home_page.go()

        return self.page.get_person_iid()

    @_need_login
    def get_structure_id(self):
        if not isinstance(self.page, _LoggedPage):
            self.home_page.go()

        return self.page.get_structure_id()

    @_need_login
    def iter_people(self):
        self.adherent_search_page.go()

        # TODO: alternate method to explore more in depth?
        # self.person_search_page.go()

        self.page.search_people()
        return self.page.iter_people()

    @_need_login
    def iter_people_by_name(self, last_name: str, first_name: str):
        self.adherent_inscription_search_page.go()
        self.page.search_people(
            last_name=last_name,
            first_name=first_name,
        )

        return self.page.iter_people()

    @_need_login
    def get_person(self, obj: _Person):
        if _empty(obj.iid):
            raise NotImplementedError

        self.adherent_page.go(params={
            'id': obj.iid.urlsafe(),
        })

        self.page.get_person(obj=obj)

        try:
            self.adherent_edit_page.go(params={
                'id': obj.iid.urlsafe(),
            })
        except _BrowserForbidden:
            pass
        else:
            if not self.home_page.is_here():  # no permissions error probably?
                self.page.get_person(obj=obj)

        return obj

    @_need_login
    def iter_delegations(self):
        # TODO: only secondary delegations here for now.

        self.secondary_functions_page.go()
        self.page.search_delegations()
        return self.page.iter_delegations()

    @_need_login
    def get_structure(self, obj: _Structure):
        if _empty(obj.iid):
            raise NotImplementedError

        self.structure_summary_page.go(params={
            'id': obj.iid.urlsafe(),
        })
        self.page.go_to_summary()
        self.page.get_structure(obj=obj)

        return obj

    @_need_login
    def iter_structures(self):
        self.structure_search_page.go(params={
            'dummy': '1',
            'single': '1',
            'tag': '_tag__btnPopupStructure',
            'operations': 'eAnHPUF82qOeC0kR9XOtQA==',  # rechercher compétences
            'statut': '-1',
        })

        self.page.search_structures()
        return self.page.iter_structures()

    @_need_login
    def get_structure_parent(self, obj: _Structure):
        if not _empty(obj.iid):
            # Let's abuse completion for the team search page.

            try:
                self.team_search_page.go(params={
                    'id': obj.iid.urlsafe(),
                })
            except _BrowserUnavailable:
                # When given an invalid IID, the page produces an error.
                # So we just think it's not found.

                raise _BrowserHTTPNotFound()

            self.page.get_structure(obj)
        elif not _empty(obj.id):
            self.team_search_page.go()
            self.page.go_to_structure(obj.id)
        else:
            raise NotImplementedError

        self.page.go_to_parent()
        return self.page.get_structure()

    @_need_login
    def iter_structure_children(self, obj):
        if not _empty(obj.id):
            # We don't actually need to go to the specific page of the
            # structure, and do not need the IID.
            #
            # However, we still need to go to the page before making the
            # autocomplete call since, otherwise, it returns an empty result.

            self.team_search_page.go()
        else:
            try:
                self.team_search_page.stay_or_go(params={
                    'id': obj.iid.urlsafe(),
                })
            except _BrowserUnavailable:
                # When given an invalid IID, the page produces an error.
                # So we just think it's not found.

                raise _BrowserHTTPNotFound()

            self.page.get_structure(obj)

        self.structure_completion_page.go(json={
            'q': '',
            'id_token': f'{obj.id}',
        })

        return self.page.iter_structure_children()

    @_need_login
    def iter_functions(self):
        # Two alternatives here:
        #
        # * Use the AutoComplete.asmx page dedicated to functions.
        # * Use the function search page in the context of searching functions
        #   to limit for a given event, using tag 'fonctionsConcernees' and
        #   operations 'HqJsfKPr7cfJtLYCZJPd2w=='.
        #
        # We chose the second one since the first one doesn't yield
        # additional data, only identifiers (which we don't have but don't
        # actually need for most actions) and labels.

        self.functions_page.go(params={
            'dummy': '1',
            'tag': 'fonctionsConcernees',
            'fonctionsConcernees': 'HqJsfKPr7cfJtLYCZJPd2w==',
        })

        self.page.search_functions()
        return self.page.iter_functions()

    @_need_login
    def get_bank_account(self, obj: _BankAccount):
        if _empty(obj.iid):
            raise NotImplementedError

        self.bank_account_page.go(params={
            'id': obj.iid.urlsafe(),
        })

        return self.page.get_bank_account(obj=obj)

# End of file.

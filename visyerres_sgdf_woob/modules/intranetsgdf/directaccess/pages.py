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
""" intranetsgdf pages definition. """

import re as _re

from datetime import date as _date

from visyerres_sgdf_woob.capabilities import (
    Address as _Address, BankAccount as _BankAccount,
    BirthPlace as _BirthPlace, Country as _Country, Delegation as _Delegation,
    Function as _Function, Person as _Person, Structure as _Structure,
)
from visyerres_sgdf_woob.mshtml import MSHTMLPage as _MSHTMLPage
from woob.browser.elements import (
    DictElement as _DictElement, ItemElement as _ItemElement,
    TableElement as _TableElement, method as _method,
)
from woob.browser.filters.html import (
    Attr as _Attr, FormValue as _FormValue, TableCell as _TableCell,
    XPath as _XPath,
)
from woob.browser.filters.json import Dict as _Dict
from woob.browser.filters.standard import (
    CleanDecimal as _CleanDecimal, CleanText as _CleanText,
    Coalesce as _Coalesce, Date as _Date, Field as _Field,
    Format as _Format, Regexp as _Regexp,
)
from woob.browser.pages import (
    JsonPage as _JsonPage, LoggedPage as _LoggedPage,
    pagination as _pagination,
)
from woob.capabilities.base import (
    NotAvailable as _NotAvailable, empty as _empty,
)

from .elements import PaginatedTableElement as _PaginatedTableElement
from .filters import IIDLink as _IIDLink

__all__ = [
    'AdherentEditPage', 'AdherentPage', 'HomePage', 'LoggedPage',
    'LoginPage', 'StructurePage',
]


class _JsonDataPage(_JsonPage):
    def build_doc(self, text):
        doc = super(_JsonDataPage, self).build_doc(text)

        if (
            isinstance(doc, dict)
            and tuple(doc.keys()) == ('d',)
            and isinstance(doc['d'], str)
        ):
            doc = super(_JsonDataPage, self).build_doc(doc['d'])

        return doc


class WebServiceErrorPage(_JsonPage):
    def get_error_message(self):
        return _CleanText(_Dict('Message', default=''))(self.doc)


class LoginPage(_MSHTMLPage):
    def do_login(self, username, password):
        self['login'] = username
        self['password'] = password

        self.submit(
            target='_btnValider',
            button_id='_btnValider',
        )

    def request_new_password(self, username: str):
        """ Request a new password for the given username. """

        self['_tbIdentifiant'] = username
        self.submit(target='Envoyer', button_id='Envoyer')

    def request_code(
        self,
        last_name: str,
        first_name: str,
        birth_date: _date,
    ):
        """ Request our adherent code by e-mail. """

        self['_tbNom'] = last_name
        self['_tbPrenom'] = first_name
        self['_dpbDateNaissance$_tbDate'] = birth_date.strftime('%d/%m/%Y')
        self.submit(
            target='EnvoyerNumeroAdherent',
            button_id='EnvoyerNumeroAdherent',
        )

    def get_error_message(self):
        return _CleanText(
            '//span[ends-with(@id, "_lblErreur")]',
            default=None,
        )(self)


class LoggedPage(_MSHTMLPage, _LoggedPage):
    def build_doc(self, content):
        doc = super(LoggedPage, self).build_doc(content)

        # We delete the suggestion modal, which seems to
        # parasitate some form submissions.

        modal = doc.xpath('//div[@id="modalSuggestionAvisUtilisateur"]')
        if modal:
            modal = modal[0]
            modal.getparent().remove(modal)

        return doc

    def get_person_iid(self):
        return _IIDLink(
            '//a[@id="ctl00__hlVoirFicherAdherentLogo"]',
        )(self)

    def get_structure_id(self):
        return _IIDLink(
            '//a[@id="ctl00__hlVoirFicheStructureLogo"]',
        )(self)


class HomePage(LoggedPage):
    pass


# ---
# Adherent-related pages.
# ---


class AdherentPage(LoggedPage):
    @_method
    class get_delegation(_ItemElement):
        klass = _Delegation

        obj_is_primary = True

        class obj_structure(_ItemElement):
            klass = _Structure

            def validate(self, obj):
                return not _empty(obj.code)

            obj_iid = _IIDLink(
                '//a[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume__hlStructure"]',
            )
            obj_label = _Structure.Label(
                '//a[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume__hlStructure"]',
                default='',
            )

        class obj_function(_ItemElement):
            klass = _Function

            def validate(self, obj):
                return not _empty(obj.code)

            obj_label = _Function.Label(
                '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume__lblFonction"]',
                default='',
            )

    @_method
    class get_person(_ItemElement):
        klass = _Person

        obj_iid = _IIDLink('//form[@id="aspnetForm"]')
        obj_type_ = _Person.TYPE_INDIVIDUAL
        obj_full_name = _Person.FullName(
            '//span[@id="ctl00_ctl00__divTitre"]',
        )

        obj_code = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume__resume__lblCodeAdherent"]',
            default=None,
        )

        def obj_delegations(self):
            # TODO: secondary delegations

            return [self.page.get_delegation()]

        def obj_status(self):
            status_name = _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume_'
                '_lblTypeInscription"]',
                default=_NotAvailable,
            )(self)

            if _empty(status_name):
                return status_name

            status_name = status_name.casefold()

            if 'pr' in status_name and 'inscrit' in status_name:
                return _Person.STATUS_PREINSCRIT
            elif 'inscrit' in status_name:
                return _Person.STATUS_INSCRIT
            elif 'adh' in status_name:
                return _Person.STATUS_ADHERENT
            elif 'inv' in status_name:
                return _Person.STATUS_INVITE
            elif 'quitt' in status_name:
                return _Person.STATUS_A_QUITTE_L_ASSOCIATION
            elif 'ced' in status_name:
                return _Person.STATUS_DECEDE

            return _Person.STATUS_UNKNOWN

        obj_duplicate_of_id = _IIDLink(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume_'
            '_resume__hlPersonneDoublonDe"]',
            default=None,
        )

        obj_function_start = _Date(
            _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume_'
                '_lblDebutFonction"]',
                default='',
            ),
            dayfirst=True,
            default=_NotAvailable,
        )
        obj_function_end = _Date(
            _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume_'
                '_lblFinFonction"]',
                default='',
            ),
            dayfirst=True,
            default=_NotAvailable,
        )

        obj_birth_name = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume__resume__modeleIndividu_'
            '_lblNomJeuneFille2"]',
        )

        class obj_address(_ItemElement):
            klass = _Address

            obj_line_1 = _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume_'
                '_modeleIndividu__resumeAdresse__lbLigne1"]',
                default='',
            )
            obj_line_2 = _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume_'
                '_modeleIndividu__resumeAdresse__lbLigne2"]',
                default='',
            )
            obj_line_3 = _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume_'
                '_modeleIndividu__resumeAdresse__lbLigne3"]',
                default='',
            )
            obj_postal_code = _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume_'
                '_modeleIndividu__resumeAdresse__lbCodePostal"]',
                default='',
            )
            obj_municipality_name = _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume_'
                '_modeleIndividu__resumeAdresse__lbVille"]',
                default='',
            )

            class obj_country(_ItemElement):
                klass = _Country

                obj_name = _CleanText(
                    '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
                    'TabContainerResumeAdherent__tabResume__resume_'
                    '_modeleIndividu__resumeAdresse__lbPays"]',
                    default='',
                )

        def obj_npai(self):
            result = _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume_'
                '_resume__modeleIndividu__lblNpai"]',
                default=_NotAvailable,
            )(self)

            if _empty(result):
                return result

            return result.casefold() == 'oui'

        obj_home_phone = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume__resume_'
            '_modeleIndividu__lblTelephoneDomicile"]',
        )
        obj_work_phone = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume__resume_'
            '_modeleIndividu__lblTelephoneBureau"]',
        )
        obj_mobile_phone = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume__resume_'
            '_modeleIndividu__lblTelephonePortable1"]',
        )
        obj_mobile_phone_2 = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume__resume_'
            '_modeleIndividu__lblTelephonePortable2"]',
        )
        obj_personal_email = _CleanText(
            '//a[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume__resume_'
            '_modeleIndividu__hlCourrielPersonnel"]',
        )
        obj_dedicated_email = _CleanText(
            '//a[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume__resume_'
            '_modeleIndividu__hlCourrielProfessionnel"]',
        )

        obj_birth_date = _Date(
            _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume_'
                '_modeleIndividu__lblDateNaissance"]',
                default='',
            ),
            dayfirst=True,
            default=_NotAvailable,
        )

        class obj_birth_place(_ItemElement):
            klass = _BirthPlace

            obj_postal_code = _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume_'
                '_modeleIndividu__lbCPNaissance"]',
                default='',
            )
            obj_municipality_name = _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume_'
                '_modeleIndividu__lbCommuneNaissance"]',
                default='',
            )
            obj_insee_code = _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume_'
                '_modeleIndividu__lbCodeInsee"]',
                default='',
            )

        obj_occupation = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume__resume_'
            '_modeleIndividu__lblProfession"]',
            default='',
        )
        obj_allocations_code = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume__resume_'
            '_modeleIndividu__lblNumeroAllocataire"]',
            default='',
        )

        def obj_allocations_regime(self):
            checked_general = _FormValue(
                '//input[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume_'
                '_modeleIndividu__cbRegimeGeneral"]',
                default=False,
            )(self)

            checked_msa = _FormValue(
                '//input[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume_'
                '_modeleIndividu__cbRegimeMSA"]',
                default=False,
            )(self)

            checked_other = _FormValue(
                '//input[@id="ctl00_ctl00_MainContent_TabsContent_'
                'TabContainerResumeAdherent__tabResume__resume_'
                '_modeleIndividu__cbRegimeEtranger"]',
                default=False,
            )(self)

            if checked_general:
                return _Person.ALLOCATIONSREGIME_GENERAL
            elif checked_msa:
                return _Person.ALLOCATIONSREGIME_MSA
            elif checked_other:
                return _Person.ALLOCATIONSREGIME_OTHER

            return _Person.ALLOCATIONSREGIME_UNKNOWN

        obj_medical_intervention_rights = _FormValue(
            '//input[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume__resume_'
            '_cbAutorisationInterventionChirurgicale"]',
            default=False,
        )
        obj_image_rights = _FormValue(
            '//input[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume__resume_'
            '_cbAutorisationImage"]',
            default=False,
        )
        obj_information_rights = _FormValue(
            '//input[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume__resume_'
            '_cbAutorisationInformations"]',
            default=False,
        )
        obj_insured = _FormValue(
            '//input[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume__resume__cbAssuranceRc"]',
            default=False,
        )

        obj_ice_last_name = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume__resume__lblNomUrgence"]',
        )
        obj_ice_first_name = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume__resume_'
            '_lblPrenomUrgence"]',
        )
        obj_ice_phone = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeAdherent__tabResume__resume_'
            '_lblTelephoneUrgence"]',
        )


class AdherentEditPage(LoggedPage):
    @_method
    class get_delegation(_ItemElement):
        klass = _Delegation

        class obj_structure(_ItemElement):
            klass = _Structure

            def validate(self, obj):
                return not _empty(obj.code)

            obj_label = _Structure.Label(_FormValue(
                '//select[@id="ctl00_MainContent__editAdherent_'
                '_selecteurStructure__ddStructure"]',
                default='',
            ))

        class obj_function(_ItemElement):
            klass = _Function

            def validate(self, obj):
                return not _empty(obj.code)

            obj_label = _Function.Label(_FormValue(
                '//select[@id="ctl00_MainContent__editAdherent__ddFonction"]',
                default='',
            ))

    @_method
    class get_person(_ItemElement):
        klass = _Person

        obj_type_ = _Person.TYPE_INDIVIDUAL

        def obj_title(self):
            result = _CleanText(_FormValue(
                '//select[@id="ctl00_MainContent__editAdherent_'
                '_editIdentite__ddCivilite"]',
            ))(self)

            return ({
                'Monsieur': _Person.TITLE_MONSIEUR,
                'Madame': _Person.TITLE_MADAME,
                'Monseigneur': _Person.TITLE_MONSEIGNEUR,
                'Père': _Person.TITLE_PERE,
                'Soeur': _Person.TITLE_SOEUR,
                'Frère': _Person.TITLE_FRERE,
            }).get(result, _Person.TITLE_UNKNOWN)

        obj_last_name = _CleanText(_FormValue(
            '//input[@id="ctl00_MainContent__editAdherent_'
            '_editIdentite__tbNom"]',
        ))
        obj_birth_name = _CleanText(_FormValue(
            '//input[@id="ctl00_MainContent__editAdherent_'
            '_editIdentite__tbNomDeJeuneFille"]',
        ))
        obj_first_name = _CleanText(_FormValue(
            '//input[@id="ctl00_MainContent__editAdherent_'
            '_editIdentite__tbPrenom"]',
        ))

        obj_birth_date = _Date(
            _CleanText(_FormValue(
                '//input[@id="ctl00_MainContent__editAdherent_'
                '_editDateLieuNaissance__dpbDateNaissance__tbDate"]',
                default='',
            )),
            dayfirst=True,
            default=_NotAvailable,
        )

        def obj_birth_place(self):
            class FranceBirthPlace(_ItemElement):
                klass = _BirthPlace

                obj_postal_code = _CleanText(_FormValue(
                    '//input[@id="ctl00_MainContent__editAdherent_'
                    '_editDateLieuNaissance__tbCPNaissance"]',
                ))
                obj_municipality_name = _CleanText(_FormValue(
                    '//input[@id="ctl00_MainContent__editAdherent_'
                    '_editDateLieuNaissance__tbCommuneNaissance"]',
                ))

                obj__insee = _CleanText(_FormValue(
                    '//input[@id="ctl00_MainContent__editAdherent_'
                    '_editDateLieuNaissance__ddCodeInsee"]',
                    default='',
                ))
                obj_insee_code = _Regexp(
                    _Field('_insee'),
                    pattern=r'.*-([^-]+)',
                    default=None,
                )

                class obj_country(_ItemElement):
                    klass = _Country

                    obj_name = 'FRANCE'
                    obj_tam_id = 0

            class OtherBirthPlace(_ItemElement):
                klass = _BirthPlace

                obj_municipality_name = _CleanText(_FormValue(
                    '//input[@id="ctl00_MainContent__editAdherent_'
                    '_editDateLieuNaissance__tbCommuneNaissanceEtranger"]',
                    default='',
                ))

                class obj_country(_ItemElement):
                    klass = _Country

                    obj_name = _CleanText(
                        '//select[@id="ctl00_MainContent__editAdherent_'
                        '_editDateLieuNaissance__ddlPaysJS"]'
                        '/option[@selected="selected"]',
                        default='',
                    )
                    obj_tam_id = _CleanDecimal.SI(_Attr(
                        '//select[@id="ctl00_MainContent__editAdherent_'
                        '_editDateLieuNaissance__ddlPaysJS"]'
                        '/option[@selected="selected"]',
                        'value',
                        default=None,
                    ))

            is_france = _FormValue(
                '//input[@id="ctl00_MainContent__editAdherent_'
                '_editDateLieuNaissance__rbNeAFr"]',
            )(self)

            is_other = _FormValue(
                '//input[@id="ctl00_MainContent__editAdherent_'
                '_editDateLieuNaissance__rbNeAEt"]',
            )(self)

            if is_france:
                return FranceBirthPlace(self.page, parent=self)()
            elif is_other:
                return OtherBirthPlace(self.page, parent=self)()
            return None

        obj_code = _CleanText(
            '//span[@id="ctl00_MainContent__editAdherent__lbCodeAdherent"]',
        )

        def obj_delegations(self):
            return [self.page.get_delegation()]

        obj_function_start = _Date(
            _CleanText(_FormValue(
                '//input[@id="ctl00_MainContent__editAdherent_'
                '_dpbDateDebut__tbDate"]',
                default='',
            )),
            dayfirst=True,
            default=_NotAvailable,
        )
        obj_function_end = _Date(
            _CleanText(_FormValue(
                '//input[@id="ctl00_MainContent__editAdherent_'
                '_dpbDateFinFonction__tbDate"]',
                default='',
            )),
            dayfirst=True,
            default=_NotAvailable,
        )

        obj_ice_last_name = _CleanText(_FormValue(
            '//input[@id="ctl00_MainContent__editAdherent_'
            '_txtNomPersonneUrgence"]',
            default='',
        ))
        obj_ice_first_name = _CleanText(_FormValue(
            '//input[@id="ctl00_MainContent__editAdherent_'
            '_txtPrenomPersonneUrgence"]',
            default='',
        ))
        obj_ice_phone = _CleanText(_FormValue(
            '//input[@id="ctl00_MainContent__editAdherent_'
            '_txtTelephonePersonneUrgence"]',
            default='',
        ))

        class obj_address(_ItemElement):
            klass = _Address

            obj_line_1 = _CleanText(_FormValue(
                '//input[@id="ctl00_MainContent__editAdherent_'
                '_editInformations__editeurAdresseIndividu_'
                '_editeurAdresse__tbLigne1"]',
                default='',
            ))
            obj_line_2 = _CleanText(_FormValue(
                '//input[@id="ctl00_MainContent__editAdherent_'
                '_editInformations__editeurAdresseIndividu_'
                '_editeurAdresse__tbLigne2"]',
                default='',
            ))
            obj_line_3 = _CleanText(_FormValue(
                '//input[@id="ctl00_MainContent__editAdherent_'
                '_editInformations__editeurAdresseIndividu_'
                '_editeurAdresse__tbLigne3"]',
                default='',
            ))

            obj_postal_code = _CleanText(_FormValue(
                '//input[@id="ctl00_MainContent__editAdherent_'
                '_editInformations__editeurAdresseIndividu_'
                '_editeurAdresse__tbCodePostal"]',
                default='',
            ))
            obj_municipality_name = _CleanText(_FormValue(
                '//input[@id="ctl00_MainContent__editAdherent_'
                '_editInformations__editeurAdresseIndividu_'
                '_editeurAdresse__tbVille"]',
                default='',
            ))

            class obj_country(_ItemElement):
                klass = _Country

                obj_name = _CleanText(
                    '//select[@id="ctl00_MainContent__editAdherent_'
                    '_editInformations__editeurAdresseIndividu_'
                    '_editeurAdresse__divDllPays"]'
                    '/option[@selected="selected"]',
                    default='',
                )
                obj_tam_id = _CleanDecimal.SI(
                    _Attr(
                        '//select[@id="ctl00_MainContent__editAdherent_'
                        '_editInformations__editeurAdresseIndividu_'
                        '_editeurAdresse__divDllPays"]'
                        '/option[@selected="selected"]',
                        'value',
                        default=None,
                    ),
                    default=None,
                )

        obj_npai = _FormValue(
            '//input[@id="ctl00_MainContent__editAdherent_'
            '_editInformations__editeurAdresseIndividu__rbNpaiOui"]',
            default=False,
        )

        obj_home_phone = _CleanText(_FormValue(
            '//input[@id="ctl00_MainContent__editAdherent__editInformations_'
            '_tbTelephoneDomicile"]',
            default='',
        ))
        obj_work_phone = _CleanText(_FormValue(
            '//input[@id="ctl00_MainContent__editAdherent__editInformations_'
            '_tbTelephoneBureau"]',
            default='',
        ))
        obj_mobile_phone = _CleanText(_FormValue(
            '//input[@id="ctl00_MainContent__editAdherent__editInformations_'
            '_tbTelephonePortable1"]',
            default='',
        ))
        obj_mobile_phone_2 = _CleanText(_FormValue(
            '//input[@id="ctl00_MainContent__editAdherent__editInformations_'
            '_tbTelephonePortable2"]',
            default='',
        ))

        obj_personal_email = _CleanText(_FormValue(
            '//input[@id="ctl00_MainContent__editAdherent__editInformations_'
            '_tbCourrielPersonnel"]',
            default='',
        ))
        obj_dedicated_email = _CleanText(_FormValue(
            '//input[@id="ctl00_MainContent__editAdherent__editInformations_'
            '_tbCourrielProfessionnel"]',
            default='',
        ))

        obj_occupation = _CleanText(_FormValue(
            '//input[@id="ctl00_MainContent__editAdherent__editInformations_'
            '_tbProfession"]',
            default='',
        ))

        obj_allocations_code = _CleanText(_FormValue(
            '//input[@id="ctl00_MainContent__editAdherent__editInformations_'
            '_tbNumeroAllocataire"]',
            default='',
        ))

        def obj_allocations_regime(self):
            checked_general = _FormValue(
                '//input[@id="ctl00_MainContent__editAdherent_'
                '_editInformations__cbRegimeGeneral"]',
                default=False,
            )(self)

            checked_msa = _FormValue(
                '//input[@id="ctl00_MainContent__editAdherent_'
                '_editInformations__cbRegimeMSA"]',
                default=False,
            )(self)

            checked_other = _FormValue(
                '//input[@id="ctl00_MainContent__editAdherent_'
                '_editInformations__cbRegimeEtranger"]',
                default=False,
            )(self)

            if checked_general:
                return _Person.ALLOCATIONSREGIME_GENERAL
            elif checked_msa:
                return _Person.ALLOCATIONSREGIME_MSA
            elif checked_other:
                return _Person.ALLOCATIONSREGIME_OTHER

            return _Person.ALLOCATIONSREGIME_UNKNOWN

        obj_medical_intervention_rights = _FormValue(
            '//input[@id="ctl00_MainContent__editAdherent_'
            '_cbAutorisationInterventionChirurgicale"]',
        )
        obj_image_rights = _FormValue(
            '//input[@id="ctl00_MainContent__editAdherent_'
            '_cbAutorisationImage"]',
        )
        obj_information_rights = _FormValue(
            '//input[@id="ctl00_MainContent__editAdherent_'
            '_cbAutorisationInformation"]',
        )
        obj_insured = _FormValue(
            '//input[@id="ctl00_MainContent__editAdherent__cbAssuranceRc"]',
        )


class AdherentSearchPage(LoggedPage):
    def search_people(self):
        # Here:
        #
        # * We select the structure 'Toutes', which produces a postback.
        # * We run the search.

        self['ctl00$MainContent$_recherche$_selecteur$_ddStructure'] = '0'
        self.postback(
            target='ctl00$MainContent$_recherche$_selecteur$_ddStructure',
            argument='',
            scriptmanager=(
                'ctl00$_upMainContent|'
                'ctl00$MainContent$_recherche$_selecteur$_ddStructure'
            ),
        )

        self.postback(
            target='ctl00$MainContent$_recherche$_btnRechercher',
            scriptmanager=(
                'ctl00$_upMainContent|'
                'ctl00$MainContent$_recherche$_btnRechercher'
            ),
        )

    @_pagination
    @_method
    class iter_people(_PaginatedTableElement):
        table_name = 'ctl00$MainContent$_recherche$_gvResultats'
        is_postback = True

        col_name = 'Nom, Prénom'
        col_code = 'N° Adhérent'
        col_function = 'Fonction'
        col_structure = 'Structure'
        col_function_end = 'Fin Fonction'
        col_postal_code = 'CP'
        col_municipality = 'Ville'
        col_status_end = 'Fin Adhésion'

        class item(_ItemElement):
            klass = _Person

            def get_colnum(self, name):
                return self.parent.get_colnum(name)

            obj_iid = _IIDLink(_TableCell('name'))
            obj_type_ = _Person.TYPE_INDIVIDUAL
            obj_full_name = _Person.FullName(_TableCell('name'))
            obj_code = _Coalesce(
                _CleanText(_TableCell('code')),
                default=None,
            )

            obj_function_end = _Date(
                _CleanText(_TableCell('function_end')),
                dayfirst=True,
                default=None,
            )

            def obj_delegations(self):
                class item(_ItemElement):
                    klass = _Delegation

                    def get_colnum(self, name):
                        return self.parent.get_colnum(name)

                    class obj_function(_ItemElement):
                        klass = _Function

                        def validate(self, obj):
                            return bool(obj.code)

                        obj_code = _CleanText(_TableCell('function'))

                    class obj_structure(_ItemElement):
                        klass = _Structure

                        def validate(self, obj):
                            return bool(obj.name)

                        obj_name = _CleanText(_TableCell('structure'))

                return [item(self.page, parent=self)()]


class AdherentStructureListPage(LoggedPage):
    pass


class AdherentInscriptionSearchPage(LoggedPage):
    def search_people(self, last_name: str = '', first_name: str = ''):
        self['ctl00$MainContent$_recherche$_tbNom'] = last_name
        self['ctl00$MainContent$_recherche$_tbPrenom'] = first_name

        self.postback(
            target='ctl00$MainContent$_recherche$_btnRechercher',
            scriptmanager=(
                'ctl00$_upMainContent|'
                'ctl00$MainContent$_recherche$_btnRechercher'
            ),
        )

    @_pagination
    @_method
    class iter_people(_PaginatedTableElement):
        table_name = 'ctl00$MainContent$_recherche$_gvResultats'
        is_postback = True

        col_url = _re.compile(r'Nom')
        col_code = 'Code adhérent'
        col_birth_date = 'Date Naissance'

        class item(_ItemElement):
            klass = _Person

            obj_iid = _IIDLink(_TableCell('url'))
            obj_type_ = _Person.TYPE_INDIVIDUAL
            obj_code = _CleanText(_TableCell('code'))
            obj_full_name = _Person.FullName(_TableCell('url'))
            obj_birth_date = _Date(
                _CleanText(_TableCell('birth_date')),
                dayfirst=True,
                default=None,
            )


# ---
# People related pages.
# ---


class PersonSearchPage(LoggedPage):
    def search_people(self):
        self.submit(
            target='ctl00$MainContent$_recherche$_btnRechercher',
        )

    @_pagination
    @_method
    class iter_people(_PaginatedTableElement):
        table_name = 'ctl00$MainContent$_recherche$_gvResultats'
        is_postback = False

        col_name = 'Nom'
        col_address = 'Adresse'
        col_postal_code = 'CP'
        col_municipality = 'Ville'

        class item(_ItemElement):
            klass = _Person

            obj_iid = _IIDLink(_TableCell('name'))

            # Technically, type depends on whether the link behind is
            # a ResumePersonne.aspx or ResumeAdherent.aspx link.
            #
            # However, all links on this page are ResumeAdherent.aspx,
            # and redirect to ResumePersonne.aspx behind if the person is
            # not an individual.
            #
            # TODO: One way to determine this would be to read the 'Type'
            # filter and use it if defined, however this is quite unreliable
            # because it could be set after the search is done.

            obj_type_ = _Person.TYPE_UNKNOWN

            obj_full_name = _Person.FullName(
                _TableCell('name'),
                has_title=False,
            )


class PersonPage(LoggedPage):
    @_method
    class get_person(_ItemElement):
        klass = _Person

        obj_type_ = _Person.TYPE_LEGAL
        obj_full_name = _Person.FullName(
            '//span[@id="ctl00_ctl00__divTitre"]',
        )

        class obj_address(_ItemElement):
            klass = _Address

            obj_line_1 = _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__resumeAdresse__lbLigne1"]',
                default='',
            )
            obj_line_2 = _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__resumeAdresse__lbLigne2"]',
                default='',
            )
            obj_line_3 = _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__resumeAdresse__lbLigne3"]',
                default='',
            )

            obj_postal_code = _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__resumeAdresse__lbCodePostal"]',
            )
            obj_municipality_name = _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__resumeAdresse__lbVille"]',
            )

            class obj_country(_ItemElement):
                klass = _Country

                obj_name = _CleanText(
                    '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
                    '_resume__resumeAdresse__lbPays"]',
                )

        def obj_npai(self):
            result = _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__lblNpai"]',
                default=_NotAvailable,
            )(self)

            if _empty(result):
                return result

            return result.casefold() == 'oui'

        obj_home_phone = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
            '_resume__lblTelephone"]',
        )


class PersonEditPage(LoggedPage):
    @_method
    class get_person(_ItemElement):
        klass = _Person

        obj_type_ = _Person.TYPE_LEGAL
        obj_full_name = _Person.FullName(_FormValue(
            '//input[@id="ctl00_MainContent__editeur__tbNom"]',
        ))

        class obj_address(_ItemElement):
            klass = _Address

            obj_line_1 = _CleanText(_FormValue(
                '//input[@id="ctl00_MainContent__editeur_'
                '_editeurAdresseIndividu__editeurAdresse__tbLigne1"]',
            ))
            obj_line_2 = _CleanText(_FormValue(
                '//input[@id="ctl00_MainContent__editeur_'
                '_editeurAdresseIndividu__editeurAdresse__tbLigne2"]',
            ))
            obj_line_3 = _CleanText(_FormValue(
                '//input[@id="ctl00_MainContent__editeur_'
                '_editeurAdresseIndividu__editeurAdresse__tbLigne3"]',
            ))

            obj_postal_code = _CleanText(_FormValue(
                '//input[@id="ctl00_MainContent__editeur_'
                '_editeurAdresseIndividu__editeurAdresse__tbCodePostal"]',
            ))
            obj_municipality_name = _CleanText(_FormValue(
                '//input[@id="ctl00_MainContent__editeur_'
                '_editeurAdresseIndividu__editeurAdresse__tbVille"]',
            ))

            class obj_country(_ItemElement):
                klass = _Country

                obj_id = _CleanDecimal.SI(_Attr(
                    '//select[@id="ctl00_MainContent__editeur_'
                    '_editeurAdresseIndividu__editeurAdresse__ddlPays"]'
                    '/option[@selected="selected"]',
                    'value',
                ))
                obj_name = _CleanText(_FormValue(
                    '//select[@id="ctl00_MainContent__editeur_'
                    '_editeurAdresseIndividu__editeurAdresse__ddlPays"]',
                ))

        obj_npai = _FormValue(
            '//input[@id="ctl00_MainContent__editeur_'
            '_editeurAdresseIndividu__rbNpaiOui"]',
        )

        obj_home_phone = _CleanText(_FormValue(
            '//input[@id="ctl00_MainContent__editeur__tbTelephoneBureau"]',
        ))


# ---
# Secondary function related pages.
# ---


class SecondaryFunctionsPage(LoggedPage):
    def search_delegations(self):
        # If there is currently a selected structure for the query,
        # we deselect it.

        delete_button = _XPath(
            '//a[@id="ctl00_MainContent__btnStructure__btnSupprimer"]',
            default=None,
        )(self)

        if delete_button is not None:
            self.postback(
                target='ctl00$MainContent$_btnStructure$_btnSupprimer',
                scriptmanager=(
                    'ctl00$_upMainContent|'
                    'ctl00$MainContent$_btnStructure$_btnSupprimer'
                ),
            )

        # Search and iterate over all listed secondary functions.

        self.postback(
            target='ctl00$MainContent$_btnRechercher',
            scriptmanager=(
                'ctl00$_upMainContent|ctl00$MainContent$_btnRechercher'
            ),
        )

    @_method
    class iter_delegations(_TableElement):
        klass = _Delegation

        head_xpath = (
            '//table[@id="ctl00_MainContent__gvDelegations"]'
            '/tr[@class="entete"]/th'
        )
        item_xpath = (
            '//table[@id="ctl00_MainContent__gvDelegations"]'
            '/tr[starts-with(@class, "ligne")]'
        )

        col_adherent = 'Adhérent'
        col_function = 'Fonction'
        col_structure = 'Structure'

        class item(_ItemElement):
            klass = _Delegation

            def get_colnum(self, name):
                return self.parent.get_colnum(name)

            obj_is_primary = False

            class obj_person(_ItemElement):
                klass = _Person

                obj_iid = _IIDLink(_TableCell('adherent'))
                obj_full_name = _Person.FullName(_TableCell('adherent'))

            class obj_function(_ItemElement):
                klass = _Function

                obj_label = _Function.Label(_TableCell('function'))

            class obj_structure(_ItemElement):
                klass = _Structure

                obj_iid = _IIDLink(_TableCell('structure'))
                obj_label = _Structure.Label(_TableCell('structure'))

# ---
# Structure-related pages.
# ---


class StructurePage(LoggedPage):
    def go_to_hierarchy(self):
        self.submit(
            target=(
                'ctl00$ctl00$MainContent$TabsContent'
                '$TabContainerResumeStructure'
            ),
            argument='activeTabChanged:0',
        )

    def go_to_summary(self):
        self.submit(
            target=(
                'ctl00$ctl00$MainContent$TabsContent'
                '$TabContainerResumeStructure'
            ),
            argument='activeTabChanged:1',
        )

    def go_to_specialities(self):
        self.submit(
            target=(
                'ctl00$ctl00$MainContent$TabsContent'
                '$TabContainerResumeStructure'
            ),
            argument='activeTabChanged:2',
        )

    def go_to_delegations(self):
        self.submit(
            target=(
                'ctl00$ctl00$MainContent$TabsContent'
                '$TabContainerResumeStructure'
            ),
            argument='activeTabChanged:3',
        )

    def go_to_contacts(self):
        self.submit(
            arget=(
                'ctl00$ctl00$MainContent$TabsContent'
                '$TabContainerResumeStructure'
            ),
            argument='activeTabChanged:4',
        )

    def go_to_bank_accounts(self):
        self.submit(
            arget=(
                'ctl00$ctl00$MainContent$TabsContent'
                '$TabContainerResumeStructure'
            ),
            argument='activeTabChanged:5',
        )

    def go_to_markers(self):
        self.submit(
            arget=(
                'ctl00$ctl00$MainContent$TabsContent'
                '$TabContainerResumeStructure'
            ),
            argument='activeTabChanged:6',
        )

    def go_to_events(self):
        self.submit(
            arget=(
                'ctl00$ctl00$MainContent$TabsContent'
                '$TabContainerResumeStructure'
            ),
            argument='activeTabChanged:7',
        )


class StructureHierarchyPage(StructurePage):
    is_here = (
        '//div[@id="ctl00_ctl00_MainContent_TabsContent_'
        'TabContainerResumeStructure__tabHierarchie__divHierarchie"]'
    )

    @_method
    class iter_structure_parents(_PaginatedTableElement):
        table_name = (
            'ctl00$ctl00$MainContent$TabsContent$'
            'TabContainerResumeStructure$_tabHierarchie$_gvParents'
        )
        is_postback = True  # only guessing here.

        col_code = 'Code'
        col_name = 'Nom'

        class item(_ItemElement):
            klass = _Structure

            obj_iid = _IIDLink(_TableCell('code'))
            obj_code = _CleanText(_TableCell('code'))
            obj_name = _CleanText(_TableCell('name'))

    @_method
    class iter_structure_children(_PaginatedTableElement):
        table_name = (
            'ctl00$ctl00$MainContent$TabsContent$'
            'TabContainerResumeStructure$_tabHierarchie$_gvEnfants'
        )
        is_postback = True  # only guessing here.

        col_code = 'Code'
        col_name = 'Nom'

        class item(_ItemElement):
            klass = _Structure

            obj_iid = _IIDLink(_TableCell('code'))
            obj_code = _CleanText(_TableCell('code'))
            obj_name = _CleanText(_TableCell('name'))

    def get_structure_parent(self):
        for obj in self.iter_structure_parents():
            return obj


class StructureSummaryPage(StructurePage):
    is_here = (
        '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
        'TabContainerResumeStructure__tabResume__resume__lblNom"]'
    )

    @_method
    class get_structure(_ItemElement):
        klass = _Structure

        obj_code = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeStructure__tabResume__resume_'
            '_lblCodeStructure"]',
        )
        obj_name = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeStructure__tabResume__resume__lblNom"]',
        )
        obj_description = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeStructure__tabResume__resume__lblDescription"]',
        )
        obj_status = _Structure.Status(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeStructure__tabResume__resume__lblStatut"]',
        )
        obj_type_ = _Structure.Type(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeStructure__tabResume__resume__lblType"]',
        )
        obj_phone = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeStructure__tabResume__resume__lblTelephone"]',
        )
        obj_fax = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeStructure__tabResume__resume__lblFax"]',
        )
        obj_email = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_TabsContent_'
            'TabContainerResumeStructure__tabResume__resume__lblCourrier"]',
        )


class StructureSpecialitiesPage(StructurePage):
    is_here = (
        '//table[@id="ctl00_ctl00_MainContent_TabsContent_'
        'TabContainerResumeStructure__tabSpecialites__gvSpecialites"]'
    )


class StructureDelegationsPage(StructurePage):
    is_here = (
        '//table[@id="ctl00_ctl00_MainContent_TabsContent_'
        'TabContainerResumeStructure__tabDeleguees__gvDeleguees"]'
    )


class StructureContactsPage(StructurePage):
    is_here = (
        '//table[@id="ctl00_ctl00_MainContent_TabsContent_'
        'TabContainerResumeStructure__tabContacts__gvContacts"]'
    )


class StructureBankAccountsPage(StructurePage):
    is_here = (
        '//table[@id="ctl00_ctl00_MainContent_TabsContent_'
        'TabContainerResumeStructure__tabComptes__divComptesBancaires"]'
    )


class StructureMarkersPage(StructurePage):
    is_here = (
        '//table[@id="ctl00_ctl00_MainContent_TabsContent_'
        'TabContainerResumeStructure__tabMarqueurs__gvMarqueurs"]'
    )


class StructureEventsPage(StructurePage):
    is_here = (
        '//table[@id="ctl00_ctl00_MainContent_TabsContent_'
        'TabContainerResumeStructure__tabEvenements__evenements_'
        '_gvEvenements"]'
    )


class StructureSearchPage(_MSHTMLPage, _LoggedPage):
    def search_structures(self):
        self.submit(
            target='ctl00$Popup$_recherche$_btnRechercher',
        )

    @_pagination
    @_method
    class iter_structures(_PaginatedTableElement):
        table_name = 'ctl00$Popup$_recherche$_gvResultats'
        is_postback = False

        col_checkbox = ''
        col_structure = 'Structure'
        col_status = 'Statut'
        col_department = 'Département'
        col_type = 'Type'
        col_phone = 'Téléphone'

        class item(_ItemElement):
            klass = _Structure

            obj_iid = _IIDLink(_TableCell('checkbox'))
            obj_label = _Structure.Label(_TableCell('structure'))
            obj_type_ = _Structure.Type(_TableCell('type'))
            obj_status = _Structure.Status(_TableCell('status'))
            obj_phone = _CleanText(_TableCell('phone'))


class StructureCompletionPage(_JsonDataPage, _LoggedPage):
    # This page is constituded of elements being either:
    # * A divider, with a title.
    # * A structure, with identifier, code and name.
    #
    # It is generally composed like this:
    #
    # = Divider 1
    # * Structure 1
    # * Structure 2
    # * Structure 3
    # = Divider 2
    # * Structure 4
    # * Structure 5
    # * Structure 6
    #
    # Dividers have the special identifier 'Divider'.
    # Known dividers are the following:
    #
    # * "Structures enfants": following structures are child structures.
    # * "Structures soeurs": following structures are sister structures.

    def iter_structures(self, section=all):
        class item(_ItemElement):
            klass = _Structure

            obj_id = _Coalesce(
                _CleanDecimal.SI(_Dict('id'), default=None),
                _CleanText(_Dict('id')),
                default=None,
            )
            obj_label = _Structure.Label(_Dict('name'))

        current_section = None
        for raw_obj in self.doc:
            obj = item(self, el=raw_obj)()
            if obj.id == 'Divider':
                current_section = obj.name
                continue

            if section is all or section is any or section == current_section:
                yield obj

    def iter_structure_children(self):
        return self.iter_structures('Structures enfants')

    def iter_structure_sisters(self):
        return self.iter_structures('Structures soeurs')


# ---
# Functions.
# ---


class FunctionsPage(_MSHTMLPage, _LoggedPage):
    def search_functions(self):
        self.submit(
            target='ctl00$Popup$_recherche$_btnRechercher',
        )

    @_pagination
    @_method
    class iter_functions(_PaginatedTableElement):
        table_name = 'ctl00$Popup$_recherche$_gvResultats'
        is_postback = False

        col_code = 'Code'
        col_masculine_name = 'Nom masculin'
        col_feminine_name = 'Nom féminin'
        col_min_age = 'Age minimum'
        col_max_age = 'Age maximum'
        col_type = 'Type de structure'
        col_speciality = 'Spécialité'

        class item(_ItemElement):
            klass = _Function

            obj_code = _CleanText(_TableCell('code'))
            obj_masculine_name = _CleanText(_TableCell('masculine_name'))
            obj_feminine_name = _CleanText(_TableCell('feminine_name'))
            obj_min_age = _CleanDecimal(_TableCell('min_age'))
            obj_max_age = _CleanDecimal(_TableCell('max_age'))


class FunctionsCompletionPage(_JsonDataPage, _LoggedPage):
    @_method
    class iter_functions(_DictElement):
        class item(_ItemElement):
            klass = _Function

            obj_id = _CleanDecimal.SI(_Dict('id'))
            obj_label = _Function.Label(_Dict('name'), is_full=True)


# ---
# Teams.
# ---


class TeamSearchPage(LoggedPage):
    def go_to_structure(self, id_: int):
        self.postback(
            target='ctl00$MainContent$_navigateur$_autocompleteStructures',
            argument=(
                '{"eventName":"Add","id":"' f'{id_}' '","name":""}'
            ),
        )

    def go_to_parent(self):
        self.submit(
            target='ctl00$MainContent$_navigateur$_btnUp',
        )

    @_method
    class get_structure(_ItemElement):
        klass = _Structure

        obj_id = _Regexp(
            _FormValue(
                '//input[@id="ctl00_MainContent__navigateur_'
                '_autocompleteStructures__hiddenAutoComplete"]',
            ),
            pattern=r'"id":"([0-9]+)"',
        )
        obj_label = _Structure.Label(_Regexp(
            _FormValue(
                '//input[@id="ctl00_MainContent__navigateur_'
                '_autocompleteStructures__hiddenAutoComplete"]',
            ),
            pattern=r'"name":"([^"]+)"',
        ))


# ---
# Bank accounts.
# ---


class BankAccountPage(LoggedPage):
    @_method
    class get_bank_account(_ItemElement):
        klass = _BankAccount

        obj_title = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_DivsContent__resume_'
            '_lblIntitule"]',
        )
        obj_rib = _Format(
            '%s%s%s%s',
            _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__lblCodeBanque"]',
            ),
            _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__lblCodeGuichet"]',
            ),
            _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__lblnumero"]',
            ),
            _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__lblCleRib"]',
            ),
        )

        obj_iban = _Format(
            '%s%s%s%s%s%s',
            _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__lbCodePaysIban"]',
            ),
            _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__lbCleControleIBAN"]',
            ),
            _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__lbCodeBanqueIBAN"]',
            ),
            _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__lbCodeAgenceIBAN"]',
            ),
            _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__lbNumeroCompteIban"]',
            ),
            _CleanText(
                '//span[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__lbCleRibIban"]',
            ),
        )

        obj_bic = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_DivsContent__resume__lbBIC"]',
        )
        obj_rum = _CleanText(
            '//span[@id="ctl00_ctl00_MainContent_DivsContent__resume__lbRum"]',
        )

        class obj_structure(_ItemElement):
            klass = _Structure

            def validate(self, obj):
                return not _empty(obj.code)

            obj_iid = _IIDLink(
                '//a[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__hlStructure"]',
            )
            obj_label = _Structure.Label(
                '//a[@id="ctl00_ctl00_MainContent_DivsContent_'
                '_resume__hlStructure"]',
                default='',
            )


# ---
# Insured good.
# ---


class InsuredGoodPage(LoggedPage):
    pass


class InsuredGoodEditPage(LoggedPage):
    pass


class InsuredGoodCreatePage(LoggedPage):
    pass


class InsuredGoodSearchPage(LoggedPage):
    pass


# ---
# Insured vehicle.
# ---


class InsuredVehicleSearchPage(LoggedPage):
    pass


class InsuredVehiclePage(LoggedPage):
    pass


# ---
# Camps (obsolete).
# ---


class CampPage(LoggedPage):
    pass


# ---
# Places (obsolete).
# ---


class PlacePage(LoggedPage):
    pass


# End of file.

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
"""monprojetsgdf pages definition."""

from woob.browser.elements import (
    DictElement as _DictElement, ItemElement as _ItemElement,
    method as _method,
)
from woob.browser.filters.json import Dict as _Dict
from woob.browser.filters.standard import (
    CleanDecimal as _CleanDecimal, CleanText as _CleanText,
    Coalesce as _Coalesce, DateTime as _DateTime, MapIn as _MapIn,
)
from woob.browser.pages import (
    JsonPage as _JsonPage, LoggedPage as _LoggedPage,
)

from visyerres_sgdf_woob.capabilities import (
    Continent as _Continent, Country as _Country, Delegation as _Delegation,
    Function as _Function, Person as _Person, Structure as _Structure,
)

__all__ = ['ErrorPage', 'LoginPage', 'ProjectPage', 'ProjectsPage']


class _FunctionElement(_ItemElement):
    klass = _Function

    obj_code = _CleanText(_Dict('fonction/code'))
    obj_label = _Function.Label(_Dict('fonction/libelle'))


class _StructureElement(_ItemElement):
    klass = _Structure

    obj_code = _CleanText(_Dict('code'))
    obj_name = _CleanText(_Dict('libelle'))
    obj_status = _MapIn(
        _Dict('actif'),
        {
            True: _Structure.STATUS_OPEN,
            False: _Structure.STATUS_UNKNOWN,
        },
    )

    # TODO: 'codeDepartement'.
    # TODO: Member has a 'sgdfWsHash' attribute, which is made of
    # 40 hexadecimal characters. I do not know how, or even whether
    # if it is linked to the intranet identifier.


class _AdherentElement(_ItemElement):
    klass = _Person

    obj_type = _Person.TYPE_INDIVIDUAL
    obj_code = _CleanText(_Dict('numero'))

    obj_title = _MapIn(_Dict('civilite/id'), {
        1: _Person.TITLE_MONSIEUR,
        2: _Person.TITLE_MADAME,
    })
    obj_last_name = _CleanText(_Dict('nom'))
    obj_first_name = _CleanText(_Dict('prenom'))

    obj_birth_date = _DateTime(_CleanText(_Dict('dateNaissance')))
    obj_birth_name = _DateTime(_CleanText(_Dict('nomNaissance')))

    obj_mobile_phone = _CleanText(_Dict('telephonePortable'))

    class obj_delegations(_DictElement):
        item_xpath = 'structureAdherents'

        class item(_ItemElement):
            klass = _Delegation

            obj_id = _Dict('id')
            obj_is_primary = _Dict('rattachementPrincipal')

            class obj_function(_FunctionElement):
                pass

            class obj_structure(_StructureElement):
                pass


# ---
# Page definitions.
# ---


class ErrorPage(_JsonPage, _LoggedPage):
    # Known errors:
    #
    #  code | message
    # ------+--------------
    #   401 | Unauthorized

    def get_error_code(self):
        return _CleanDecimal.SI(_Dict('code', default=None))(self.doc)

    def get_error_message(self):
        return _Coalesce(
            _CleanText(_Dict('message', default='')),
            default=None,
        )(self.doc)


class LoginPage(_JsonPage):
    def get_access_token(self):
        return _CleanText(_Dict('token'))(self.doc)

    @_method
    class get_adherent(_ItemElement):
        klass = _Person

        code = _Dict('userData/numero')
        full_name = _Person.FullName(
            _Dict('userData/fullName'),
            has_title=False,
        )

        # monprojet calls delegations 'functionnalities', and adds quite
        # a bit of information to them, probably deduced from the position.

        class structure(_ItemElement):
            klass = _Structure

            code = _Dict('userData/selectedFunctionality/codeStructure')
            name = _Dict('userData/selectedFunctionality/libelleStructure')

        class function(_ItemElement):
            klass = _Function

            code = _Dict('userData/selectedFunctionality/codeFonction')
            name = _Dict('userData/selectedFunctionality/libelleFonction')


class ProjectsPage(_JsonPage, _LoggedPage):
    pass


class ProjectPage(_JsonPage, _LoggedPage):
    pass


class StructuresPage(_JsonPage, _LoggedPage):
    # Note that monprojet considers structure codes to be unique, when,
    # on the intranet, they are not; however, this isn't really an issue
    # since all *active* structures have unique codes, and monprojet mostly
    # interacts with active structures.
    #
    # TODO: all, or most? Actually not very sure.

    @_method
    class iter_structures(_DictElement):
        class item(_StructureElement):
            pass


class AdherentsPage(_JsonPage, _LoggedPage):
    @_method
    class iter_adherents(_DictElement):
        class item(_AdherentElement):
            pass


class CountriesPage(_JsonPage, _LoggedPage):
    @_method
    class iter_countries(_DictElement):
        class item(_ItemElement):
            klass = _Country

            obj_id = _Dict('id')
            obj_name = _Dict('libelle')
            obj_tam_id = _Dict('idTamPays')
            obj_open_ = _Dict('paysOuvert')
            obj_contact_email = _Dict('emailContact')

            class obj_continent(_ItemElement):
                klass = _Continent

                obj_id = _Dict('codeContinent', default=None)
                obj_omms_id = _Dict('continentOmms/code')
                obj_name = _Dict('continentOmms/libelle')

# End of file.

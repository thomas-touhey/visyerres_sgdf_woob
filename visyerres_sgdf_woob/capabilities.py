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
"""Define capabilities."""

import re as _re
from datetime import date as _date, datetime as _datetime
from typing import Optional as _Optional

from woob.browser.filters.standard import CleanText as _CleanText
from woob.capabilities.base import (
    BaseObject as _BaseObject, BoolField as _BoolField, Enum as _Enum,
    EnumField as _EnumField, Field as _Field, IntField as _IntField,
    NotAvailable as _NotAvailable, StringField as _StringField,
    empty as _empty,
)

from visyerres_sgdf_woob.utils import IID as _IID

__all__ = (
    'Continent', 'Country', 'Function', 'Structure', 'StructureStatus',
    'StructureType',
)


class _IIDField(_Field):
    """A field which accepts intranet identifiers."""

    def __init__(self, doc, **kwargs):
        super().__init__(doc, _IID, **kwargs)

    def convert(self, value):
        if isinstance(value, _IID):
            return value
        if not value:
            return None
        return _IID(value)


class Continent(_BaseObject):
    """Represents a continent."""

    name = _StringField('Name for the continent')
    omms_id = _IntField('OMMS identifier for the continent')
    name = _StringField('Name for the continent')


class Country(_BaseObject):
    """Represents a country."""

    name = _StringField('Country name')
    tam_id = _IntField('TAM identifier of the country')
    open_ = _BoolField('Whether the country is opened or not')
    continent = _Field('Country continent', Continent)
    contact_email = _StringField('Contact e-mail address amongst SGDF')


class Address(_BaseObject):
    """Represents a postal / residential address."""

    line_1 = _StringField('First line')
    line_2 = _StringField('Second line')
    line_3 = _StringField('Third line')
    postal_code = _StringField('Postal code')
    municipality_name = _StringField('Municipality name')
    country = _Field('Country', Country)


class BirthPlace(_BaseObject):
    """Represents a birth place."""

    postal_code = _StringField('Postal code')
    insee_code = _StringField('INSEE code')
    municipality_name = _StringField('Municipality name')
    country = _Field('Country', Country)


class StructureStatus(_Enum):
    """Describe a structure status.

    .. py:data:: OPEN

        The structure is currently open, i.e. currently active.

    .. py:data:: CLOSED

        The structure is closed, i.e. no longer active.

    .. py:data:: SUSPENDED

        The structure is suspended, i.e. not currently active.
    """

    UNKNOWN = 'unknown'

    OPEN = 'open'
    CLOSED = 'closed'
    SUSPENDED = 'suspended'


class StructureType(_Enum):
    """Describe a structure type.

    .. py:data:: SOMMET

        Structure tree root; note that there are currently two roots,
        the 'SCOUTS ET GUIDES DE FRANCE' root which is open, and the
        'GUIDES DE FRANCE' root which is closed.

    .. py:data:: TERRITOIRE

        Usually a subdivision of the root; manages a set of groups
        usually located in a given geographic area and linked to one or more
        national administrative subdivisions, e.g. regions or departments
        depending on the needs.

    .. py:data:: GROUPE

        Usually a subdivision of territories; manages the activity from a
        local point of view, i.e. a municipality or a set of municipalities.

    .. py:data:: ASSOCIES_N

        A group of people formed to accomplish a mission at root level.

    .. py:data:: ASSOCIES_T

        A group of people formed to accomplish a mission at territory level.

    .. py:data:: ASSOCIES_L

        A group of people formed to accomplish a mission at group level.

    .. py:data:: CENTRE_NATIONAL

        Either a national administrative subdivision such as regions,
        resource centers within the organization, or other teams.

    .. py:data:: UNITE_FARFADETS

        A unit with participants between 6 and 8, accompanied by their parents.
        Used to be 'Sarabandes' until 2007. More information:

        https://fr.scoutwiki.org/Farfadets
        https://fr.scoutwiki.org/Sarabande

    .. py:data:: UNITE_8_11_ANS

        A unit with participants between 8 and 11, accompanied by their
        scout leaders (chefs et cheftaines).
        Usually called 'Louveteaux-jeanettes-moussaillons'; used to be
        called 'Louveteaux-louvettes' before the SDF/GDF fusion in 2004.
        More information:

        https://fr.scoutwiki.org/Louveteaux_et_jeannettes

    .. py:data:: UNITE_11_14_ANS

        A unit with participants between 11 and 14, accompanied by their
        scout leaders (chefs et cheftaines).
        Usually called 'Scouts-guides-mousses'.
        More information:

        https://fr.scoutwiki.org/Scouts_et_guides_(SGDF)

    .. py:data:: UNITE_14_17_ANS

        A unit with participants between 14 and 17, accompanied by their
        scout leaders (chefs et cheftaines).
        Usually called 'Pionniers-caravelles'.
        More information:

        https://fr.scoutwiki.org/Pionniers_et_caravelles_(SGDF)

    .. py:data:: UNITE_17_20_ANS

        A unit with participants between 17 and 20, accompanied by their
        accompanist (accompagnateur compagnons).
        Usually called 'Compagnons'.
        More information:

        https://fr.scoutwiki.org/Compagnons_(SGDF)

    .. py:data:: UNITE_VENT_DU_LARGE

        A unit with adult participants with handicaps.
        Usually called 'Audace', previously called 'Vent du Large'.
        More information:

        https://fr.scoutwiki.org/Audace

    .. py:data:: AUTRE

        Other structure.
    """

    UNKNOWN = 'unknown'

    SOMMET = 'sommet'
    TERRITOIRE = 'territoire'
    GROUPE = 'groupe'
    ASSOCIES_N = 'associes_n'
    ASSOCIES_T = 'associes_t'
    ASSOCIES_L = 'associes_l'
    CENTRE_NATIONAL = 'centre_national'

    UNITE_FARFADETS = 'unite_farfadets'
    UNITE_8_11_ANS = 'unite_8_11_ans'
    UNITE_11_14_ANS = 'unite_11_14_ans'
    UNITE_14_17_ANS = 'unite_14_17_ans'
    UNITE_17_20_ANS = 'unite_17_20_ans'
    UNITE_VENT_DU_LARGE = 'unite_vent_du_large'
    UNITE_AUDACE = 'unite_audace'

    AUTRE = 'autre'


class Structure(_BaseObject):
    """Representation of the structure."""

    @classmethod
    def Label(klass, *args, **kwargs):
        """Get a filter for reading the code and name from a string."""

        class Filter(_CleanText):
            def __call__(self, item):
                full_name = super().__call__(item)
                full_name_parts = full_name.split('-')

                if len(full_name_parts) > 1:
                    code_part = full_name_parts[0].strip()
                    if _re.match(r'[A-Z0-9]+', code_part):
                        item.obj.code = code_part
                        full_name_parts.pop(0)

                item.obj.name = '-'.join(full_name_parts).lstrip()

            def filter(self, text):  # noqa: A003
                return super().filter(text)

        return Filter(*args, **kwargs)

    @classmethod
    def Type(klass, *args, **kwargs):
        """Get a filter for reading the type from a string."""

        class Filter(_CleanText):
            def filter(self, item):  # noqa: A003
                result = super().filter(item).casefold()

                if 'autre' in result:
                    return StructureType.AUTRE
                elif 'sommet' in result:
                    return StructureType.SOMMET
                elif 'territoire' in result:
                    return StructureType.TERRITOIRE
                elif 'groupe' in result:
                    return StructureType.GROUPE
                elif 'membres assoc' in result and 'national' in result:
                    return StructureType.ASSOCIES_N
                elif 'membres assoc' in result and 'territor' in result:
                    return StructureType.ASSOCIES_T
                elif 'membres assoc' in result and 'local' in result:
                    return StructureType.ASSOCIES_L
                elif 'centre national' in result:
                    return StructureType.CENTRE_NATIONAL
                elif 'farfa' in result:
                    return StructureType.UNITE_FARFADETS
                elif '8-11' in result:
                    return StructureType.UNITE_8_11_ANS
                elif '11-14' in result:
                    return StructureType.UNITE_11_14_ANS
                elif '14-17' in result:
                    return StructureType.UNITE_14_17_ANS
                elif '17-20' in result:
                    return StructureType.UNITE_17_20_ANS
                elif 'vent du large' in result:
                    return StructureType.UNITE_VENT_DU_LARGE
                elif 'audace' in result:
                    return StructureType.UNITE_AUDACE

                return StructureType.UNKNOWN

        return Filter(*args, **kwargs)

    @classmethod
    def Status(klass, *args, **kwargs):
        """Get a filter for reading the status from a string."""

        class Filter(_CleanText):
            def filter(self, item):  # noqa: A003
                result = super().filter(item).casefold()

                if 'uvert' in result:
                    return StructureStatus.OPEN
                elif 'erm' in result:
                    return StructureStatus.CLOSED
                elif 'uspendu' in result:
                    return StructureStatus.SUSPENDED

                return StructureStatus.UNKNOWN

        return Filter(*args, **kwargs)

    iid = _IIDField('Structure IID')
    code = _StringField('Structure code')
    name = _StringField('Structure name')
    description = _StringField('Structure description')

    status = _EnumField('Structure status', StructureStatus)
    type_ = _EnumField('Structure type', StructureType)
    phone = _StringField('Structure phone number')
    fax = _StringField('Structure fax number')
    email = _StringField('Structure email')

    @property
    def label(self):
        """Get the structure label."""

        if self.code and self.name:
            return f'{self.code} - {self.name}'
        return _NotAvailable

    @label.setter
    def label(self, value):
        pass  # virtual property


class Function(_BaseObject):
    """Describe a function and its properties."""

    @classmethod
    def Label(klass, *args, **kwargs):
        """Get a filter for gathering structure codes and names from labels."""

        class Filter(_CleanText):
            __slots__ = ('_is_full',)

            def __init__(self, *args, is_full: bool = False, **kwargs):
                super().__init__(*args, **kwargs)
                self._is_full = is_full

            def __call__(self, item):
                full_name = super().__call__(item)

                m = _re.match(r'(.+)\s*\(([^\)]+)\)', full_name)
                if m is not None:
                    code, name = m.groups()
                    item.obj.code = code.strip()

                    name = name.strip()

                    if self._is_full:
                        name = name.split('/')
                        if len(name) == 1:
                            item.obj.masculine_name = name[0].strip()
                            item.obj.feminine_name = item.obj.masculine_name
                        else:
                            item.obj.masculine_name = (
                                '/'.join(name[:len(name) // 2]).strip()
                            )
                            item.obj.feminine_name = (
                                '/'.join(name[len(name) // 2:]).strip()
                            )
                    else:
                        item.obj.name = name.strip()

            def filter(self, text):  # noqa: A003
                return super().filter(text)

        return Filter(*args, **kwargs)

    code = _StringField('Function code')
    name = _StringField('Function name for given person')

    masculine_name = _StringField('Function masculine name')
    feminine_name = _StringField('Function feminine name')
    min_age = _IntField('Minimum age')
    max_age = _IntField('Maximum age')

    @property
    def label(self):
        """Get the function label."""

        if self.code and self.name:
            return f'{self.name} ({self.code})'
        return _NotAvailable

    @label.setter
    def label(self, value):
        pass  # virtual property


class PersonType(_Enum):
    """Describe the person type."""

    UNKNOWN = 'unknown'

    INDIVIDUAL = 'individual'
    LEGAL = 'legal'


class PersonTitle(_Enum):
    """Describe a person title."""

    UNKNOWN = 'unknown'

    MONSIEUR = 'mister'
    MADAME = 'miss'
    MONSEIGNEUR = 'monseigneur'
    PERE = 'pere'
    SOEUR = 'soeur'
    FRERE = 'frere'


class PersonStatus(_Enum):
    """Describe a person status."""

    UNKNOWN = 'unknown'

    PREINSCRIT = 'preinscrit'
    INSCRIT = 'inscrit'
    ADHERENT = 'adherent'
    INVITE = 'invite'
    A_QUITTE_L_ASSOCIATION = 'a_quitte_l_association'
    DECEDE = 'decede'


class AllocationsRegime(_Enum):
    """Describe an allocations regime."""

    UNKNOWN = 'unknown'

    GENERAL = 'general'  # Régime général (CAF, Maritime, SNCF, ...).
    MSA = 'msa'  # MSA
    OTHER = 'other'  # Étranger, conseil de l'Europe.


class Person(_BaseObject):
    """Describe an adherent or a legal entity and its properties."""

    TYPE_UNKNOWN = PersonType.UNKNOWN
    TYPE_INDIVIDUAL = PersonType.INDIVIDUAL
    TYPE_LEGAL = PersonType.LEGAL

    TITLE_UNKNOWN = PersonTitle.UNKNOWN
    TITLE_MONSIEUR = PersonTitle.MONSIEUR
    TITLE_MADAME = PersonTitle.MADAME
    TITLE_MONSEIGNEUR = PersonTitle.MONSEIGNEUR
    TITLE_PERE = PersonTitle.PERE
    TITLE_SOEUR = PersonTitle.SOEUR
    TITLE_FRERE = PersonTitle.FRERE

    STATUS_UNKNOWN = PersonStatus.UNKNOWN
    STATUS_PREINSCRIT = PersonStatus.PREINSCRIT
    STATUS_INSCRIT = PersonStatus.INSCRIT
    STATUS_ADHERENT = PersonStatus.ADHERENT
    STATUS_INVITE = PersonStatus.INVITE
    STATUS_A_QUITTE_L_ASSOCIATION = PersonStatus.A_QUITTE_L_ASSOCIATION
    STATUS_DECEDE = PersonStatus.DECEDE

    ALLOCATIONSREGIME_UNKNOWN = AllocationsRegime.UNKNOWN
    ALLOCATIONSREGIME_GENERAL = AllocationsRegime.GENERAL
    ALLOCATIONSREGIME_MSA = AllocationsRegime.MSA
    ALLOCATIONSREGIME_OTHER = AllocationsRegime.OTHER

    TITLES = {
        PersonTitle.MONSIEUR: ('M.', 'Mr.'),
        PersonTitle.MADAME: ('Mme.',),
    }

    @classmethod
    def FullName(klass, *args, **kwargs):
        class Filter(_CleanText):
            __slots__ = ('_has_title',)

            def __init__(
                self,
                *args,
                has_title: _Optional[bool] = None,
                **kwargs,
            ):
                super().__init__(*args, **kwargs)
                self._has_title = has_title

            def __call__(self, item):
                full_name = super().__call__(item)

                if _empty(item.obj._has_title) or not _empty(self._has_title):
                    item.obj._has_title = self._has_title

                if isinstance(full_name, str):
                    full_name = full_name.strip()
                    if full_name == '(Sans nom)':
                        full_name = None

                return full_name

            def filter(self, text):  # noqa: A003
                return super().filter(text)

        return Filter(*args, **kwargs)

    iid = _IIDField('Person IID')
    type_ = _EnumField('Person type', PersonType)
    code = _StringField('Person code')
    status = _EnumField('Person status', PersonStatus)
    duplicate_of_id = _IIDField('IID of the duplicate person')

    _title = _EnumField('Person title (internal)', PersonTitle)

    @property
    def title(self):
        """Person civility title."""

        if not _empty(self._title):
            return self._title

        title, _, _, _ = self._full_name_components
        return title

    @title.setter
    def title(self, value):
        self._title = value

    title = _EnumField('Person title', PersonTitle)
    last_name = _StringField('Common name')
    first_name = _StringField('First name')

    full_name = _StringField('Full name')
    _has_title = _BoolField(
        'Whether full name has a title or not',
        default=None,
    )

    @property
    def _full_name_components(self):
        """Get the full name components.

        The result is available as a tuple of the following elements:

        * Deduced title, when available.
        * Deduced last name, when available.
        * Deduced first name, when available.
        * Deduced birth name, when available.
        """

        full_name = self.full_name
        if _empty(full_name):
            return _NotAvailable, _NotAvailable, _NotAvailable, _NotAvailable

        full_name = full_name.strip()
        if full_name == '(Sans nom)':
            return _NotAvailable, _NotAvailable, _NotAvailable, _NotAvailable

        # Get the birth name, if available.
        m = _re.match(r'([^\(\)]*)(?:\((.*)\))?', full_name)
        full_name, birth_name = m.groups()

        if birth_name is None:
            birth_name = _NotAvailable
        else:
            birth_name = birth_name.strip()

        # Get the title, if available.
        full_name = full_name.split()
        if not full_name:
            return _NotAvailable, _NotAvailable, _NotAvailable, birth_name

        title = _NotAvailable
        if self._has_title is not False:  # True or None
            title = ({
                value.casefold(): key
                for key, values in self.TITLES.items()
                for value in values
            }).get(full_name[0].casefold(), _NotAvailable)

            if not _empty(title):
                del full_name[0]

        # Get the first and last name.
        # We cannot determine with precision where the last name
        # stops and the first name starts; we suppose that the
        # last name covers everything except the first name.
        #
        # Note that if we already have the last or first name,
        # we use that to get the delimitation.
        last_name = self.last_name or _NotAvailable
        first_name = self.first_name or _NotAvailable
        if full_name:
            if (
                not _empty(last_name)
                and not _empty(first_name)
                and ' '.join(full_name) == ' '.join((
                    last_name, first_name,
                ))
            ):
                pass
            elif (
                not _empty(last_name)
                and last_name == ' '.join(
                    full_name[:len(last_name.split())],
                )
            ):
                first_name = ' '.join(
                    full_name[len(last_name.split()):],
                )
            elif (
                not _empty(first_name)
                and first_name == ' '.join(
                    full_name[len(first_name.split()):],
                )
            ):
                first_name = first_name
                last_name = ' '.join(
                    full_name[:len(first_name.split())],
                )
            elif len(full_name) == 1:
                last_name = full_name[0]
                first_name = ''
            else:
                last_name = ' '.join(full_name[:-1])
                first_name = full_name[-1]

        return title, last_name, first_name, birth_name

    @property
    def deduced_last_name(self):
        """Deduced last name from the full name, when available."""

        _, result, _, _ = self._full_name_components
        return result

    @property
    def deduced_first_name(self):
        """Deduced first name from the full name, when available."""

        _, _, result, _ = self._full_name_components
        return result

    _birth_name = _StringField('Birth name (internal)')

    @property
    def birth_name(self):
        """Birth name."""

        if not _empty(self._birth_name):
            return self._birth_name

        _, _, _, result = self._full_name_components
        return result

    @birth_name.setter
    def birth_name(self, value):
        self._birth_name = value

    birth_date = _Field('Date of birth', _date, _datetime)
    birth_place = _Field('Place of birth', BirthPlace)

    delegations = _Field('Person delegations amongst organization', list)
    function_start = _Field('Start of function', _date, _datetime)
    function_end = _Field('End of function', _date, _datetime)

    address = _Field('Adherent address', Address)
    npai = _BoolField("Doesn't live at given address")

    home_phone = _StringField('Home phone number')
    work_phone = _StringField('Office phone number')
    mobile_phone = _StringField('Mobile phone number')
    mobile_phone_2 = _StringField('Second mobile phone number')
    personal_email = _StringField('Personal email address')
    dedicated_email = _StringField('Dedicated email address')

    occupation = _StringField('Occupation (profession)')

    allocations_regime = _EnumField('Allocations regime', AllocationsRegime)
    allocations_code = _StringField('Code to the allocations regime')

    medical_intervention_rights = _BoolField(
        'Medical and chirurgical intervention rights have been granted',
    )
    image_rights = _BoolField('Image rights have been granted')
    information_rights = _BoolField('Information right have been granted')
    insured = _BoolField('Has a "chef de famille" insurance')

    ice_last_name = _StringField('Last name of ICE contact')
    ice_first_name = _StringField('First name of ICE contact')
    ice_phone = _StringField('Phone number for ICE contact')


class Delegation(_BaseObject):
    """Describe a secondary function."""

    person = _Field('Person', Person)
    structure = _Field('Structure', Structure)
    function = _Field('Function', Function)
    is_primary = _BoolField('Whether is the primary delegation')


class BankAccount(_BaseObject):
    """Describe a bank account."""

    title = _StringField('Bank account title')
    rib = _StringField('Bank account RIB')
    iban = _StringField('Bank account IBAN')
    bic = _StringField('Bank account BIC')
    rum = _StringField('Bank account RUM')

    structure = _Field('Bank account structure', Structure)


class InsuredGood(_BaseObject):
    """Describe an insured good ("bien")."""

    iid = _IIDField('Good IID')
    name = _StringField('Good name')
    structure = _Field('Structure associated to the good', Structure)
    owner = _Field('Good owner', Person)

# End of file.

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
"""Module definition."""

from copy import copy as _copy

from woob.tools.backend import (
    BackendConfig as _BackendConfig, Module as _Module,
)
from woob.tools.value import Value as _Value

__all__ = ['Module']


class _ModuleMeta(type):
    def __new__(mcls, clsname, superclasses, attributedict):
        values = {}

        # We do not want to read the CONFIG here, in order not to
        # get config values that have been deleted using "key = None",
        # i.e. inheritance to delete values.
        for key, value in attributedict.items():
            if isinstance(value, _Value):
                value = _copy(value)
                value.id = key
                values[key] = value

        # Insert the value copies.
        for value in values.values():
            attributedict[value.id] = value

        attributedict['CONFIG'] = _BackendConfig(*(values.values()))
        return super().__new__(mcls, clsname, superclasses, attributedict)


class Module(_Module, metaclass=_ModuleMeta):
    """Base class for modules within visyerres_sgdf_woob.

    TODO: Manage the mock browser.
    """

    VERSION = '3.1'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The fields have been copied in the CONFIG, we need to update the
        # values as indexed by the keys directly in order to make
        # uses like ``self.my_value.get()`` doable.
        for value in self.config.values():
            setattr(self, value.id, value)

# End of file.

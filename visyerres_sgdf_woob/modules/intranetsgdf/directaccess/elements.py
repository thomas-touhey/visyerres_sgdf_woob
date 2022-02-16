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
""" Useful elements for the intranetsgdf woob module. """

from typing import Optional as _Optional

from woob.browser.elements import TableElement as _TableElement
from woob.browser.filters.html import Link as _Link
from woob.browser.filters.standard import (
    CleanDecimal as _CleanDecimal, Regexp as _Regexp,
)

__all__ = ['PaginatedTableElement']


class PaginatedTableElement(_TableElement):
    """ Table element with pagination as the intranet likes to make it.

        :data table_name str: Name of the table with '$' in it.
                              Can usually be found in the page
                              Javascript links.
        :data is_postback bool: Whether we should use postback to access new
                                pages, or a simple submit.
        :data max_page int: Maximum page to reach, mainly used for debugging
                            purposes (e.g. debugging a page with lots of
                            elements).
    """

    table_name: str = None
    is_postback: bool = False
    max_page: _Optional[int] = None

    def __init__(self, *args, **kwargs):
        if not isinstance(self.table_name, str) or not self.table_name:
            raise ValueError('table_name should be set')

        super(PaginatedTableElement, self).__init__(*args, **kwargs)

    @property
    def table_xpath(self):
        return f'//table[@id="{self.table_name.replace("$", "_")}"]'

    @property
    def head_xpath(self):
        return f'{self.table_xpath}/tr[@class="entete"]/th'

    @property
    def item_xpath(self):
        return f'{self.table_xpath}/tr[starts-with(@class, "ligne")]'

    def next_page(self):
        current_page = _CleanDecimal.SI(
            f'{self.table_xpath}/tr[@class="pagination"]//span',
            default=None,
        )(self)
        last_page = _CleanDecimal.SI(
            _Regexp(
                _Link(
                    f'({self.table_xpath}/tr[@class="pagination"]'
                    '//a[contains(@href, "Page$")])[last()]',
                    default='',
                ),
                r'Page\$([0-9]+)',
                default=None,
            ),
            default=None,
        )(self)

        if not current_page or not last_page:
            return
        if current_page >= last_page:
            return
        if self.max_page is not None and current_page + 1 > self.max_page:
            return

        current_page = int(current_page)

        if self.is_postback:
            self.page.postback(
                target=self.table_name,
                argument=f'Page${current_page + 1}',
                scriptmanager=f'ctl00$_upMainContent|{self.table_name}',
            )
        else:
            self.page.submit(
                target=self.table_name,
                argument=f'Page${current_page + 1}',
            )

        return self.page.browser.page

# End of file.

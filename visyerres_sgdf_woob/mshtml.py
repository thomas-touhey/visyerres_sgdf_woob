#!/usr/bin/env python
# -*- coding: utf-8 -*-
# *****************************************************************************
# Copyright (C) 2017-2022 Thomas Touhey <thomas@touhey.fr>
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
""" HTML pages with support for Microsoft Ajax.

    This kind of pages is mainly used with websites built using the
    ASP.NET framework, such as the SGDF intranet.
"""

import os.path as _path

import re as _re
from io import StringIO as _StringIO
from os import environ as _environ, listdir as _listdir

from lxml.etree import (
    Element as _Element, XMLSyntaxError as _XMLSyntaxError,
    tostring as _html_to_str,
)
from lxml.html import HTMLParser as _HTMLParser, parse as _parse_html
from requests import Request as _Request
from weboob.browser.pages import HTMLPage as _HTMLPage
from weboob.exceptions import (
    BrowserHTTPError as _BrowserHTTPError, BrowserRedirect as _BrowserRedirect,
)
from weboob.tools.compat import unquote as _unquote, urljoin as _urljoin

__all__ = ['MSHTMLPage']


def _listrepr(x):
    """ Represent a list in a short fashion, for easy representation. """

    try:
        len(x)
    except TypeError:
        return None
    else:
        return '<%d element%s>' % (len(x), 's'[:len(x) >= 2])


class _MicrosoftAjaxResponseParsingError(Exception):
    """ A Microsoft Ajax call has resulted in an error. """

    __slots__ = ('_column', '_description')

    def __init__(self, column, description):
        self.column = column
        self.description = description

    def __str__(self):
        return 'at column %d: %s' % (self.column, self.description)


class MicrosoftAjaxResponse:
    """ Response to a Microsoft Ajax call.

        Re-implements the same concepts as ``_parseDelta`` in
        the reference implementation.
    """

    __slots__ = (
        '_version', '_redirectUrl', '_error', '_pageTitle', '_focus',
        '_updatePanelNodes', '_hiddenFieldNodes',
        '_arrayDeclarationNodes', '_scriptBlockNodes', '_scriptStartupNodes',
        '_expandoNodes', '_onSubmitNodes', '_dataItemNodes',
        '_dataItemJsonNodes', '_scriptDisposeNodes',
        '_asyncPostBackControlIDsNode', '_postBackControlIDsNode',
        '_updatePanelIDsNode', '_asyncPostBackTimeoutNode',
        '_childUpdatePanelIDsNode', '_panelsToRefreshNode', '_formActionNode',
    )

    __srepr__ = {
        '_updatePanelNodes': _listrepr,
        '_hiddenFieldNodes': _listrepr,
        '_arrayDeclarationNodes': _listrepr,
        '_scriptBlockNodes': _listrepr,
        '_scriptStartupNodes': _listrepr,
        '_expandoNodes': _listrepr,
        '_onSubmitNodes': _listrepr,
        '_dataItemNodes': _listrepr,
        '_dataItemJsonNodes': _listrepr,
        '_scriptDisposeNodes': _listrepr,
    }

    def __init__(
        self,
        version=None,
        updatePanelNodes=(),
        hiddenFieldNodes=(),
        arrayDeclarationNodes=(),
        scriptBlockNodes=(),
        scriptStartupNodes=(),
        expandoNodes=(),
        onSubmitNodes=(),
        dataItemNodes=(),
        dataItemJsonNodes=(),
        scriptDisposeNodes=(),
        asyncPostBackControlIDsNode=None,
        postBackControlIDsNode=None,
        updatePanelIDsNode=None,
        asyncPostBackTimeoutNode=None,
        childUpdatePanelIDsNode=None,
        panelsToRefreshNode=None,
        formActionNode=None,
        redirectUrl=None,
        error=None,
        pageTitle=None,
        focus=None,
    ):
        self._version = version
        self._updatePanelNodes = updatePanelNodes
        self._hiddenFieldNodes = hiddenFieldNodes
        self._arrayDeclarationNodes = arrayDeclarationNodes
        self._scriptBlockNodes = scriptBlockNodes
        self._scriptStartupNodes = scriptStartupNodes
        self._expandoNodes = expandoNodes
        self._onSubmitNodes = onSubmitNodes
        self._dataItemNodes = dataItemNodes
        self._dataItemJsonNodes = dataItemJsonNodes
        self._scriptDisposeNodes = scriptDisposeNodes
        self._asyncPostBackControlIDsNode = asyncPostBackControlIDsNode
        self._postBackControlIDsNode = postBackControlIDsNode
        self._updatePanelIDsNode = updatePanelIDsNode
        self._asyncPostBackTimeoutNode = asyncPostBackTimeoutNode
        self._childUpdatePanelIDsNode = childUpdatePanelIDsNode
        self._panelsToRefreshNode = panelsToRefreshNode
        self._formActionNode = formActionNode
        self._redirectUrl = redirectUrl
        self._error = error
        self._pageTitle = pageTitle
        self._focus = focus

    def __repr__(self):
        args = ', '.join(
            '%s=%s' % (
                x[1:],
                self.__class__.__srepr__.get(x, repr)(getattr(self, x)),
            )
            for x in self.__class__.__slots__ if getattr(self, x)
        )

        return '%s(%s)' % (self.__class__.__name__, args)

    @property
    def version(self):
        """ ASP.NET server-side version. """

        return self._version

    @property
    def version4(self):
        """ Get if ASP.NET server-side version is 4 or above. """

        return self._version is not None and self._version >= 4

    @property
    def errorCode(self):
        """ Get the error code, if any. """

        return self._error[0] if self._error else None

    @property
    def errorMessage(self):
        """ Get the error message, if any. """

        return self._error[1] if self._error else None

    @property
    def redirectUrl(self):
        """ Get the redirect URL, if any. """

        return self._redirectUrl

    @property
    def updatePanelNodes(self):
        """ Update panel nodes. """

        return self._updatePanelNodes

    @property
    def hiddenFieldNodes(self):
        """ Hidden field nodes. """

        return self._hiddenFieldNodes

    @property
    def scriptBlockNodes(self):
        """ Script block nodes. """

        return self._scriptBlockNodes

    @classmethod
    def fromtext(cls, text):
        return cls.fromstream(_StringIO(text))

    @classmethod
    def fromstream(cls, stream):
        """ Get a Microsoft Ajax response from a text stream. """

        version = None
        redirectUrl = None
        error = None
        pageTitle = None
        focus = None
        updatePanelNodes = []
        hiddenFieldNodes = []
        arrayDeclarationNodes = []
        scriptBlockNodes = []
        scriptStartupNodes = []
        expandoNodes = []
        onSubmitNodes = []
        asyncPostBackControlIDsNode = None
        postBackControlIDsNode = None
        updatePanelIDsNode = None
        asyncPostBackTimeoutNode = None
        childUpdatePanelIDsNode = None
        panelsToRefreshIDsNode = None
        formActionNode = None
        dataItemNodes = []
        dataItemJsonNodes = []
        scriptDisposeNodes = []

        # Utilitaires.

        def parseinvariantnumber(x):
            """ Equivalent of ``Number.parseInvariant``.

                Implemented here for compatibility reasons.
            """

            x = x.strip()
            if x == '+infinity':
                return float('+inf')
            elif x == '-infinity':
                return float('-inf')
            elif x[:2] == '0x':
                try:
                    return int(x[2:], 16)
                except (TypeError, ValueError):
                    pass

            try:
                x = float(x)
            except ValueError:
                return float('nan')

            if x == int(x):
                x = int(x)
            return x

        # Main reading loop.
        #
        # Note that this algorithm is greedy; if the caller has to
        # read something after this response, it must provide us with
        # a limited input stream.

        buf = ''
        column = 1

        while True:
            # We want to read a new node from here.

            lastoffset = -1
            left = 3

            while left:
                newoffset = buf.find('|', lastoffset + 1)
                if newoffset < 0:
                    break

                lastoffset = newoffset
                left -= 1

            if left:
                newchars = stream.read(512)
                if not newchars:
                    # There might be an EOL at the end of the stream,
                    # we should ignore it. This case also manages an
                    # empty end of stream (buf == ''), not anomalous.

                    if all(c in ('\n', '\r') for c in buf):
                        break
                    raise _MicrosoftAjaxResponseParsingError(
                        column, 'unterminated response')

                buf += newchars
                continue

            # We have the three initial fields, we will be able to read
            # them. Then, we complete the content with what we just read,
            # and we set up the buffer correctly for the next field.
            #
            # Note that the reference implementation requires the final
            # '|' even on the last node, whereas we can just have an end
            # of file here.

            clength, ctype, cname = buf[:lastoffset].split('|')
            type_column = column + buf.find('|') + 1

            buf = buf[lastoffset + 1:]
            column += lastoffset + 1

            try:
                clength = int(clength)
            except ValueError:
                raise _MicrosoftAjaxResponseParsingError(
                    column + 1,
                    'invalid content length %r' % clength,
                )
            if clength < 0:
                raise _MicrosoftAjaxResponseParsingError(
                    column + 1,
                    'invalid content length %r' % clength,
                )

            if len(buf) < clength + 1:
                buf += stream.read(clength + 1 - len(buf))
                if len(buf) < clength:
                    raise _MicrosoftAjaxResponseParsingError(
                        column, (
                            'premature end of stream, could only read '
                            '%d/%d utf-8 characters' % (len(buf), clength)
                        ))

            if buf[clength:clength + 1] not in ('', '|'):
                raise _MicrosoftAjaxResponseParsingError(
                    column + clength, (
                        "expected '|' or end of stream at end of content, "
                        'got %r' % buf[clength:clength + 1],
                    ),
                )

            content = buf[:clength]
            buf = buf[clength + 1:]
            column += clength + 1

            # We add the field where it needs to be.

            if ctype == '#':
                version = float(content)
            elif ctype == 'pageRedirect':
                # The reference implementation redirects directly when
                # this URL is read; to emulate this behaviour, we do not
                # replace the existing redirection URL if already
                # set.

                if redirectUrl is None:
                    if version is not None and version >= 4:
                        content = _unquote(content)
                    redirectUrl = content
            elif ctype == 'error':
                if error is None:
                    error = (parseinvariantnumber(cname), content)
            elif ctype == 'pageTitle':
                pageTitle = content
            elif ctype == 'focus':
                focus = content
            elif ctype == 'updatePanel':
                updatePanelNodes.append((cname, content))
            elif ctype == 'hiddenField':
                hiddenFieldNodes.append((cname, content))
            elif ctype == 'arrayDeclaration':
                arrayDeclarationNodes.append((cname, content))
            elif ctype == 'scriptBlock':
                scriptBlockNodes.append((cname, [content]))
            elif ctype == 'fallbackScript':
                try:
                    scriptPaths = scriptBlockNodes[-1][1]
                except KeyError:
                    pass
                else:
                    scriptPaths.append(content)
            elif ctype == 'scriptStartupBlock':
                scriptStartupNodes.append((cname, content))
            elif ctype == 'expando':
                expandoNodes.append((cname, content))
            elif ctype == 'onSubmit':
                onSubmitNodes.append((cname, content))
            elif ctype == 'asyncPostBackControlIDs':
                asyncPostBackControlIDsNode = (cname, content)
            elif ctype == 'postBackControlIDs':
                postBackControlIDsNode = (cname, content)
            elif ctype == 'updatePanelIDs':
                updatePanelIDsNode = (cname, content)
            elif ctype == 'asyncPostBackTimeout':
                asyncPostBackTimeoutNode = (cname, content)
            elif ctype == 'childUpdatePanelIDs':
                childUpdatePanelIDsNode = (cname, content)
            elif ctype == 'panelsToRefreshIDs':
                panelsToRefreshIDsNode = (cname, content)
            elif ctype == 'formAction':
                formActionNode = (cname, content)
            elif ctype == 'dataItem':
                dataItemNodes.append((cname, content))
            elif ctype == 'dataItemJson':
                dataItemJsonNodes.append((cname, content))
            elif ctype == 'scriptDispose':
                scriptDisposeNodes.append((cname, content))
            else:
                raise _MicrosoftAjaxResponseParsingError(
                    type_column, 'unknown ajax fragment type %r' % ctype,
                )

        return cls(
            version=version,
            redirectUrl=redirectUrl,
            error=error,
            pageTitle=pageTitle,
            focus=focus,
            updatePanelNodes=updatePanelNodes,
            hiddenFieldNodes=hiddenFieldNodes,
            arrayDeclarationNodes=arrayDeclarationNodes,
            scriptBlockNodes=scriptBlockNodes,
            scriptStartupNodes=scriptStartupNodes,
            expandoNodes=expandoNodes,
            onSubmitNodes=onSubmitNodes,
            asyncPostBackControlIDsNode=asyncPostBackControlIDsNode,
            postBackControlIDsNode=postBackControlIDsNode,
            updatePanelIDsNode=updatePanelIDsNode,
            asyncPostBackTimeoutNode=asyncPostBackTimeoutNode,
            childUpdatePanelIDsNode=childUpdatePanelIDsNode,
            panelsToRefreshNode=panelsToRefreshIDsNode,
            formActionNode=formActionNode,
            dataItemNodes=dataItemNodes,
            dataItemJsonNodes=dataItemJsonNodes,
            scriptDisposeNodes=scriptDisposeNodes,
        )


class MSHTMLPage(_HTMLPage):
    """ Represents an HTML page as used on the SGDF intranet.

        All such pages act as a global form on which operations are executed.
    """

    __slots__ = ('_scriptmanagerid', '_formid')

    def __setitem__(self, key, value):
        """ Sets the control with the given name at the given value.

            This method behaves differently depending on the control type:

            * If the control is a simple text input, we edit the ``value``
              attribute.
            * If the control is a checkbox or a radio button, we check it
              by defining the ``checked`` attribute.
            * If the control is a combobox (``<select>``), we remove
              ``selected`` from all attributes then we check the option
              whose ``value`` attribute is given; if such an option isn't
              found, we add it to the list.
        """

        if not isinstance(key, str):
            raise TypeError('form key should be a string, is %r' % key)
        if not isinstance(value, str):
            raise TypeError('form value should be a string, is %r' % value)

        form = self.form
        try:
            c = form.xpath('//*[@name=$id_]', id_=key)[0]
        except IndexError:
            new_hidden_field = _Element('input')
            new_hidden_field.attrib['type'] = 'hidden'
            new_hidden_field.attrib['name'] = key
            new_hidden_field.attrib['value'] = value

            form.append(new_hidden_field)
        else:
            if c.tag == 'select':
                value_found = False

                for opt in c.xpath('./option'):
                    if opt.get('value') == value:
                        opt.attrib['selected'] = 'selected'
                        value_found = True
                    elif 'selected' in opt.attrib:
                        del opt.attrib['selected']

                if not value_found:
                    new_option = _Element('option')
                    new_option.attrib['value'] = value
                    new_option.attrib['selected'] = 'selected'

                    c.append(new_option)
            elif c.tag == 'input' and c.get('type') in ('checkbox', 'radio'):
                if value:
                    c.attrib['checked'] = 'checked'
                elif 'checked' in c.attrib:
                    del c['checked']
            else:
                c.attrib['value'] = value

    @property
    def form(self):
        """ Get the form element. """

        if self._formid is not None:
            return self.doc.xpath('//form[@id=$id_]', id_=self._formid)[0]

        return self.doc.xpath('//form')[0]

    def build_doc(self, content):
        """ Build structured data. """

        doc = super(MSHTMLPage, self).build_doc(content)

        self._scriptmanagerid = None
        self._formid = None

        for result in doc.xpath(
            '//script[contains(text(), '
            '"WebForms.PageRequestManager._initialize")]',
        ):
            try:
                m = next(_re.finditer(
                    r'WebForms\.PageRequestManager\._initialize'
                    r"\(('([^']*)'|\"([^\"])*\"),\s+('([^']*)'|\"([^\"])*\")",
                    result.text,
                ))
            except StopIteration:
                continue

            s1 = m.group(2)
            s2 = m.group(3)
            f1 = m.group(5)
            f2 = m.group(6)

            self._scriptmanagerid = s1 or s2
            self._formid = f1 or f2

            break

        return doc

    def xpath(self, *args, **kwargs):
        """ Get the elements through the xpath relative to the document. """

        return self.doc.xpath(*args, **kwargs)

    def request(self, target, argument='', button_id=''):
        """ Make the Request out of the current page. """

        form = self.form

        url = _urljoin(
            self.browser.url,
            form.attrib.get('action', ''),
        )
        method = form.attrib.get('method', 'POST')

        # Explore form tags in search for form data.

        fields = {}
        files = {}

        for inp in form.xpath('.//input | .//select'):
            value = None
            if inp.attrib.get('disabled'):
                continue

            try:
                name = inp.attrib['name']
            except KeyError:
                continue

            if inp.tag == 'select':
                defvalue = None
                for opt in inp.xpath('.//option'):
                    optvalue = opt.attrib.get('value', opt.text)
                    optsel = opt.attrib.get('selected') == 'selected'

                    if optsel:
                        value = optvalue
                        break

                    if defvalue is None:
                        defvalue = optvalue

                if value is None:
                    value = defvalue
                fields[name] = value
                continue

            try:
                typ = inp.attrib['type']
            except KeyError:
                continue

            if typ in ('checkbox', 'radio'):
                if inp.attrib.get('checked'):
                    value = inp.attrib.get('value', 'on')
                elif name in fields:
                    continue
            elif typ == 'file':
                files[name] = ('', inp.attrib.get('value', b''))
                continue
            elif typ == 'submit':
                if not button_id or inp.attrib.get('id') != button_id:
                    continue
                value = inp.attrib.get('value') or ''
            elif typ != 'submit':
                value = inp.attrib.get('value') or ''

            fields[name] = value

        fields['__EVENTTARGET'] = target or ''
        fields['__EVENTARGUMENT'] = argument or ''
        fields['__LASTFOCUS'] = ''

        if '_eo_js_modules' in fields:
            fields['_eo_js_modules'] = ''
        if '_eo_obj_inst' in fields:
            fields['_eo_obj_inst'] = ''

        # Prepare the request.

        return _Request(
            url=url,
            method=method,
            data=fields,
        )

    def postback(self, target='', argument='', scriptmanager=None):
        """ Makes an AJAX call on the page.

            Updates the document depending on the answer.
        """

        browser = self.browser

        request = self.request(target, argument)
        request.data[self._scriptmanagerid] = scriptmanager
        request.data['__ASYNCPOST'] = 'true'
        request.headers['Cache-Control'] = 'no-cache'
        request.headers['X-MicrosoftAjax'] = 'Delta=true'
        request.headers['X-Requested-With'] = 'XMLHttpRequest'

        response = browser.open(request)
        ajax = MicrosoftAjaxResponse.fromtext(response.text)

        if ajax.errorCode is not None:
            raise _BrowserHTTPError(
                '%s%s' % (
                    ajax.errorCode,
                    ' ' + ajax.errorMessage if ajax.errorMessage else '',
                ),
            )

        if ajax.redirectUrl is not None:
            raise _BrowserRedirect(ajax.redirectUrl)

        for name, content in ajax.updatePanelNodes:
            if not content.strip():
                continue

            elements = self.doc.xpath('//*[@id=$id_]', id_=name)
            if len(elements) != 1:
                continue

            element = elements[0]

            try:
                fragment = _parse_html(
                    _StringIO('<html><body>%s</body></html>' % content),
                    _HTMLParser(),
                )
            except _XMLSyntaxError:
                continue
            else:
                # Get the <body> tag.

                fragment = fragment.getroot()[0]

            for child in element:
                element.remove(child)

            element.text = fragment.text
            for child in fragment:
                element.append(child)

        for name, content in ajax.hiddenFieldNodes:
            self[name] = content

        # We ought to save the response if necessary for quick debugging.

        if (
            browser.save_response in browser.session.hooks['response']
            and _environ.get('WOOB_USE_OBSOLETE_RESPONSES_DIR') == '1'
        ):
            result_path = _path.join(browser.responses_dirname, max(
                x for x in _listdir(browser.responses_dirname)
                if x.endswith('-request.txt')
            )[:-12] + '-updated.html')

            with open(result_path, 'wb+') as result_file:
                result_file.write(_html_to_str(self.doc))

            browser.logger.info('Result saved to %s' % result_path)

    def submit(self, target='', argument='', button_id=None):
        """ Réalise un appel POST sur la page en soumettant le formulaire. """

        return self.browser.location(self.request(
            target,
            argument,
            button_id,
        ))

# End of file.

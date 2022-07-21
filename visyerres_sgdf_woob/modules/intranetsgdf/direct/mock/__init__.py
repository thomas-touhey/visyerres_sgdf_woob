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
"""WSGI application mocking the intranet."""

from urllib.parse import urlencode as _urlencode, urlparse as _urlparse

from flask import (
    Flask as _Flask, redirect as _redirect, render_template as _template,
    request as _r,
)
from flask.wrappers import Request as _BaseRequest

__all__ = ['app']


class GenericException(Exception):
    # Raised when the intranet does not give any details on what went wrong.
    pass


class _Request(_BaseRequest):
    """Base request class for intranetsgdf mock."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The real intranet does not make the difference between upper-case
        # and lower-case, we want to emulate this by casefolding here.
        path = self.path.casefold()

        # The real intranet probably has a rule at server-level that
        # produces duplicate content with and without the prefix.
        #
        # In order to manage both in a simple fashion, we simply
        # remove the prefix once when we see it.
        #
        # NOTE: If the URL is exactly /Specialisation/Sgdf, it seems to
        #       trigger an error since there is a redirect from
        #       / to /Default.aspx but not from /Specialisation/Sgdf/ to
        #       /Specialisation/Sgdf/Default.aspx, so we need to keep it.
        if (
            path.startswith('/specialisation/sgdf')
            and path not in (
                '/specialisation/sgdf',
                '/specialisation/sgdf/',
            )
        ):
            path = path[20:]

        self.path = path or '/'
        self.environ['PATH_INFO'] = path or '/'


app = _Flask(__name__)
app.request_class = _Request

# ---
# Error management.
# ---


@app.errorhandler(GenericException)
def redirect_to_generic_error(exc):
    parsed_url = _urlparse(_urlparse(_r.url).path)
    parsed_url = parsed_url._replace(
        path='/Specialisation/Sgdf/erreurs/Erreur.aspx',
        query=_urlencode({'aspxerrorpath': parsed_url.path}, doseq=True),
    )

    return _redirect(parsed_url.geturl())


@app.errorhandler(404)
def not_found(exc):
    return _template('NotFound.html')


@app.route('/erreurs/erreur.aspx')
def generic_error():
    return _template('ErreurInconnue.html')


@app.route('/specialisation/sgdf')
@app.route('/specialisation/sgdf/')
def no_redirect():
    raise GenericException()


# ---
# Login management.
# ---


@app.route('/')
def redirect_to_login():
    return _redirect('/Specialisation/Sgdf/Default.aspx')


@app.route('/default.aspx', methods=['GET', 'POST'])
def default():
    """Login and forgot password options."""

    if _r.method == 'GET':
        return _template('Default.html')

    raise NotImplementedError

# End of file.

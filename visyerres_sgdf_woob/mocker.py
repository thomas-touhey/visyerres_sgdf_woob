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
""" Tools for mocking a website for unit testing without actual access.

    The website can be defined using a WSGI application implementing PEP 3333.
"""

from http.client import HTTPResponse as _HTTPResponse
from io import BytesIO as _BytesIO
from sys import stderr as _stderr
from urllib.parse import urlparse as _urlparse
from wsgiref.handlers import SimpleHandler as _SimpleWSGIHandler

from responses import (
    BaseResponse as _BaseResponse, RequestsMock as _RequestsMock,
)

from .version import version as _version

__all__ = ['RequestsMock', 'WSGIResponse']


class WSGIHandler(_SimpleWSGIHandler):
    """ Represents a WSGI request handler. """

    __slots__ = ('_request',)

    def __init__(self, request):
        self._request = request

        body = request.body or b''
        if isinstance(body, str):
            body = body.encode('utf-8')

        super().__init__(
            stdin=_BytesIO(body),
            stdout=_BytesIO(),
            stderr=_stderr,
            environ=self.get_environ(),
            multithread=False,
            multiprocess=False,
        )

    def get_environ(self):
        """ Get the CGI environment for the given request. """

        request = self._request

        # Get the base URL information.

        parsed_url = _urlparse(request.url)
        scheme, netloc = parsed_url.scheme, parsed_url.netloc
        scheme, netloc = scheme.casefold(), netloc.casefold()

        netloc_components = parsed_url.netloc.split(':')
        if len(netloc_components) == 2:
            netloc, port = netloc_components
            port = int(port)
        elif scheme == 'http':
            port = 80
        elif scheme == 'https':
            port = 443
        else:
            raise AssertionError(f'unknown port number for scheme {scheme!r}')

        environ = {
            'GATEWAY_INTERFACE': 'CGI/1.1',
            'SERVER_SOFTWARE': f'WoobRequestsMocker/{_version}',
            'SCRIPT_NAME': '',

            'SERVER_PROTOCOL': 'HTTP/1.1',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': f'{port}',
            'REMOTE_HOST': '127.0.0.1',

            'REQUEST_METHOD': request.method,
            'PATH_INFO': parsed_url.path,
            'QUERY_STRING': parsed_url.query,
        }

        if request.body is not None:
            environ['CONTENT_TYPE'] = request.headers.get(
                'Content-Type',
                'text/plain',
            )
            environ['CONTENT_LENGTH'] = request.headers.get(
                'Content-Length',
                str(len(request.body)),
            )

        for header_name, header_value in request.headers.items():
            environ[f'HTTP_{header_name}'] = header_value

        return environ


class WSGIResponse(_BaseResponse):
    """ Represents a WSGI response for the RequestsMocker registry. """

    __slots__ = ('_appclass', '_scheme', '_netloc')

    _appclass: object
    _scheme: str
    _netloc: str

    def __init__(self, url: str, app: object):
        super().__init__('GET', url)

        self._scheme, self._netloc = self._get_scheme_and_netloc(url)
        self._appclass = app

        # We want to avoid triggering the assertion error for
        # WSGI responses.
        self.call_count += 1

    def matches(self, request):
        """ Check if the current response should match the request. """

        scheme, netloc = self._get_scheme_and_netloc(request.url)
        if (scheme, netloc) != (self._scheme, self._netloc):
            return False, 'Base URL does not match'

        return True, ''

    def get_response(self, request):
        """ Get the response associated with the request. """

        handler = WSGIHandler(request)
        handler.run(self._appclass)
        handler.stdout.seek(0)

        class Socket:
            """ Some kind of socket override.

                Not a very elegant solution, but HTTPResponse expects
                a socket instead of a file stream directly;
                this is the solution I've settled with.
            """

            def makefile(*args, **kwargs):
                return handler.stdout

        response = _HTTPResponse(Socket())
        response.begin()

        return response

    @staticmethod
    def _get_scheme_and_netloc(url: str):
        """ Get the scheme and net location of the given URL. """

        parsed_url = _urlparse(url)
        scheme, netloc = parsed_url.scheme, parsed_url.netloc
        scheme, netloc = scheme.casefold(), netloc.casefold()

        # netloc can contain the port number, e.g. 'example.org:443'.
        # If the given port number is the standard port for the scheme,
        # we ought to remove it.

        netloc_components = parsed_url.netloc.split(':')
        if len(netloc_components) == 2:
            new_netloc, port = netloc_components
            if (
                (scheme == 'http' and port == '80')
                or (scheme == 'https' and port == '443')
            ):
                netloc = new_netloc

        return scheme, netloc


class RequestsMock(_RequestsMock):
    """ Requests mocker. """

    def add_wsgi(self, url: str, app: object):
        """ Add a WSGI application implementing PEP 3333 to the mocker.

            This is mostly useful when mocking complex applications, or
            applications with states.

            An example of this using Flask is the following:

            .. code-block:: python

                from flask import Flask
                import requests
                from visyerres_sgdf_woob.mocker import RequestsMocker

                app = Flask()

                @app.route('/hello/world')
                def hello_world():
                    return 'hello, world'

                with RequestsMocker() as responses:
                    responses.add_wsgi('https://example.org', app)

                    resp = requests.get('https://example.org/hello/world')
                    print('status code:', resp.status_code)
                    print('text:', resp.text)
        """

        self.add(WSGIResponse(url, app))

# End of file.

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
""" intranetsgdf module definition.

    This module is used for interacting with the SGDF intranet, a derivative
    of the Intrassoc solution by Supralog edited and hosted by the same vendor.
    It is used by all associations to manage both the organization itself
    through defining people and related statuses, and provides a few
    ACM (Accueil Collectif de Mineurs) management tools such as an
    attendance registry, an event organizer, and insurance-related interfaces.

    Although the intranet used to manage camps and declarations, it has moved
    to monprojet for a few years now.
"""

from .module import IntranetSGDFModule

__all__ = ['IntranetSGDFModule']

# End of file.

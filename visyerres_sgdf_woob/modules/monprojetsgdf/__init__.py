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
""" monprojetsgdf module definition.

    This module is used for interacting with monprojet.sgdf.fr, which is
    the main platform that interacts with the public department that manages
    ACMs (Accueil Collectif de Mineurs) [1] through their TAM platform [2].

    It is used for making declarations for the year amongst a group and
    the camps. It gathers data from the intranet in order to function.

    [1] This department is one of the french department, and is a subsidiary
        of the Ministère de l'Éducation Nationale, de la Jeunesse et des
        Sports.

        It has beared multiple names over the years, and can have a different
        name between departements. Some names in use or used are the following:

        * Jeunesse & Sport (J&S, JS), the historic name for such a department.
        * Direction Départementale de la Jeunesse et des Sports (DDJS).
        * Direction Départementale de la Cohésion Sociale (DDCS).
        * Direction Départementale de l'Emploi, du Travail et de la
          Solidarité (DDETS).
    [2] Téléprocédure des Accueils de Mineurs, accessible through the
        following URL: https://tam.extranet.jeunesse-sports.gouv.fr/
"""

from .module import MonProjetSGDFModule

__all__ = ['MonProjetSGDFModule']

# End of file.

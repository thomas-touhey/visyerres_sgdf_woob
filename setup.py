#!/usr/bin/env python3
# *****************************************************************************
# Copyright (C) 2022 Thomas "Cakeisalie5" Touhey <thomas@touhey.fr>
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
""" Setup script for the visyerres_sgdf_woob Python package and script. """

import os.path as _path
from setuptools import setup as _setup

requirements = set()
with open(_path.join(_path.dirname(__file__), 'requirements.txt'), 'r') as f:
    requirements.update(f.read().splitlines())

_setup(
    install_requires=sorted(filter(lambda x: x, requirements)),
)

# End of file.

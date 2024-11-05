#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015-2023 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys

import sys

try:
    import matplotlib
except ImportError:
    raise ImportError(
        'Matplotlib seems to be missing. Needed for plotting support')
else:
    # Set a stable backend compatible with Streamlit and non-GUI environments
    touse = 'Agg'  # Use the non-interactive 'Agg' backend on all platforms
    try:
        matplotlib.use(touse)
    except:
        # If another backend has already been loaded, this exception can be ignored
        pass

from .plot import Plot, Plot_OldSync
from .scheme import PlotScheme
# try:
#     import matplotlib
# except ImportError:
#     raise ImportError(
#         'Matplotlib seems to be missing. Needed for plotting support')
# else:
#     touse = 'TKAgg' if sys.platform != 'darwin' else 'MacOSX'
#     try:
#         matplotlib.use(touse)
#     except:
#         # if another backend has already been loaded, an exception will be
#         # generated and this can be skipped
#         pass


# from .plot import Plot, Plot_OldSync
# from .scheme import PlotScheme

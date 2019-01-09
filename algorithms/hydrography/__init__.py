# -*- coding: utf-8 -*-

"""
Hydrography Algorithms

***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from .AggregateLineSegments import AggregateLineSegments
from .LengthOrder import LengthOrder
from .NetworkNodes import NetworkNodes
from .SelectConnectedComponents import SelectConnectedComponents
from .StrahlerOrder import StrahlerOrder

def hydrography_algorithms():

    return [
        AggregateLineSegments(),
        LengthOrder(),
        NetworkNodes(),
        SelectConnectedComponents(),
        StrahlerOrder()
    ]

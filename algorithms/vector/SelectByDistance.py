# -*- coding: utf-8 -*-

"""
***************************************************************************
    SelectByDistance.py
    ---------------------
    Date                 : November 2016
    Copyright            : (C) 2016 by Christophe Rousson
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Christophe Rousson'
__date__ = 'November 2016'
__copyright__ = '(C) 2016, Christophe Rousson'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.core import QGis, QgsFeature, QgsGeometry, QgsPoint, QgsSpatialIndex, QgsFields, QgsField, QgsWKBTypes
from qgis.core import QgsVectorLayer
from qgis.core import QgsFeatureRequest, QgsExpression
from PyQt4.QtCore import QVariant
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterVector
from processing.core.parameters import ParameterNumber
from processing.core.parameters import ParameterTableField
from processing.core.outputs import OutputVector
from processing.tools import dataobjects, vector
from processing.core.ProcessingLog import ProcessingLog
from math import sqrt

class SelectByDistance(GeoAlgorithm):

    TARGET_LAYER = 'TARGET_LAYER'
    DISTANCE_TO_LAYER = 'DISTANCE_TO_LAYER'
    DISTANCE = 'DISTANCE'

    def defineCharacteristics(self):

        self.name, self.i18n_name = self.trAlgorithm('Select By Distance')
        self.group, self.i18n_group = self.trAlgorithm('Tools for Vectors')

        self.addParameter(ParameterVector(self.TARGET_LAYER,
                                          self.tr('Select From Layer'), [ParameterVector.VECTOR_TYPE_ANY]))
        self.addParameter(ParameterVector(self.DISTANCE_TO_LAYER,
                                          self.tr('Distance To Layer'), [ParameterVector.VECTOR_TYPE_ANY]))
        self.addParameter(ParameterNumber(self.DISTANCE,
                                          self.tr('Max Distance'),
                                          optional=False, default=0.0, minValue=0.0))

    def processAlgorithm(self, progress):

        target_layer = dataobjects.getObjectFromUri(self.getParameterValue(self.TARGET_LAYER))
        distance_layer = dataobjects.getObjectFromUri(self.getParameterValue(self.DISTANCE_TO_LAYER))
        distance = self.getParameterValue(self.DISTANCE)

        spatial_index = QgsSpatialIndex(distance_layer.getFeatures())

        total = 100.0 / target_layer.featureCount()
        selection = set()

        for current, feature in enumerate(target_layer.getFeatures()):
            
            search_box = feature.geometry().boundingBox()
            search_box.grow(distance)
            
            for candid in spatial_index.intersects(search_box):

                candidate = distance_layer.getFeatures(QgsFeatureRequest(candid)).next()

                if (feature.geometry().distance(candidate.geometry())) <= distance:
                    selection.add(feature.id())
                    break

            progress.setPercentage(int(current * total))

        target_layer.setSelectedFeatures(list(selection))
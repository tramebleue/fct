# -*- coding: utf-8 -*-

"""
***************************************************************************
    SegmentEndpoints.py
    ---------------------
    Date                 : February 2018
    Copyright            : (C) 2018 by Christophe Rousson
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
__date__ = 'February 2018'
__copyright__ = '(C) 2018, Christophe Rousson'

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

from ...core import vector as vector_helper

class SegmentEndpoints(GeoAlgorithm):

    INPUT_LAYER = 'INPUT'
    OUTPUT_LAYER = 'OUTPUT'

    def defineCharacteristics(self):

        self.name, self.i18n_name = self.trAlgorithm('Segment Endpoints')
        self.group, self.i18n_group = self.trAlgorithm('Tools for Vectors')

        self.addParameter(ParameterVector(self.INPUT_LAYER,
                                          self.tr('Segments'), [ParameterVector.VECTOR_TYPE_LINE]))

        self.addOutput(OutputVector(self.OUTPUT_LAYER, self.tr('Endpoints')))

    def processAlgorithm(self, progress):

        layer = dataobjects.getObjectFromUri(self.getParameterValue(self.INPUT_LAYER))

        writer = self.getOutputFromName(self.OUTPUT_LAYER).getVectorWriter(
            vector_helper.createUniqueFieldsList(
                layer,
                QgsField('TYPE', QVariant.String, len=5)
            ),
            QGis.WKBPoint,
            layer.crs())
        total = 100.0 / layer.featureCount()

        for current, feature in enumerate(layer.getFeatures()):

            geom = feature.geometry()
            startpoint = geom.interpolate(0.0)
            endpoint   = geom.interpolate(geom.length())
            
            outfeature = QgsFeature()
            outfeature.setGeometry(startpoint)
            outfeature.setAttributes(feature.attributes() + [ 'START' ])
            writer.addFeature(outfeature)

            outfeature = QgsFeature()
            outfeature.setGeometry(endpoint)
            outfeature.setAttributes(feature.attributes() + [ 'END' ])
            writer.addFeature(outfeature)             

            progress.setPercentage(int(current * total))
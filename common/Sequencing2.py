# -*- coding: utf-8 -*-

"""
***************************************************************************
    Sequencing2.py
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

from qgis.core import QGis, QgsFeature, QgsGeometry, QgsPoint, QgsSpatialIndex, QgsFeatureRequest, QgsFields, QgsField
from qgis.core import QgsVectorLayer
from PyQt4.QtCore import QVariant
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterVector
from processing.core.parameters import ParameterNumber
from processing.core.parameters import ParameterTableField
from processing.core.outputs import OutputVector
from processing.tools import dataobjects, vector
from processing.core.ProcessingLog import ProcessingLog
from math import sqrt


class Sequencing2(GeoAlgorithm):

    INPUT_LAYER = 'INPUT'
    OUTPUT_LAYER = 'OUTPUT'
    ENDPOINTS_LAYER = 'ENDPOINTS_LAYER'
    UNMATCHED_LAYER = 'UNMATCHED_LAYER'
    START_POINT_X = 'START_POINT_X'
    START_POINT_Y = 'START_POINT_Y'
    SEARCH_DISTANCE = 'SEARCH_DISTANCE'

    def defineCharacteristics(self):

        self.name, self.i18n_name = self.trAlgorithm('Sequencing 2')
        self.group, self.i18n_group = self.trAlgorithm('Common Routines')

        self.addParameter(ParameterVector(self.INPUT_LAYER,
                                          self.tr('Input linestrings'), [ParameterVector.VECTOR_TYPE_LINE]))
        self.addParameter(ParameterNumber(self.START_POINT_X,
                                          self.tr('Start X'), default=0.0, optional=False))
        self.addParameter(ParameterNumber(self.START_POINT_Y,
                                          self.tr('Start Y'), default=0.0, optional=False))
        self.addParameter(ParameterNumber(self.SEARCH_DISTANCE,
                                          self.tr('Search Distance'), default=10.0, optional=False))
        
        self.addOutput(OutputVector(self.ENDPOINTS_LAYER, self.tr('Endpoints')))
        self.addOutput(OutputVector(self.UNMATCHED_LAYER, self.tr('Unmatched lines')))
        self.addOutput(OutputVector(self.OUTPUT_LAYER, self.tr('Ordered graph')))

    def asPolyline(self, geometry):
        if geometry.isMultipart():
            return geometry.asMultiPolyline()[0]
        else:
            return geometry.asPolyline()

    def snapToPrecision(self, point, precision):
        x = round(point.x() / precision, 0) * precision
        y = round(point.y() / precision, 0) * precision
        return QgsPoint(x, y)

    def findNearestFeature(self, point, layer, spatial_index, max_distance):

        for match_id in spatial_index.nearestNeighbor(point, 1):
            match = layer.getFeatures(QgsFeatureRequest(match_id)).next()
            if QgsGeometry.fromPoint(point).distance(match.geometry()) <= max_distance:
                return match

        return None

    def distance(self, ptA, ptB):
        return QgsGeometry.fromPoint(ptA).distance(QgsGeometry.fromPoint(ptB))

    def node_type(self, in_degree, out_degree):

        if in_degree == 0:
            if out_degree == 0:
                return 'XOUT' # Exterior node (not included in graph construction)
            elif out_degree == 1:
                return 'SRCE' # Source node
            else:
                return 'DIVG' # Diverging node
        elif in_degree == 1:
            if out_degree == 0:
                return 'EXUT' # Outlet (exutoire)
            elif out_degree == 1:
                return 'NODE' # Simple node between 2 edges (reaches)
            else:
                return 'DIFL' # Diffluence
        else:
            if out_degree == 0:
                return 'XSIN' # Sink
            elif out_degree == 1:
                return 'CONF' # Confluence
            else:
                return 'XXOS' # Crossing

    def processAlgorithm(self, progress):

        layer = dataobjects.getObjectFromUri(self.getParameterValue(self.INPUT_LAYER))
        search_distance = self.getParameterValue(self.SEARCH_DISTANCE)

        features = vector.features(layer)
        total = 100.0 / (2*len(features))
        links = dict()

        # Step 1

        progress.setText(self.tr("Building endpoints index ..."))
        
        segments_to_points = dict()
        points_to_segments = dict()
        measures = dict()

        endpoints_layer = QgsVectorLayer("Point", "endpoints", "memory")
        endpoints_layer.setCrs(layer.crs())
        endpoints_layer.dataProvider().addAttributes([
                QgsField('GID', type=QVariant.Int, len=10),
                QgsField('DIN', type=QVariant.Int, len=6),
                QgsField('DOUT', type=QVariant.Int, len=6),
                QgsField('MEASURE', type=QVariant.Double, len=12, prec=4),
                QgsField('TYPE', type=QVariant.String, len=4)
            ])
        endpoints_index = QgsSpatialIndex()
        endpoints_layer.startEditing()
        total = 100.0 / len(features)
        nextid = 0
        
        for current, feature in enumerate(features):
            
            geometry = feature.geometry()
            polyline = self.asPolyline(geometry)
            start_point = polyline[0]
            end_point = polyline[-1]
        
            # skip loop
            if self.distance(start_point, end_point) < search_distance:
                continue

            endpoint_ids = []
            for point in [ start_point, end_point ]:
                
                endpoint = self.findNearestFeature(point, endpoints_layer, endpoints_index, search_distance)
                if endpoint is not None:
                
                    endpoint_id = endpoint.attribute('GID')
                    endpoint_ids.append(endpoint_id)
                    points_to_segments[endpoint_id].append(feature.id())
                
                else:
                    
                    new_endpoint = QgsFeature()
                    new_endpoint.setGeometry(QgsGeometry.fromPoint(point))
                    new_endpoint.setAttributes([
                            nextid,
                            0,
                            0,
                            0,
                            'XOUT'
                        ])

                    # endpoints_layer.startEditing()
                    endpoints_layer.addFeature(new_endpoint)
                    # endpoints_layer.updateExtents()
                    # endpoints_layer.commitChanges()

                    endpoints_index.insertFeature(new_endpoint)
                    
                    endpoint_ids.append(nextid)
                    points_to_segments[nextid] = [ feature.id() ]
                    measures[nextid] = 0
                    nextid = nextid + 1

            # Record segment (id) -> (endpoint A, endpoint B)
            segments_to_points[feature.id()] = tuple(endpoint_ids)
            progress.setPercentage(int(current * total))

        endpoints_layer.updateExtents()
        endpoints_layer.commitChanges()
        # QgsMapLayerRegistry.instance().addMapLayer(endpoints_layer)
        
        # Rebuild indices : ids have changed when layer was committed
        endpoints_index = QgsSpatialIndex(endpoints_layer.getFeatures())
        endpoints_gid_index = dict()
        for endpoint in endpoints_layer.getFeatures():
            endpoints_gid_index[endpoint.attribute('GID')] = endpoint.id()

        # Step 2

        progress.setText(self.tr("Build directed graph and compute measures ..."))

        layerFields = layer.fields()
        fields = layerFields.toList() + [
            QgsField('NODE_A', type=QVariant.Int, len=10),
            QgsField('NODE_B', type=QVariant.Int, len=10),
            QgsField('STARTM', type=QVariant.Double, len=12, prec=4),
            QgsField('ENDM', type=QVariant.Double, len=12, prec=4)
        ]
        writer = self.getOutputFromName(self.OUTPUT_LAYER).getVectorWriter(
            fields, layer.dataProvider().geometryType(), layer.crs())

        process_stack = []

        start_point = QgsPoint(
            self.getParameterValue(self.START_POINT_X),
            self.getParameterValue(self.START_POINT_Y))
        
        start_endpoint = self.findNearestFeature(start_point, endpoints_layer, endpoints_index, search_distance)
        if start_endpoint is not None:
            process_stack.append(start_endpoint)

        total = 100.0 / len(features)
        current = 0
        endpoints_layer.startEditing()

        while process_stack:
            
            current_endpoint = process_stack.pop()
            current_endpoint_gid = current_endpoint.attribute('GID')
            current_point = current_endpoint.geometry().asPoint()
            segment_ids = points_to_segments[current_endpoint_gid]

            for segment_id in segment_ids:

                if not segments_to_points.has_key(segment_id):
                    continue

                endpointA_gid, endpointB_gid = segments_to_points.pop(segment_id)

                reverse = (current_endpoint_gid != endpointA_gid)
                if reverse:
                    endpointB_gid = endpointA_gid
                    endpointA_gid = current_endpoint_gid
                
                endpointA_id = endpoints_gid_index[endpointA_gid]
                endpointB_id = endpoints_gid_index[endpointB_gid]
                endpointA = endpoints_layer.getFeatures(QgsFeatureRequest(endpointA_id)).next()
                endpointB = endpoints_layer.getFeatures(QgsFeatureRequest(endpointB_id)).next()
                segment = layer.getFeatures(QgsFeatureRequest(segment_id)).next()

                # Compute new attributes
                
                measureA = measures[endpointA_gid]
                measureB = max(measures[endpointB_gid], measureA + segment.geometry().length())
                measures[endpointB_gid] = measureB

                attributes = [
                    endpointA_gid,
                    endpointB_gid,
                    measureA,
                    measureB
                ]

                # Write out feature

                outFeature = QgsFeature()
                polyline = self.asPolyline(segment.geometry())
                if reverse:
                    polyline.reverse()
                polyline[0] = endpointA.geometry().asPoint()
                polyline[-1] = endpointB.geometry().asPoint()
                outFeature.setGeometry(QgsGeometry.fromPolyline(polyline))
                outFeature.setAttributes(segment.attributes() + attributes)
                writer.addFeature(outFeature)

                # Update in-degree and out-degree

                endpointA.setAttribute('DIN', endpointA.attribute('DIN') + 1)
                endpoints_layer.updateFeature(endpointA)
                endpointB.setAttribute('DOUT', endpointB.attribute('DOUT') + 1)
                endpointB.setAttribute('MEASURE', measureB)
                endpoints_layer.updateFeature(endpointB)

                # Step forward

                process_stack.append(endpointB)
                current = current + 1
                progress.setPercentage(int(current * total))

        endpoints_layer.commitChanges()

        # Step 4

        progress.setText(self.tr("Output unmatched lines ..."))
        ProcessingLog.addToLog(ProcessingLog.LOG_INFO, "%d unmatched lines" % len(segments_to_points))

        writer = self.getOutputFromName(self.UNMATCHED_LAYER).getVectorWriter(
            layer.fields().toList(),
            layer.dataProvider().geometryType(),
            layer.crs())
        
        for segment_id in segments_to_points.keys():

            next_feature = layer.getFeatures(QgsFeatureRequest(segment_id)).next()
            outFeature = QgsFeature()
            outFeature.setGeometry(next_feature.geometry())
            outFeature.setAttributes(next_feature.attributes())
            writer.addFeature(outFeature)
            current = current + 1
            progress.setPercentage(int(current * total))

        # Step 5

        progress.setText(self.tr("Write endpoints layer ..."))
        writer = self.getOutputFromName(self.ENDPOINTS_LAYER).getVectorWriter(
            endpoints_layer.fields().toList(),
            endpoints_layer.dataProvider().geometryType(),
            endpoints_layer.crs())

        for endpoint in endpoints_layer.getFeatures():
            measure = measures[endpoint.attribute('GID')]
            feature = QgsFeature(endpoint)
            feature.setGeometry(endpoint.geometry())
            feature.setAttributes(endpoint.attributes())
            feature.setAttribute(
                'TYPE',
                self.node_type(
                    endpoint.attribute('DIN'),
                    endpoint.attribute('DOUT')))
            writer.addFeature(feature)

        progress.setText(self.tr("Done."))


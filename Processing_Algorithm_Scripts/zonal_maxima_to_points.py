"""
/***************************************************************************
    begin                : April 2024
    copyright            : (C) 2024 by Ben Wirf
    email                : ben.wirf@gmail.com
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsFields, QgsField, QgsFeature, QgsFeatureSink,
                        QgsFeatureRequest, QgsWkbTypes, QgsRasterLayer,
                        QgsProcessing, QgsProcessingAlgorithm,
                        QgsProcessingParameterRasterLayer,
                        QgsProcessingParameterFeatureSource,
                        QgsProcessingParameterFeatureSink,
                        QgsPointXY, QgsGeometry)
from qgis.analysis import QgsZonalStatistics
from osgeo import gdal
import numpy as np
import processing
import os

class ZonalMaxPoints(QgsProcessingAlgorithm):
    RASTER = 'RASTER'
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
 
    def __init__(self):
        super().__init__()
 
    def name(self):
        return "zonalmaxpoints"
         
    def displayName(self):
        return "Zonal maxima to points"
 
    def group(self):
        return "Raster analysis"
 
    def groupId(self):
        return "raster_analysis"
 
    def shortHelpString(self):
        return "Extract raster pixels with maximum value for each feature of an\
        overlay polygon layer and add them to an output point layer.\
        Note: If multiple pixels have the same value equal to the zonal maximum,\
        a point feature will be created for each one. If every pixel inside the\
        polygon has the same value (max==min) a single feature at the polygon\
        centroid will be created."
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
   
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.RASTER,
            "Input raster layer"))
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT,
            "Input polygon layer",
            [QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT,
            "Output layer",
            QgsProcessing.TypeVectorPoint))
 
    def processAlgorithm(self, parameters, context, feedback):
        raster_lyr = self.parameterAsRasterLayer(parameters, self.RASTER, context)
        poly_lyr = self.parameterAsSource(parameters, self.INPUT, context)
        if poly_lyr.sourceCrs() != raster_lyr.crs():
            poly_lyr = poly_lyr.materialize(QgsFeatureRequest().setDestinationCrs(raster_lyr.crs(), context.transformContext()))
        output_fields = QgsFields()
        output_fields.append(QgsField('Elev', QVariant.Double, len=5, prec=1))
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                               output_fields, QgsWkbTypes.Point, raster_lyr.crs())
        max_feats = []
        total_fts = poly_lyr.featureCount()
        for i, ft in enumerate(poly_lyr.getFeatures()):
            pcnt = (i/total_fts)*100
            feedback.setProgress(pcnt)
            bb = ft.geometry().boundingBox()
            ext = f'{bb.xMinimum()},{bb.xMaximum()},{bb.yMinimum()},{bb.yMaximum()}'
            params = {'INPUT':raster_lyr,
                    'PROJWIN':ext,
                    'OVERCRS':False,
                    'NODATA':-999,
                    'OPTIONS':'',
                    'DATA_TYPE':0,
                    'EXTRA':'',
                    'OUTPUT':'TEMPORARY_OUTPUT'}
                    
            temp_rl = QgsRasterLayer(processing.run("gdal:cliprasterbyextent",
                                                    params,
                                                    is_child_algorithm=True,
                                                    feedback=None,
                                                    context=context)['OUTPUT'], '', 'gdal')
            
            pixel_size_X = temp_rl.rasterUnitsPerPixelX()
            pixel_size_Y = temp_rl.rasterUnitsPerPixelY()
            res = QgsZonalStatistics.calculateStatistics(temp_rl.dataProvider(),
                                                        ft.geometry(),
                                                        pixel_size_X,
                                                        pixel_size_Y,
                                                        1,
                                                        QgsZonalStatistics.Statistic.Min | QgsZonalStatistics.Statistic.Max)
            if not list(res):
                continue
            min = res[list(res)[0]]
            max = res[list(res)[1]]
            if min == max:
                feat = QgsFeature(output_fields)
                feat.setGeometry(ft.geometry().centroid())
                feat.setAttributes([min])
                max_feats.append(feat)
                continue
            path = temp_rl.source()
            ds = gdal.Open(path)
            geotransform = ds.GetGeoTransform()
            originX = geotransform[0]
            originY = geotransform[3]
            pixelWidth = geotransform[1]
            pixelHeight = geotransform[5]
            arr = ds.ReadAsArray()
            value_indices = list(zip(*np.where(arr == max)))
            all_points = []
            for pp in value_indices:
                x = (originX+(pp[1]*pixelWidth))+pixelWidth/2
                y = (originY+(pp[0]*pixelHeight))+pixelHeight/2
                all_points.append(QgsPointXY(x, y))
            ds = None
            os.remove(path)
            for pt in all_points:
                geom = QgsGeometry.fromPointXY(pt)
                if geom.within(ft.geometry()):
                    feat = QgsFeature(output_fields)
                    feat.setGeometry(geom)
                    feat.setAttributes([max])
                    max_feats.append(feat)
            
        sink.addFeatures(max_feats, QgsFeatureSink.FastInsert)
        return {self.OUTPUT: dest_id}
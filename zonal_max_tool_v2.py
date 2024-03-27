from osgeo import gdal
import numpy as np

class CustomMapTool(QgsMapToolEmitPoint):
    
    def __init__(self, iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        super(CustomMapTool, self).__init__(self.canvas)
        self.buffer_distance = 5000.0# Hard coded for this example (units are meters)
        self.da = QgsDistanceArea()
        #######################################################################
        if not QgsProject.instance().mapLayersByName('Max_Points'):
            self.output_lyr = QgsVectorLayer('Point?crs=epsg:4326', 'Max_Points', 'memory')
            self.output_lyr.dataProvider().addAttributes([QgsField('Elev', QVariant.Double, len=5, prec=1)])
            self.output_lyr.updateFields()
            QgsProject.instance().addMapLayer(self.output_lyr)
        else:
            self.output_lyr = QgsProject.instance().mapLayersByName('Max_Points')[0]
        
    def canvasReleaseEvent(self, e):
        clicked_point = e.mapPoint()
        lyr = self.iface.activeLayer()
        if lyr.type() != QgsMapLayerType.RasterLayer:
            return
        max, coords = self.get_zonal_max(lyr, clicked_point)
        print(max, coords)
        #######################################################################
        fts = []
        for i, coord_pair in enumerate(coords):
            ft = QgsFeature(self.output_lyr.fields())
            ft_geom = QgsGeometry.fromPointXY(QgsPointXY(coord_pair[0], coord_pair[1]))
            if lyr.crs().authid() != 'epsg:4326':
                ft_geom = self.transformed_geom(ft_geom, lyr.crs(), QgsCoordinateReferenceSystem('epsg:4326'))
            ft.setGeometry(ft_geom)
            ft.setAttributes([max])
            fts.append(ft)
        self.output_lyr.dataProvider().addFeatures(fts)
        self.output_lyr.updateExtents()
        self.output_lyr.triggerRepaint()
        #######################################################################

    def get_zonal_max(self, rl, click_pt):
        canvas_crs = self.canvas.mapSettings().destinationCrs()
        if canvas_crs.mapUnits() != QgsUnitTypes.DistanceMeters:
            self.da.setSourceCrs(canvas_crs, self.canvas.mapSettings().transformContext())
            self.da.setEllipsoid(canvas_crs.ellipsoidAcronym())
            radius = self.da.convertLengthMeasurement(self.buffer_distance, canvas_crs.mapUnits())
        else:
            radius = self.buffer_distance
        pt_geom = QgsGeometry.fromPointXY(click_pt)
        buffer = pt_geom.buffer(radius, 50)
        
        if rl.crs() != canvas_crs:
            buffer = self.transformed_geom(buffer, canvas_crs, rl.crs())
        
        bb = buffer.boundingBox()
        ext = f'{bb.xMinimum()},{bb.xMaximum()},{bb.yMinimum()},{bb.yMaximum()}'
        params = {'INPUT':rl,
                'PROJWIN':ext,
                'OVERCRS':False,
                'NODATA':-999,
                'OPTIONS':'',
                'DATA_TYPE':0,
                'EXTRA':'',
                'OUTPUT':'TEMPORARY_OUTPUT'}
                
        temp_rl = QgsRasterLayer(processing.run("gdal:cliprasterbyextent", params)['OUTPUT'], '', 'gdal')
        
        pixel_size_X = temp_rl.rasterUnitsPerPixelX()
        pixel_size_Y = temp_rl.rasterUnitsPerPixelY()
        res = QgsZonalStatistics.calculateStatistics(temp_rl.dataProvider(),
                                                    buffer,
                                                    pixel_size_X,
                                                    pixel_size_Y,
                                                    1,
                                                    QgsZonalStatistics.Statistic.Max)
        if not list(res):
            return NULL, []
        max = res[list(res)[0]]
        max_coords = []
        highest_pts = self.get_pixel_coords_from_val(temp_rl, max)
        for pt in highest_pts:
            pt_geom = QgsGeometry.fromPointXY(pt)
            if pt_geom.within(buffer):
                max_coords.append((pt.x(), pt.y()))
        return max, max_coords
        
    def transformed_geom(self, g, src_crs, dest_crs):
        xform = QgsCoordinateTransform(src_crs, dest_crs, QgsProject.instance())
        g.transform(xform)
        return g
        
    def get_pixel_coords_from_val(self, r_lyr, val):
        path = r_lyr.source()
        ds = gdal.Open(path)
        geotransform = ds.GetGeoTransform()
        originX = geotransform[0]
        originY = geotransform[3]
        pixelWidth = geotransform[1]
        pixelHeight = geotransform[5]
        cols = ds.RasterXSize
        rows = ds.RasterYSize
        arr = ds.ReadAsArray()
        value_indices = list(zip(*np.where(arr == val)))
        all_points = []
        for pp in value_indices:
            x = (originX+(pp[1]*pixelWidth))+pixelWidth/2
            y = (originY+(pp[0]*pixelHeight))+pixelHeight/2
            all_points.append(QgsPointXY(x, y))
        ds = None
        return all_points
        
        
map_tool = CustomMapTool(iface)
iface.mapCanvas().setMapTool(map_tool)
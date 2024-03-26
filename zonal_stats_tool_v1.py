from osgeo import gdal
import numpy as np

class CustomMapTool(QgsMapToolEmitPoint):
    
    def __init__(self, iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        super(CustomMapTool, self).__init__(self.canvas)
        self.buffer_distance = 5000.0# Hard coded for this example (units are meters)
        self.da = QgsDistanceArea()
        
    def canvasReleaseEvent(self, e):
        clicked_point = e.mapPoint()
        lyr = self.iface.activeLayer()
        if lyr.type() != Qgis.LayerType.Raster:
            return
        max, coords = self.get_zonal_max(lyr, clicked_point)
        print(max, coords)

    def get_zonal_max(self, rl, click_pt):
        canvas_crs = self.canvas.mapSettings().destinationCrs()
        if canvas_crs.mapUnits() != Qgis.DistanceUnit.Meters:
            self.da.setSourceCrs(canvas_crs, self.canvas.mapSettings().transformContext())
            self.da.setEllipsoid(canvas_crs.ellipsoidAcronym())
            radius = self.da.convertLengthMeasurement(self.buffer_distance, canvas_crs.mapUnits())
        else:
            radius = self.buffer_distance
        pt_geom = QgsGeometry.fromPointXY(click_pt)
        buffer = pt_geom.buffer(radius, 50)
        
        if rl.crs() != canvas_crs:
            buffer = self.transformed_geom(buffer, canvas_crs, rl.crs())
        
        pixel_size_X = rl.rasterUnitsPerPixelX()
        pixel_size_Y = rl.rasterUnitsPerPixelY()
        res = QgsZonalStatistics.calculateStatistics(rl.dataProvider(),
                                                    buffer,
                                                    pixel_size_X,
                                                    pixel_size_Y,
                                                    1,
                                                    QgsZonalStatistics.Statistic.Max)
        max = res[list(res)[0]]
        max_coords = []
        highest_pts = self.get_pixel_coords_from_val(rl, max)
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
        return all_points
        
        
        
map_tool = CustomMapTool(iface)
iface.mapCanvas().setMapTool(map_tool)

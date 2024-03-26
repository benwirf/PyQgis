from osgeo import gdal
import numpy as np

lyr = iface.activeLayer()

path = lyr.source()

ds = gdal.Open(path)

geotransform = ds.GetGeoTransform()
originX = geotransform[0]
originY = geotransform[3]
pixelWidth = geotransform[1]
pixelHeight = geotransform[5]
cols = ds.RasterXSize
rows = ds.RasterYSize

arr = ds.ReadAsArray()

value_indices = list(zip(*np.where(arr == 150)))

# print(value_indices)

temp_lyr = QgsVectorLayer('Point?crs=epsg:4326', 'points', 'memory')
temp_lyr.dataProvider().addAttributes([QgsField('ID', QVariant.Int)])
temp_lyr.updateFields()
feats = []

count = 1

for pp in value_indices:
    x = (originX+(pp[1]*pixelWidth))+pixelWidth/2# Column index
    y = (originY+(pp[0]*pixelHeight))+pixelHeight/2# Row index
    #print(x, y)
    ft = QgsFeature()
    ft.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
    ft.setAttributes([count])
    feats.append(ft)
    count+=1
    
temp_lyr.dataProvider().addFeatures(feats)
temp_lyr.updateExtents()
QgsProject.instance().addMapLayer(temp_lyr)
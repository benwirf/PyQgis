crs_id = iface.mapCanvas().mapSettings().destinationCrs().authid()

lyr = QgsVectorLayer(f'Polygon?crs={crs_id}', 'Geodesic_Buffer', 'memory')

def geodesic_buffer_geom(x, y, radius):
    crs_canvas = iface.mapCanvas().mapSettings().destinationCrs()
    crs_wgs84 = QgsCoordinateReferenceSystem('epsg:4326')
    
    ct_canvas2wgs84 = QgsCoordinateTransform(crs_canvas, crs_wgs84, QgsProject.instance())
    
    center_pt = ct_canvas2wgs84.transform(QgsPointXY(x, y))
    #print(center_pt)

    proj_string = 'PROJ4:+proj=aeqd +ellps=WGS84 +lat_0={} +lon_0={} +x_0=0 +y_0=0'.format(center_pt.y(), center_pt.x())
    crs_aeqd = QgsCoordinateReferenceSystem(proj_string)
    buffer_geom = QgsGeometry.fromPointXY(QgsPointXY(0, 0)).buffer(radius, 90)
    
    ct_aeqd2canvas = QgsCoordinateTransform(crs_aeqd, crs_canvas, QgsProject.instance())
    buffer_geom.transform(ct_aeqd2canvas)
    ####################################
    
    ####################################
    #print(buffer_geom)
    return buffer_geom


#geom = geodesic_buffer_geom(-1986762.0, 4235015.0, 7000000)

#geom = geodesic_buffer_geom(3627086,-4193979, 5000000)
geom = geodesic_buffer_geom(1022863,1995261, 1000000)

ft = QgsFeature()
ft.setGeometry(geom)
lyr.dataProvider().addFeature(ft)
lyr.updateExtents()
QgsProject.instance().addMapLayer(lyr)
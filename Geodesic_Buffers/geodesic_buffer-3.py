#ext_lyr = QgsVectorLayer('Polygon?crs=epsg:4326', 'Geo Extent', 'memory')
'''
Working well with EPSG:4326
'''

lyr = QgsVectorLayer('Polygon?crs=epsg:4326', 'Geodesic_Buffer', 'memory')

def geodesic_buffer_geom(x, y, radius):
    # Define geometries representing the antimeridian and the extent of global geographic CRS
    antimeridline = QgsGeometry.fromPolyline([QgsPoint(180.0, 90.0), QgsPoint(180.0, -90.0)])
    geo_extent = QgsGeometry.fromWkt('POLYGON ((179.9 85.0, -179.9 85.0, -179.9 -85.0, 179.9 -85.0, 179.9 85.0))')
    #geo_extent = QgsGeometry.fromWkt('POLYGON ((179.9 89.9, -179.9 89.9, -179.9 -89.9, 179.9 -89.9, 179.9 89.9))')
    # Define the required CRSs
    crs_wgs84 = QgsCoordinateReferenceSystem('epsg:4326')
    crs_pac = QgsCoordinateReferenceSystem('epsg:3832')
    proj_string = 'PROJ4:+proj=aeqd +ellps=WGS84 +lat_0={} +lon_0={} +x_0=0 +y_0=0'.format(y, x)
    crs_aeqd = QgsCoordinateReferenceSystem(proj_string)
    # Define the required coordinate transforms
    ct_wgs842aeqd = QgsCoordinateTransform(crs_wgs84, crs_aeqd, QgsProject.instance())
    ct_aeqd2pac = QgsCoordinateTransform(crs_aeqd, crs_pac, QgsProject.instance())
    ct_wgs842pac = QgsCoordinateTransform(crs_wgs84, crs_pac, QgsProject.instance())
    
    center_pt = QgsPointXY(x, y)
    #transform center point to Azimuthal Equidistant projection centered on point
    aeqd_center = ct_wgs842aeqd.transform(center_pt)
    # Buffer with required distance
    aeqd_buffer = QgsGeometry.fromPointXY(aeqd_center).buffer(radius, 90)#.asWkt()
    # Transform buffer to Pacific centered projection
    aeqd_buffer.transform(ct_aeqd2pac)
    # Transform antimeridian line geometry to Pacific centered projection
    antimeridline.transform(ct_wgs842pac)
    # If the buffer crosses the antimeridian, cut it with slightly buffered line
    diff = aeqd_buffer.difference(antimeridline.buffer(1, 2))
    ### Test whether this is valid when transformed back to wgs84
    test_geom = QgsGeometry.fromWkt(diff.asWkt())
    test_geom.transform(ct_wgs842pac, Qgis.TransformDirection.Reverse)
    if not test_geom.isGeosValid():
        poly = QgsGeometry.fromPointXY(aeqd_center).buffer(radius, 90)#.asWkt()
        poly.transform(ct_wgs842aeqd, Qgis.TransformDirection.Reverse)
        arr = [[p.x(), p.y()] for p in poly.asPolygon()[0]]
        arr2 = []
        i = 0
        while i < len(arr) - 1:
            arr2.append(f'{arr[i][0]} {arr[i][1]}')
            if abs(arr[i+1][0] - arr[i][0]) > 180:
                vsign = -1 if arr[i][1] < 0 else 1
                hsign = -1 if arr[i][0] < 0 else 1
                arr2.append(f'{hsign*179.9} {arr[i][1]}')
                arr2.append(f'{hsign*179.9} {vsign*89.9}')
                arr2.append(f'{-hsign*179.9} {vsign*89.9}')
                arr2.append(f'{-hsign*179.9} {arr[i+1][1]}')
                i+=5
            else:
                i+=1
        geom = QgsGeometry.fromWkt(f'POLYGON (({",".join(arr2)}))')
        if not geom.contains(center_pt):
            geom = geo_extent.difference(geom)
            return geom
        return geom.intersection(geo_extent)
    diff.transform(ct_wgs842pac, Qgis.TransformDirection.Reverse)
    #############################
    return diff.intersection(geo_extent)

geom = geodesic_buffer_geom(168, -48, 5000000)
ft = QgsFeature()
ft.setGeometry(geom)
lyr.dataProvider().addFeature(ft)
lyr.updateExtents()
QgsProject.instance().addMapLayer(lyr)
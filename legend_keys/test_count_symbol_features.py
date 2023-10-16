lyr_name = 'Kakadu_Districts_WGS84'

lyr = QgsProject.instance().mapLayersByName(lyr_name)[0]

lyr.countSymbolFeatures()
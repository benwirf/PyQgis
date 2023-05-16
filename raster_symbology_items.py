lyr = QgsProject.instance().mapLayersByName('KNP_slope')[0]
items = lyr.renderer().legendSymbologyItems()
for i in items:
    print(i)
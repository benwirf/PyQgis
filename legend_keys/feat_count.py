lyr = QgsProject.instance().mapLayersByName('perry_land_systems')[0]

print(len(list(lyr.getFeatures('"P_Status" LIKE \'Adequate\''))))
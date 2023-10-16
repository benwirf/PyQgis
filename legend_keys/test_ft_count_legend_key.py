#lyr_name = 'perry_land_systems'
lyr_name = 'Roads'

lyr = QgsProject.instance().mapLayersByName(lyr_name)[0]

def getFeatureCount():
    f_cnt = lyr.featureCount('0')
    print(f_cnt)
    
lyr.symbolFeatureCountMapChanged.connect(getFeatureCount)

lyr.countSymbolFeatures()
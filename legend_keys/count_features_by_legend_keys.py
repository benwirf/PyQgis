lyr_name = 'CDNP_Points'
# lyr_name = 'Kakadu_Districts_WGS84'

lyr = QgsProject.instance().mapLayersByName(lyr_name)[0]
renderer = lyr.renderer().clone()
l_keys = list(renderer.legendKeys())

def getFeatureCount():
    # disconnect slot from signal so we don't end up with multiple connections
    lyr.symbolFeatureCountMapChanged.disconnect(getFeatureCount)
    for k in l_keys:
        print(f'Legend key: {k}')
        print(f'Legend key expression: {renderer.legendKeyToExpression(k, lyr)}')
        print(f'Feature count for legend key: {lyr.featureCount(k)}')
        
lyr.symbolFeatureCountMapChanged.connect(getFeatureCount)

# countSymbolFeatures() returns nullptr (None in Python) if the count has already been done
# so we check the return value and if None is returned, we call our getFeatureCount() method
# because in this case, the symbolFeatureCountMapChanged signal won't be fired
if not lyr.countSymbolFeatures():
    getFeatureCount()
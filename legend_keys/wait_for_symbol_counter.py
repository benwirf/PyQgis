# lyr_name = 'CDNP_Points'
lyr_name = 'Kakadu_Districts_WGS84'

lyr = QgsProject.instance().mapLayersByName(lyr_name)[0]
renderer = lyr.renderer().clone()
l_keys = list(renderer.legendKeys())

cntr = lyr.countSymbolFeatures()

if cntr:
    cntr.waitForFinished()

for k in l_keys:
    print(f'Legend key: {k}')
    print(f'Legend key expression: {renderer.legendKeyToExpression(k, lyr)}')
    print(f'Feature count for legend key: {lyr.featureCount(k)}')
    

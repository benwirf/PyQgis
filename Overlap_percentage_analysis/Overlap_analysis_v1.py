##################################################################
#Author: Ben Wirf 2020############################################
#Email: ben.wirf@gmail.com########################################
##################################################################
'''Intersection analysis with spatial index only'''

import csv
output_file = open('D:\\Folder\\Intersection.csv', 'w', newline='')
writer = csv.writer(output_file)
writer.writerow(['POA Feature'] + ['Parent Region'] + ['Percentage'])

POA_layer = QgsProject().instance().mapLayersByName('POA_2016_AUST')[0]
parent_region_layer = QgsProject().instance().mapLayersByName('PHN_boundaries_AUS_May2017_V7')[0]

d = QgsDistanceArea()
d.setEllipsoid('WGS84')

POA_features = [f for f in POA_layer.getFeatures()]
parent_region_features = [f for f in parent_region_layer.getFeatures()]

index = QgsSpatialIndex()
for f in POA_features:
    index.insertFeature(f)

for parent_region_feature in parent_region_features:
        parent_region_name = parent_region_feature['FIRST_PHN_']
        region_geom = parent_region_feature.geometry()
        ids = index.intersects(region_geom.boundingBox())
        req = QgsFeatureRequest().setFilterFids(ids)
        for POA_feature in POA_layer.getFeatures(req):
            POA_name = POA_feature['POA_NAME16']
            POA_geom = POA_feature.geometry()
            total_area = d.convertAreaMeasurement(d.measureArea(POA_geom), QgsUnitTypes.AreaSquareKilometers)
            if POA_geom.intersects(region_geom):
                intersection = POA_geom.intersection(region_geom)
                intersection_km2 = d.convertAreaMeasurement(d.measureArea(intersection), QgsUnitTypes.AreaSquareKilometers)
                pcnt = (intersection_km2/total_area)*100
                print('Percentage of {} in parent region {}: {}%'.format(POA_name, parent_region_name, pcnt))
                writer.writerow([str(POA_name)] + [str(parent_region_name)] + [str(pcnt)])
            elif POA_geom.within(region_geom):
                print('{} is fully enclosed by {}'.format(POA_name, parent_region_name))
                writer.writerow([str(POA_name)] + [str(parent_region_name)] + ['Fully enclosed- 100'])
            else:
                print('There is no intersection')
                writer.writerow([str(POA_name)] + [str(parent_region_name)] + ['No intersection- 0'])
output_file.close()
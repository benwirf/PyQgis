##################################################################
#Author: Ben Wirf 2020############################################
#Email: ben.wirf@gmail.com########################################
##################################################################
'''Intersection analysis with spatial index, geometry engine and storing
ids and features in a dict to allow removing getFeatures() call from loop'''

import csv
output_file = open('D:\\Folder\\Intersection.csv', 'w', newline='')
writer = csv.writer(output_file)
writer.writerow(['POA Feature'] + ['Parent Region'] + ['Percentage'])

POA_layer = QgsProject().instance().mapLayersByName('POA_2016_AUST')[0]
parent_region_layer = QgsProject().instance().mapLayersByName('PHN_boundaries_AUS_May2017_V7')[0]

d = QgsDistanceArea()
d.setEllipsoid('WGS84')

POA_features = {f.id(): f for f in POA_layer.getFeatures()}
parent_region_features = [f for f in parent_region_layer.getFeatures()]

index = QgsSpatialIndex()
for k, v in POA_features.items():
    index.insertFeature(v)
    
for parent_region_feature in parent_region_features:
        parent_region_name = parent_region_feature['FIRST_PHN_']
        region_geom = parent_region_feature.geometry()
        engine = QgsGeometry.createGeometryEngine(region_geom.constGet())
        engine.prepareGeometry()
        candidate_ids = index.intersects(region_geom.boundingBox())
        candidate_features = [v for k, v in POA_features.items() if k in candidate_ids]
        for POA_feature in candidate_features:
            POA_name = POA_feature['POA_NAME16']
            POA_geom = POA_feature.geometry()
            total_area = d.convertAreaMeasurement(d.measureArea(POA_geom), QgsUnitTypes.AreaSquareKilometers)
            if engine.intersects(POA_geom.constGet()):
                intersection = POA_geom.intersection(region_geom)
                intersection_km2 = d.convertAreaMeasurement(d.measureArea(intersection), QgsUnitTypes.AreaSquareKilometers)
                pcnt = (intersection_km2/total_area)*100
                print('Percentage of {} in parent region {}: {}%'.format(POA_name, parent_region_name, pcnt))
                writer.writerow([str(POA_name)] + [str(parent_region_name)] + [str(pcnt)])
            elif engine.contains(POA_geom.constGet()):
                print('{} is fully enclosed by {}'.format(POA_name, parent_region_name))
                writer.writerow([str(POA_name)] + [str(parent_region_name)] + ['Fully enclosed- 100'])
            else:
                print('There is no intersection')
                writer.writerow([str(POA_name)] + [str(parent_region_name)] + ['No intersection- 0'])
output_file.close()
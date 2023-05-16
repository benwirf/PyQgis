# https://gis.stackexchange.com/questions/307393/qgis-python-ignore-invalid-geometries
from processing.tools import dataobjects

params = {'INPUT':iface.activeLayer(),# Tested with OMP waterpoint layer called 'Water Point'
        'DISTANCE':0.01,
        'SEGMENTS':25,
        'END_CAP_STYLE':0,
        'JOIN_STYLE':0,
        'MITER_LIMIT':2,
        'DISSOLVE':False,
        'OUTPUT':'TEMPORARY_OUTPUT'}
        
buff = processing.runAndLoadResults('native:buffer', params)
context = dataobjects.createContext()
v_lyr = QgsProcessingUtils.mapLayerFromString(buff['OUTPUT'], context)
print(v_lyr.featureCount())
for ft in v_lyr.getFeatures():
    print(ft['Waterpoint'])
    print(ft.geometry())

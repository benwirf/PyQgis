from osgeo import gdal

lyr = QgsProject.instance().mapLayersByName('KNP_slope')[0]

ds = gdal.Open(lyr.source())

arr = ds.ReadAsArray()

no_data = ds.GetRasterBand(1).GetNoDataValue()

min_val = ds.GetRasterBand(1).GetMinimum()

max_val = ds.GetRasterBand(1).GetMaximum()

renderer = lyr.renderer()

shader = renderer.shader()
fn = shader.rasterShaderFunction()
#QgsColorRampShader inherits from QgsRasterShaderFunction
ramp_items = fn.colorRampItemList()

class_values = [i.value for i in ramp_items]

print(class_values[1:-1])
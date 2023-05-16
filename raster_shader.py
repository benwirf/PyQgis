lyr = QgsProject.instance().mapLayersByName('KNP_slope')[0]
renderer = lyr.renderer()
shader = renderer.shader()
fn = shader.rasterShaderFunction()
#QgsColorRampShader inherits from QgsRasterShaderFunction
ramp_items = fn.colorRampItemList()
for i in ramp_items:
    print(i.value, (i.color.red(), i.color.green(), i.color.blue()), i.label)
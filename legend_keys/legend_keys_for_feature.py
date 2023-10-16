#lyr_name = 'perry_land_systems'
# lyr_name = 'CDNP_Points'
lyr_name = 'Kakadu_Districts_WGS84'

lyr = QgsProject.instance().mapLayersByName(lyr_name)[0]
renderer = lyr.renderer().clone()
ms = iface.mapCanvas().mapSettings()
render_context = QgsRenderContext().fromMapSettings(ms)
renderer.startRender(render_context, lyr.fields())

legend_keys = []

for ft in lyr.getFeatures():
    lks = renderer.legendKeysForFeature(ft, render_context)
    for i in list(lks):
        if not i in legend_keys:
            legend_keys.append(i)
    
renderer.stopRender(render_context)

print(legend_keys)
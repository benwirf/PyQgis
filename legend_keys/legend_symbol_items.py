lyr = QgsProject.instance().mapLayersByName('perry_land_systems')[0]
renderer = lyr.renderer().clone()
legend_symbol_items = renderer.legendSymbolItems()
#print(legend_symbol_items)
for lsi in legend_symbol_items:
    rule_key = lsi.ruleKey()
    print(rule_key)
lyr = iface.activeLayer()
renderer = lyr.renderer().clone()
sym_items = renderer.legendSymbolItems()
for i in sym_items:
    print(i.ruleKey())
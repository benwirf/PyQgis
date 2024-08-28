# Define rules with label, expression, color
rules = ( ('Darwin Coastal', """"REG_NAME_7" LIKE 'Darwin%'""", QColor('Green')),
            ('Arnhem', """"REG_NAME_7" LIKE '%Arnhem%'""", QColor('Brown')),
            ('Other', "ELSE", QColor('Gray')))
                
layer = iface.activeLayer()
# create a new rule-based renderer
symbol = QgsSymbol.defaultSymbol(layer.geometryType())
renderer = QgsRuleBasedRenderer(symbol)
# get the "root" rule
root_rule = renderer.rootRule()

for label, expression, color in rules:
    # create a clone (i.e. a copy) of the default rule
    rule = root_rule.children()[0].clone()
    # set the label, expression and color
    rule.setLabel(label)
    rule.setFilterExpression(expression)
    rule.symbol().setColor(color)
    # append the rule to the list of rules
    root_rule.appendChild(rule)

# delete the default rule
root_rule.removeChildAt(0)
# apply the renderer to the layer
layer.setRenderer(renderer)
# refresh the layer on the map canvas
layer.triggerRepaint()
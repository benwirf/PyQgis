v = iface.layerTreeView()
lyr_tree_model = v.layerTreeModel()
tree = lyr_tree_model.rootGroup()
selection_model = v.selectionModel()
current_index = selection_model.currentIndex()
row = current_index.row()

    
def move_up(node):
    pn = node.parent()
    if not isinstance(pn, QgsLayerTree) or row > 0:# Do nothing with very top row (will disable move up action)
        if row == 0:# First row of a group or subgroup
            pnp = pn.parent()
            if QgsLayerTree.isGroup(pnp):
                # Insert child node into pnp(grandparent) at index above the current row's parent
                pnp.insertChildNode(v.node2index(pn).row(), node.clone())
                selection_model.setCurrentIndex(v.node2index(pnp.children()[v.node2index(pn).row()-1]), QItemSelectionModel.Select)
        else:
            sibling_above = pn.children()[row-1]
            # If sibling above is a group, we insert the current node into the group at the last position ***CHANGE
            if QgsLayerTree.isGroup(sibling_above):
                sibling_above.insertChildNode(-1, node.clone())
                selection_model.setCurrentIndex(v.node2index(sibling_above.children()[-1]), QItemSelectionModel.Select)
            else:# Insert current node into parent group at position above current row
                node.parent().insertChildNode(row-1, node.clone())
                selection_model.setCurrentIndex(v.node2index(node.parent().children()[row-1]), QItemSelectionModel.Select)
        pn.removeChildNode(node)

#n = v.index2node(current_index)
n = v.currentNode()

if n:
#    print(get_last_node(n))
    move_up(n)
v = iface.layerTreeView()
lyr_tree_model = v.layerTreeModel()
tree = lyr_tree_model.rootGroup()
selection_model = v.selectionModel()
current_index = selection_model.currentIndex()
row = current_index.row()

def get_last_node(tree_node):
    '''Recursive method to return the node directly above the current selection
    including groups and subgroup tree structures, if the sibling above the
    selected node is a group/sub-group'''
    while tree_node.children():
        tree_node = get_last_node(tree_node.children()[-1])
    return tree_node
    
def move_up(node):
    pn = node.parent()
    if not isinstance(pn, QgsLayerTree) or row > 0:# Do nothing with very top row (will disable move up action)
        if row == 0:# First row of a group or subgroup
            pnp = pn.parent()
            if isinstance(pnp, QgsLayerTreeGroup):
                # Insert child node into pnp(grandparent) at index above the current row's parent
                pnp.insertChildNode(v.node2index(pn).row(), node.clone())
                selection_model.setCurrentIndex(v.node2index(pnp.children()[v.node2index(pn).row()-1]), QItemSelectionModel.Select)
        else:
            sibling_above = pn.children()[row-1]
            ln = get_last_node(sibling_above)
            if node.parent() == ln.parent():
                ln.parent().insertChildNode(row-1, node.clone())
                selection_model.setCurrentIndex(v.node2index(ln.parent().children()[row-1]), QItemSelectionModel.Select)
            else:
                ln.parent().insertChildNode(-1, node.clone())
                selection_model.setCurrentIndex(v.node2index(ln.parent().children()[-1]), QItemSelectionModel.Select)
        pn.removeChildNode(node)

n = v.index2node(current_index)
if n:
    move_up(n)
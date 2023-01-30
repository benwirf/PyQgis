v = iface.layerTreeView()
lyr_tree_model = v.layerTreeModel()
tree = lyr_tree_model.rootGroup()
selection_model = v.selectionModel()
current_index = selection_model.currentIndex()
row = current_index.row()
    
def get_first_ancestor_which_is_not_last_child(n):
    '''Recursive method the first ancestor of the current node
    which is not the last child of it's parent'''
#    print(n.parent())
#    print(n.children())
    while n.parent() and v.node2index(n).row() == len(n.parent().children())-1:
        n = get_first_ancestor_which_is_not_last_child(n.parent())
#    print(n)
    return n

def move_down(node):
    pn = node.parent()
    if not isinstance(pn, QgsLayerTree) or v.node2index(node).row() < len(pn.children())-1:
        if v.node2index(node).row() < len(pn.children())-1:
            sibling_below = pn.children()[row+1]
            # If sibling below is a group, insert node into that group at index 0
            if isinstance(sibling_below, QgsLayerTreeGroup):
                sibling_below.insertChildNode(0, node.clone())
                selection_model.setCurrentIndex(v.node2index(sibling_below.children()[0]), QItemSelectionModel.Select)
            # If sibling below is not a group, insert node into parent at index below
            else:
                pn.insertChildNode(row+2, node.clone())
                selection_model.setCurrentIndex(v.node2index(pn.children()[row+2]), QItemSelectionModel.Select)
        else:# node is last child of its parent
            #We insert the node into it's grandparent node at position below it's parent ***CHANGE            
            if pn.parent():
                pn.parent().insertChildNode(v.node2index(pn).row()+1, node.clone())
                selection_model.setCurrentIndex(v.node2index(pn.parent().children()[v.node2index(pn).row()+1]), QItemSelectionModel.Select)
        pn.removeChildNode(node)
    
n = v.index2node(current_index)
if n:
    print(n)
#    x = get_first_ancestor_which_is_not_last_child(n)
#    print(x)
    move_down(n)
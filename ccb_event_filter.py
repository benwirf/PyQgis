class FilterCheckableComboBox(QDialog):
    
    def __init__(self):
        QDialog.__init__(self)
        self.setGeometry(500, 300, 500, 300)
        self.layout = QVBoxLayout(self)
#        self.filter_le = QLineEdit(self)
        self.ccb = QgsCheckableComboBox(self)
        self.ccb.setEditable(True)
#        self.layout.addWidget(self.filter_le)
        self.layout.addWidget(self.ccb)
        self.ccb.installEventFilter(self)
        
        self.items = [f['REG_NAME_7'] for f in iface.activeLayer().getFeatures()]
        self.set_items(self.items)
        
    def eventFilter(self, obj, event):
#        print(event)
        if event.type() == 7:
            print(event)
            return True
        return False
    
        
    def set_items(self, _items):
        self.ccb.addItems(_items)
        
        
dlg = FilterCheckableComboBox()
dlg.show()
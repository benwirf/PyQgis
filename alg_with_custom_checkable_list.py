from processing.gui.wrappers import WidgetWrapper
from qgis.PyQt.QtWidgets import (QWidget, QListWidget, QListWidgetItem,
                                QLabel, QLineEdit, QGridLayout, QMenu,
                                QAction)
from qgis.PyQt.QtCore import (QCoreApplication, QVariant, Qt, QEvent)
from qgis.PyQt.QtGui import QCursor
from qgis.core import (QgsProcessingAlgorithm, QgsProcessingParameterMatrix,
                        QgsMapLayerProxyModel)
from qgis.gui import (QgsMapLayerComboBox, QgsFieldComboBox)

import re

class CustomListWidget(QgsProcessingAlgorithm):
    INPUT_PARAMS = 'INPUT_PARAMS'
 
    def __init__(self):
        super().__init__()
 
    def name(self):
        return "widgetwrapperexample"
     
    def tr(self, text):
        return QCoreApplication.translate("widgetwrapperexample", text)
         
    def displayName(self):
        return self.tr("Widget wrapper example")
 
    def group(self):
        return self.tr("Examples")
 
    def groupId(self):
        return "examples"
 
    def shortHelpString(self):
        return self.tr("Example script with custom widgets")
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
   
    def initAlgorithm(self, config=None):
        
        param = QgsProcessingParameterMatrix(self.INPUT_PARAMS, 'Input parameters')
        param.setMetadata({'widget_wrapper': {'class': CheckableListWidget}})
        self.addParameter(param)
 
    def processAlgorithm(self, parameters, context, feedback):
        user_options = self.parameterAsMatrix(parameters, self.INPUT_PARAMS, context)
        input_vector_layer = user_options[0]
        # Do something with input_vector_layer...
        
        weight_field = user_options[1]
        # Do something with weight_field...
        
        field_values = user_options[2]
        if field_values:
            # Do something with field_values...
        
        # Just return the input parameter values for demo purposes
        return {'INPUT_LAYER': input_vector_layer,
                'INPUT_FIELD': weight_field,
                'VALUE_LIST': field_values}
        
class CheckableListWidget(WidgetWrapper):

    def createWidget(self):
        self.custom_widget = customParametersWidget()

        return self.custom_widget

    def value(self):
        source_layer = self.custom_widget.get_layer()
        source_field = self.custom_widget.get_field()
        checked_values = self.custom_widget.get_values()
        # cast int/float items back to numeric values if possible
        options = [int(v) if v.isdigit() else float(v) if re.match(r'^-?\d+(?:\.\d+)$', v) else str(v) for v in checked_values]
        params = [source_layer, source_field, options]
        
        return params
        
class customParametersWidget(QWidget):
    def __init__(self):
        super(customParametersWidget, self).__init__()
#        self.setGeometry(500, 300, 500, 250)
        
        self.lyr_lbl = QLabel('Input vector layer:')
        self.lyr_cb = QgsMapLayerComboBox(self)
        self.lyr_cb.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.lyr_cb.layerChanged.connect(self.layer_changed)
        self.fld_lbl = QLabel('Select field:')
        self.fld_cb = QgsFieldComboBox(self)
        self.fld_cb.setLayer(self.lyr_cb.currentLayer())
        self.fld_cb.fieldChanged.connect(self.populate_list_widget)
        self.val_lbl = QLabel('Select values:')
        self.filter_le = QLineEdit(self)
        self.filter_le.setPlaceholderText('Type to filter...')
        self.filter_le.textChanged.connect(self.filter_items)
        self.value_list = QListWidget(self)
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.lyr_lbl, 0, 0, 1, 1)
        self.layout.addWidget(self.lyr_cb, 0, 1, 1, 3)
        self.layout.addWidget(self.fld_lbl, 1, 0, 1, 1)
        self.layout.addWidget(self.fld_cb, 1, 1, 1, 3)
        self.layout.addWidget(self.val_lbl, 2, 0, 1, 1)
        self.layout.addWidget(self.filter_le, 3, 0, 1, 4)
        self.layout.addWidget(self.value_list, 4, 0, 1, 4)
        
        self.setLayout(self.layout)
        
        self.populate_list_widget()
        
        self.context_menu = QMenu(self)
        self.action_check_all = QAction('Select All', self)
        self.action_check_all.triggered.connect(self.select_all)
        self.action_uncheck_all = QAction('De-select All', self)
        self.action_uncheck_all.triggered.connect(self.deselect_all)
        self.context_menu.addAction(self.action_check_all)
        self.context_menu.addAction(self.action_uncheck_all)
        
        self.value_list.viewport().installEventFilter(self)
        
    def layer_changed(self, lyr):
        self.fld_cb.setLayer(lyr)
        self.populate_list_widget()
        
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress and obj == self.value_list.viewport():
            if event.button() == Qt.LeftButton:
                clicked_item = self.value_list.itemAt(event.pos())
                if clicked_item.checkState() == Qt.Checked:
                    clicked_item.setCheckState(Qt.Unchecked)
                else:
                    clicked_item.setCheckState(Qt.Checked)
            elif event.button() == Qt.RightButton:
                self.context_menu.exec(QCursor.pos())
            return True
        return False
        
    def select_all(self):
        for i in range(self.value_list.count()):
            item = self.value_list.item(i)
            if not item.isHidden():
                item.setCheckState(Qt.Checked)

    def deselect_all(self):
        for i in range(self.value_list.count()):
            item = self.value_list.item(i)
            if not item.isHidden():
                item.setCheckState(Qt.Unchecked)
        
    def filter_items(self, filter_txt):
        for i in range(self.value_list.count()):
            item = self.value_list.item(i)
            filter = filter_txt.lower() not in item.text().lower()
            self.value_list.setRowHidden(i, filter)
        
    def populate_list_widget(self):
        self.value_list.clear()
        lyr = self.lyr_cb.currentLayer()
        if not lyr:
            return
        fld_name = self.fld_cb.currentField()
        fld_idx = lyr.fields().lookupField(fld_name)
        list_items = lyr.uniqueValues(fld_idx)
        if list_items:
            for i in list_items:
                li = QListWidgetItem(str(i))
                li.setFlags(li.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                li.setCheckState(Qt.Unchecked)
                self.value_list.addItem(li)
                
    def get_layer(self):
        return self.lyr_cb.currentLayer()
        
    def get_field(self):
        return self.fld_cb.currentField()
    
    def get_values(self):
        return [self.value_list.item(i).data(0) for i in range(self.value_list.count()) if self.value_list.item(i).checkState() == Qt.Checked]
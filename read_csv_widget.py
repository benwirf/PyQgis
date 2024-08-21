import csv
import re

class ReadColorMapWidget(QWidget):
    def __init__(self):
        super(ReadColorMapWidget, self).__init__()
        self.main_layout = QVBoxLayout(self)
        self.setMinimumWidth(600)
        
        self.file_label = QLabel('Select colour map file (.csv)', self)
        self.file_widget = QgsFileWidget(self)
        self.file_widget.setStorageMode(QgsFileWidget.GetFile)
        #self.file_widget.setFilter('*.txt;*.csv')
        self.file_widget.setFilter('*.csv')
        
        self.table_label = QLabel('File data', self)
        self.table_widget = QTableWidget(self)
        
        self.color_cb_label = QLabel('CSV column containing color hexcode', self)
        self.color_column_cb = QComboBox(self)
        
        self.lyr_label = QLabel('Layer', self)
        self.layer_cb = QgsMapLayerComboBox(self)
        self.layer_cb.setFilters(QgsMapLayerProxyModel.VectorLayer)
        
        self.fld_label = QLabel('Classification field', self)
        self.field_cb = QgsFieldComboBox(self)
        self.field_cb.setFilters(QgsFieldProxyModel.String)
        self.field_cb.setLayer(self.layer_cb.currentLayer())
        
        self.main_layout.addWidget(self.file_label)
        self.main_layout.addWidget(self.file_widget)
        self.main_layout.addWidget(self.table_label)
        self.main_layout.addWidget(self.table_widget)
        self.main_layout.addWidget(self.color_cb_label)
        self.main_layout.addWidget(self.color_column_cb)
        self.main_layout.addWidget(self.lyr_label)
        self.main_layout.addWidget(self.layer_cb)
        self.main_layout.addWidget(self.fld_label)
        self.main_layout.addWidget(self.field_cb)
        
        self.file_widget.fileChanged.connect(self.populate_sample)
        self.layer_cb.layerChanged.connect(lambda: self.field_cb.setLayer(self.layer_cb.currentLayer()))
        
    def populate_sample(self, f_path):
        csv_file = open(f_path)
        csv_reader = csv.reader(csv_file, delimiter=',')
        csv_rows = [row for row in csv_reader]
        
        #table_row_count = 6 if len(csv_rows)>6 else len(csv_rows)
        table_row_count = len(csv_rows)
        table_col_count = len(csv_rows[0])
        
        self.table_widget.setColumnCount(table_col_count)
        hdr_items = [csv_rows[0][i] for i in range(table_col_count)]
        self.table_widget.setHorizontalHeaderLabels(hdr_items)
        self.table_widget.setRowCount(table_row_count-1)
        for i in range(1, table_row_count):
            for j in range(table_col_count):
                #print(csv_rows[i][j])
                cell_item = QTableWidgetItem(csv_rows[i][j])
                if re.match('#[a-zA-Z0-9]+$', csv_rows[i][j]):
                    cell_brush = QBrush()
                    cell_brush.setStyle(Qt.SolidPattern)
                    cell_brush.setColor(QColor(csv_rows[i][j]))
                    cell_item.setBackground(cell_brush)
                self.table_widget.setItem(i-1, j, cell_item)
        self.color_column_cb.addItems(hdr_items)
        
w = ReadColorMapWidget()
w.show()
class XY_difference_tool(QgsMapToolEmitPoint):

    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.result = None
        self.start_point = None
        self.rubber_band = QgsRubberBand(iface.mapCanvas())
        self.rubber_band.setColor(QColor(Qt.red))
        self.rubber_band.reset()

    def canvasPressEvent(self, event):
        project = QgsProject().instance()
        units = project.crs().mapUnits()
        str_unit = units.baseClass().encodeUnit(units)
        if self.start_point is None:
            if self.result is not None:
                self.result.close()
            self.rubber_band.reset()
            self.start_point = self.toMapCoordinates(event.pos())
            start_X = self.start_point.x()
            start_Y = self.start_point.y()
        else:
            start_X = self.start_point.x()
            start_Y = self.start_point.y() 
            end_point = self.toMapCoordinates(event.pos())
            end_X = end_point.x()
            end_Y = end_point.y()
            self.result = result_dialog()
            self.result.result_box.setText('X Differential: {} {}\nY Differential: {} {}'.format(end_X - start_X, str_unit, end_Y - start_Y, str_unit))
            self.result.show()
            self.result.btn_ok.clicked.connect(self.msg_accepted)
            self.rubber_band.addPoint(self.start_point)
            self.rubber_band.addPoint(end_point)
            self.start_point = None
                
    def msg_accepted(self):
        self.result.close()
        self.result = None
        self.rubber_band.reset()
    
    def canvasMoveEvent(self, event):
        if self.start_point is not None:
            self.rubber_band.reset()
            v1 = self.start_point
            v2 = self.toMapCoordinates(event.pos())
            self.rubber_band.addPoint(v1)
            self.rubber_band.addPoint(v2)

class result_dialog(QWidget):
    def __init__(self, Parent=None):
        QWidget.__init__(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setGeometry(150, 150, 375, 125)
        self.setWindowTitle('XY Difference Result')
        self.result_box = QTextEdit(self)
        self.result_box.resize(350, 50)
        self.result_box.setFont(QFont('Arial', 10))
        self.result_box.setReadOnly(True)
        self.btn_ok = QPushButton('OK', self)
        self.btn_ok.move(255, 70)
    

T = XY_difference_tool(iface.mapCanvas())
iface.mapCanvas().setMapTool(T)
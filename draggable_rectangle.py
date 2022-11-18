#****************************************************************#
############Author: Ben Wirf November 2022########################
#################Email: ben.wirf@gmail.com########################
#****************************************************************#

class RectangleTool(QgsMapTool):
    
    def __init__(self, iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        QgsMapTool.__init__(self, self.canvas)
        self.project = QgsProject.instance()
        self.rb = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        # Define coordinates of top left & bottom right corners of rectangle
        # These are in geographic coordinates
        self.tl = QgsPointXY(0.2, 44.5)
        self.br = QgsPointXY(2.7, 42.5)
        # Create a rectangle from top left & bottom right points
        # Here we also transform the rectangle to the project CRS so it renders correctly on the canvas
        self.rect = self.transform_rect(QgsRectangle(self.tl, self.br))
        self.geom = QgsGeometry.fromRect(self.rect)
        self.rb.setToGeometry(self.geom)
        self.rb.setStrokeColor(QColor(75, 190, 165))
        self.rb.setFillColor(QColor(75, 190, 165, 75))
        self.rb.setWidth(0.5)
        self.rb.show()
        self.moving = False
        self.start_point = None
        self.new_point = None
        self.tl_x_offset = None
        self.tl_y_offset = None
        self.br_x_offset = None
        self.br_y_offset = None
            
    def transform_rect(self, rect):
        xform = QgsCoordinateTransform(QgsCoordinateReferenceSystem('epsg:4326'), self.project.crs(), self.project)
        return xform.transform(rect)
        
    def canvasPressEvent(self, e):
        # Check if the mouse click is inside the rectangle
        if QgsGeometry().fromPointXY(e.mapPoint()).intersects(self.geom):
            self.start_point = e.mapPoint()
            # Calculate the offset from click point to top left/bottom right corners
            self.tl_x_offset = self.rect.xMinimum() - self.start_point.x()
            self.tl_y_offset = self.rect.yMaximum() - self.start_point.y()
            self.br_x_offset = self.rect.xMaximum() - self.start_point.x()
            self.br_y_offset = self.rect.yMinimum() - self.start_point.y()
            # Set condition to true. We will set back to False when mouse is released
            # This means that rectangle will only be dragged when the mouse button is held down
            self.moving = True
        
    def canvasMoveEvent(self, e):
        if self.moving:
            # Reset the rubber band
            self.rb.reset()
            self.new_point = e.mapPoint()
            # Define new top left/ bottom right corners relative to current cursor position on canvas
            self.tl = QgsPointXY(self.new_point.x()+self.tl_x_offset, self.new_point.y()+self.tl_y_offset)
            self.br = QgsPointXY(self.new_point.x()+self.br_x_offset, self.new_point.y()+self.br_y_offset)
            self.rect = QgsRectangle(self.tl, self.br)
            self.geom = QgsGeometry.fromRect(self.rect)
            self.rb.setToGeometry(self.geom)
            self.rb.show()
                
    def canvasReleaseEvent(self, e):
        # Set condition to False
        if self.moving:
            self.moving = False
    
    def deactivate(self):
        # Remove the rubber band when the custom tool is deactivated
        self.rb.reset()
        
t = RectangleTool(iface)
iface.mapCanvas().setMapTool(t)
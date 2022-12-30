from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                        QgsProcessingAlgorithm,
                        QgsProcessingParameterFeatureSource,
                        QgsProcessingParameterExtent,
                        QgsProcessingParameterFeatureSink,
                        QgsProcessingMultiStepFeedback,
                        QgsCoordinateReferenceSystem,
                        QgsProcessingLayerPostProcessorInterface,
                        QgsVectorLayer,
                        QgsLineSymbol)
import processing
                       
class ExAlgo(QgsProcessingAlgorithm):
    
    INPUT_LINES = 'INPUT_LINES'
    GRID_EXTENT = 'GRID_EXTENT'
    OUTPUT_GRID = 'OUTPUT_GRID'
    OUTPUT_LINES = 'OUTPUT_LINES'
 
    def __init__(self):
        super().__init__()
 
    def name(self):
        return "exalgo"
     
    def tr(self, text):
        return QCoreApplication.translate("exalgo", text)
         
    def displayName(self):
        return self.tr("Example script")
 
    def group(self):
        return self.tr("Examples")
 
    def groupId(self):
        return "examples"
 
    def shortHelpString(self):
        return self.tr("Example script which styles an output layers")
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
        
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_LINES,
            self.tr("Input line layer"),
            [QgsProcessing.TypeVectorLine]))
            
        self.addParameter(QgsProcessingParameterExtent(
            self.GRID_EXTENT,
            self.tr("Line grid extent")
            ))
            
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT_GRID,
            self.tr("Output line grid"),
            QgsProcessing.TypeVectorAnyGeometry))
    
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT_LINES,
            self.tr("Output line layer"),
            QgsProcessing.TypeVectorAnyGeometry))

    def processAlgorithm(self, parameters, context, model_feedback):
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}
        
        # Create line grid
        grid_params = {'TYPE':1,
                        'EXTENT':parameters[self.GRID_EXTENT],
                        'HSPACING':10000,
                        'VSPACING':10000,
                        'HOVERLAY':0,
                        'VOVERLAY':0,
                        'CRS':QgsCoordinateReferenceSystem('EPSG:3857'),# Never use 3857 for accurate distance measurement IRL!
                        'OUTPUT':parameters[self.OUTPUT_GRID]}
                        
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
            
        outputs['line_grid'] = processing.run("native:creategrid", grid_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['line_grid'] = outputs['line_grid']['OUTPUT']
                    
        # Fix Line Geometries
        fix_geom_params = {'INPUT':parameters[self.INPUT_LINES], 'OUTPUT':'TEMPORARY_OUTPUT'}
        
        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}
        
        outputs['fixed_geometries'] = processing.run('native:fixgeometries', fix_geom_params, context=context, feedback=feedback, is_child_algorithm=True) #1
        results['fixed_geometries'] = outputs['fixed_geometries']['OUTPUT']
            
        # Using Field calculator to Add an ID
        fld_calc_params = {
            'INPUT': results['fixed_geometries'],
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,
            'FORMULA': '$id',
            'OUTPUT': parameters[self.OUTPUT_LINES]
        }
        
        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}
                
        outputs['add_id'] = processing.run('native:fieldcalculator', fld_calc_params, context=context, feedback=feedback, is_child_algorithm=True) #2
        results['add_id'] = outputs['add_id']['OUTPUT']
        
        if context.willLoadLayerOnCompletion(results['line_grid']):
            context.layerToLoadOnCompletionDetails(results['line_grid']).setPostProcessor(GridPostProcessor.create())

        if context.willLoadLayerOnCompletion(results['add_id']):
            context.layerToLoadOnCompletionDetails(results['add_id']).setPostProcessor(LinePostProcessor.create())

        return results
    

class GridPostProcessor(QgsProcessingLayerPostProcessorInterface):

    instance = None

    def postProcessLayer(self, layer, context, feedback):
        if not isinstance(layer, QgsVectorLayer):
            return
        renderer = layer.renderer().clone()
        symbol = QgsLineSymbol.createSimple({'line_color': '191,191,191,255', 'line_width': '0.20', 'line_style': 'dash'})
        renderer.setSymbol(symbol)
        layer.setRenderer(renderer)

    @staticmethod
    def create() -> 'GridPostProcessor':
        GridPostProcessor.instance = GridPostProcessor()
        return GridPostProcessor.instance


class LinePostProcessor(QgsProcessingLayerPostProcessorInterface):

    instance = None

    def postProcessLayer(self, layer, context, feedback):
        if not isinstance(layer, QgsVectorLayer):
            return
        renderer = layer.renderer().clone()
        symbol = QgsLineSymbol.createSimple({'line_color': '191,191,191,255', 'line_width': '0.20', 'line_style': 'dash'})
        renderer.setSymbol(symbol)
        layer.setRenderer(renderer)

    @staticmethod
    def create() -> 'LinePostProcessor':
        LinePostProcessor.instance = LinePostProcessor()
        return LinePostProcessor.instance
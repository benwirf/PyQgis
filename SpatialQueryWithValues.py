

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsField, QgsFeature, QgsFeatureSink, QgsFeatureRequest, QgsProcessing,
                       QgsGeometry, QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource, QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterField, QgsSpatialIndex)


class PointsPolygonsValues(QgsProcessingAlgorithm):
    INPUT_POLYGONS = 'INPUT_POLYGONS'
    INPUT_ADDITIONAL = 'INPUT_ADDITIONAL'
    VALUE_FIELD = 'VALUE_FIELD'
    M_VAL = 'M_VAL'
    OUTPUT = 'OUTPUT'

    def __init__(self):
        super().__init__()

    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagRequiresMatchingCrs

    def name(self):
        return "Spatial_query_with_values"

    def tr(self, text):
        return QCoreApplication.translate("Spatial_query_with_values", text)

    def displayName(self):
        return self.tr("Spatial query with values")

    def group(self):
        return self.tr("Spatial Query With Values")

    def groupId(self):
        return "spatial_query_with_values"

    def shortHelpString(self):
        return self.tr("Extracts features with maximum or minimum value from a layer \
        which intersects the features of a polygon layer")

    def helpUrl(self):
        return "https://qgis.org"

    def createInstance(self):
        return type(self)()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_POLYGONS,
            self.tr("Input polygon layer"),
            [QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_ADDITIONAL,
            self.tr("Additional input layer"),
            [QgsProcessing.TypeVectorAnyGeometry]))
        self.addParameter(QgsProcessingParameterField(
            self.VALUE_FIELD,
            self.tr("Attribute field"),
            parentLayerParameterName=self.INPUT_ADDITIONAL, type=0, optional=False))
        self.vals = [self.tr("Maximum"), self.tr("Minimum")]
        self.addParameter(QgsProcessingParameterEnum(
            self.M_VAL,
            self.tr("Select Value"),
            options=self.vals, defaultValue=0))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT,
            self.tr("Output layer"),
            QgsProcessing.TypeVectorAnyGeometry))

    def processAlgorithm(self, parameters, context, feedback):
        source_poly = self.parameterAsSource(parameters, self.INPUT_POLYGONS, context)
        source_add = self.parameterAsSource(parameters, self.INPUT_ADDITIONAL, context)
        val_field = self.parameterAsString(parameters, self.VALUE_FIELD, context)
        feature_value = self.parameterAsEnum(parameters, self.M_VAL, context)
        if feature_value == 0:
            m_val = max
        elif feature_value == 1:
            m_val = min
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                               source_add.fields(), source_add.wkbType(), source_add.sourceCrs())
        max_ids = []
        att_col_idx = source_add.fields().indexFromName(val_field)
        fcount = source_poly.featureCount()
        polygons = source_poly.getFeatures()
        points = source_add.getFeatures()
        index = QgsSpatialIndex()  # this spatial index contains all the features of the point layer
        for point in points:
            index.insertFeature(point)

        for current, polygon in enumerate(polygons):
            if feedback.isCanceled():
                break
            f = int(current + 1)
            pcnt = int(f/fcount * 100/1)
            feedback.setProgress(pcnt)
            ids = []
            vals = []
            poly_geom = polygon.geometry()
            engine = QgsGeometry.createGeometryEngine(poly_geom.constGet())
            engine.prepareGeometry()
            idx_ids = index.intersects(poly_geom.boundingBox())
            for f in source_add.getFeatures(QgsFeatureRequest(idx_ids)):
                geom = f.geometry()
                if engine.contains(geom.constGet()):
                    ids.append(f.id())
                    vals.append(f.attributes()[att_col_idx])
            #Note that the three lines below are all in the polygon feature loop so they are executed once for each polygon feature
            d = dict(zip(ids, vals)) #creates dictionaries with id as key and elevation as value
            if d:
                n_max = m_val(d.values())  #m_val is either max or min depending on which radio button is checked
                max_ids.append([a for a, b in d.items() if b == n_max])  #gets ids from each dictionary as keys with highest value
        all_max_ids = [item for sublist in max_ids for item in sublist]  # creates the flat list from list of lists
        #Below should work after rest of 'SQV' code to be pasted in
        result_features = source_add.getFeatures(QgsFeatureRequest(all_max_ids))

        for feat in result_features:
            out_feat = QgsFeature()
            out_feat.setGeometry(feat.geometry())
            out_feat.setAttributes(feat.attributes())
            sink.addFeature(out_feat, QgsFeatureSink.FastInsert)

        return {self.OUTPUT: dest_id}

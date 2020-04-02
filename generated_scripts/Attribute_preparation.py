from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Attribute_preparation(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSink('Fl', 'fl', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='/home/gift/Documents/git_projects/qgis/QGIS_Flower_Analysis/output_shapefiles/Flower.shp'))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)
        results = {}
        outputs = {}

        # Load layer into project
        alg_params = {
            'INPUT': '/home/gift/Documents/git_projects/qgis/QGIS_Flower_Analysis/Shapefile/Flower_Data.shp',
            'NAME': 'flower'
        }
        outputs['LoadLayerIntoProject'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Date',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 3,
            'FORMULA': 'concat (\"Year\",\'/\',\"Month\",\'/\',\"Day\")',
            'INPUT': outputs['LoadLayerIntoProject']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 3,
            'FIELD_NAME': 'Code',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,
            'FORMULA': 'upper(concat(left(\"Flower\",2),right(\"Flower\",1)))',
            'INPUT': outputs['FieldCalculator']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Refactor fields
        alg_params = {
            'FIELDS_MAPPING': [{'expression': '"Flower"', 'length': 254, 'name': 'Flo_color', 'precision': 0, 'type': 10}, {'expression': '"F_Count"', 'length': 11, 'name': 'Flo_count', 'precision': 0, 'type': 4}, {'expression': '"F_Shape"', 'length': 254, 'name': 'Flo_shape', 'precision': 0, 'type': 10}, {'expression': '"Month"', 'length': 200, 'name': 'Month', 'precision': 0, 'type': 10}, {'expression': '"Day"', 'length': 200, 'name': 'Day', 'precision': 0, 'type': 10}, {'expression': '"Year"', 'length': 200, 'name': 'Year', 'precision': 0, 'type': 10}, {'expression': '"Key"', 'length': 200, 'name': 'Key', 'precision': 0, 'type': 10}, {'expression': '"Developed"', 'length': 254, 'name': 'Matured', 'precision': 0, 'type': 10}, {'expression': '"Latitude"', 'length': 30, 'name': 'Latitude', 'precision': 15, 'type': 6}, {'expression': '"Longitude"', 'length': 30, 'name': 'Longitude', 'precision': 15, 'type': 6}, {'expression': '"Location"', 'length': 254, 'name': 'Location', 'precision': 0, 'type': 10}, {'expression': '"Date"', 'length': 10, 'name': 'Date', 'precision': 3, 'type': 14}, {'expression': '"Code"', 'length': 3, 'name': 'Code', 'precision': 3, 'type': 10}],
            'INPUT': outputs['FieldCalculator']['OUTPUT'],
            'OUTPUT': parameters['Fl']
        }
        outputs['RefactorFields'] = processing.run('qgis:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Fl'] = outputs['RefactorFields']['OUTPUT']
        return results

    def name(self):
        return 'Attribute_preparation'

    def displayName(self):
        return 'Attribute_preparation'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Attribute_preparation()

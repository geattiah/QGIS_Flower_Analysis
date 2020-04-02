from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Add_district_data_to_flower(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSink('D', 'd', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('S', 's', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='/home/gift/Documents/git_projects/qgis/QGIS_Flower_Analysis/output_shapefiles/Flower_Dataset.shp'))
        self.addParameter(QgsProcessingParameterFeatureSink('J', 'j', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(6, model_feedback)
        results = {}
        outputs = {}

        # Load flower layer into project
        alg_params = {
            'INPUT': '/home/gift/Documents/git_projects/qgis/QGIS_Flower_Analysis/output_shapefiles/Flower.shp',
            'NAME': 'f'
        }
        outputs['LoadFlowerLayerIntoProject'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Load schleswig holstein layer into project
        alg_params = {
            'INPUT': '/home/gift/Documents/git_projects/qgis/QGIS_Flower_Analysis/output_shapefiles/Schleswig_Holstein.shp',
            'NAME': 'sh'
        }
        outputs['LoadSchleswigHolsteinLayerIntoProject'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Join attributes by location
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['LoadFlowerLayerIntoProject']['OUTPUT'],
            'JOIN': outputs['LoadSchleswigHolsteinLayerIntoProject']['OUTPUT'],
            'JOIN_FIELDS': None,
            'METHOD': 1,
            'PREDICATE': [0],
            'PREFIX': '',
            'OUTPUT': parameters['J']
        }
        outputs['JoinAttributesByLocation'] = processing.run('qgis:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['J'] = outputs['JoinAttributesByLocation']['OUTPUT']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Refactor fields
        alg_params = {
            'FIELDS_MAPPING': [{'expression': '"Flo_color"', 'length': 254, 'name': 'Flo_color', 'precision': 0, 'type': 10}, {'expression': '"Flo_count"', 'length': 11, 'name': 'Flo_count', 'precision': 0, 'type': 10}, {'expression': '"Flo_shape"', 'length': 254, 'name': 'Flo_shape', 'precision': 0, 'type': 10}, {'expression': '"Month"', 'length': 200, 'name': 'Month', 'precision': 0, 'type': 10}, {'expression': '"Day"', 'length': 200, 'name': 'Day', 'precision': 0, 'type': 10}, {'expression': '"Year"', 'length': 200, 'name': 'Year', 'precision': 0, 'type': 10}, {'expression': '"Key"', 'length': 200, 'name': 'Key', 'precision': 0, 'type': 10}, {'expression': '"Matured"', 'length': 254, 'name': 'Matured', 'precision': 0, 'type': 10}, {'expression': '"Latitude"', 'length': 30, 'name': 'Latitude', 'precision': 15, 'type': 6}, {'expression': '"Longitude"', 'length': 30, 'name': 'Longitude', 'precision': 15, 'type': 6}, {'expression': '"Location"', 'length': 254, 'name': 'Location', 'precision': 0, 'type': 10}, {'expression': '"Date"', 'length': 10, 'name': 'Date', 'precision': 0, 'type': 14}, {'expression': '"Code"', 'length': 4, 'name': 'Code', 'precision': 0, 'type': 10}, {'expression': '"State"', 'length': 50, 'name': 'State', 'precision': 0, 'type': 10}, {'expression': '"District"', 'length': 50, 'name': 'District', 'precision': 0, 'type': 10}],
            'INPUT': outputs['JoinAttributesByLocation']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RefactorFields'] = processing.run('qgis:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Replace null values in District
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'District',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,
            'FORMULA': 'CASE \nWHEN \"District\" IS NULL THEN \'None\'\nELSE \"District\"\nEND',
            'INPUT': outputs['RefactorFields']['OUTPUT'],
            'NEW_FIELD': False,
            'OUTPUT': parameters['D']
        }
        outputs['ReplaceNullValuesInDistrict'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['D'] = outputs['ReplaceNullValuesInDistrict']['OUTPUT']

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Replace null values in state
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'State',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,
            'FORMULA': 'CASE \nWHEN \"State\" IS NULL THEN \'Outside\' \nELSE \"State\"\nEND',
            'INPUT': outputs['ReplaceNullValuesInDistrict']['OUTPUT'],
            'NEW_FIELD': False,
            'OUTPUT': parameters['S']
        }
        outputs['ReplaceNullValuesInState'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['S'] = outputs['ReplaceNullValuesInState']['OUTPUT']
        return results

    def name(self):
        return 'Add_district_data_to_flower'

    def displayName(self):
        return 'Add_district_data_to_flower'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Add_district_data_to_flower()

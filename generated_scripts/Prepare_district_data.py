from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Prepare_district_data(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSink('Sh', 'sh', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='/home/gift/Documents/git_projects/qgis/QGIS_Flower_Analysis/output_shapefiles/sh.shp'))
        self.addParameter(QgsProcessingParameterFeatureSink('S', 's', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Ss', 'ss', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='/home/gift/Documents/git_projects/qgis/QGIS_Flower_Analysis/output_shapefiles/Schleswig_Holstein.shp'))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(5, model_feedback)
        results = {}
        outputs = {}

        # Load german states layer into project
        alg_params = {
            'INPUT': '/home/gift/Documents/git_projects/qgis/QGIS_Flower_Analysis/Shapefile/Germany_states.shp',
            'NAME': 'g_states'
        }
        outputs['LoadGermanStatesLayerIntoProject'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Load germany district layer into project
        alg_params = {
            'INPUT': '/home/gift/Documents/git_projects/qgis/QGIS_Flower_Analysis/Shapefile/Germany_district.shp',
            'NAME': 'g_districts'
        }
        outputs['LoadGermanyDistrictLayerIntoProject'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Extract by attribute
        alg_params = {
            'FIELD': 'GEN',
            'INPUT': outputs['LoadGermanStatesLayerIntoProject']['OUTPUT'],
            'OPERATOR': 0,
            'VALUE': 'Schleswig-Holstein',
            'OUTPUT': parameters['Sh']
        }
        outputs['ExtractByAttribute'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Sh'] = outputs['ExtractByAttribute']['OUTPUT']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Intersection
        alg_params = {
            'INPUT': outputs['ExtractByAttribute']['OUTPUT'],
            'INPUT_FIELDS': None,
            'OVERLAY': outputs['LoadGermanyDistrictLayerIntoProject']['OUTPUT'],
            'OVERLAY_FIELDS': None,
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': parameters['S']
        }
        outputs['Intersection'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['S'] = outputs['Intersection']['OUTPUT']

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Refactor fields
        alg_params = {
            'FIELDS_MAPPING': [{'expression': '"GEN"', 'length': 50, 'name': 'State', 'precision': 0, 'type': 10}, {'expression': '"GEN_2"', 'length': 50, 'name': 'District', 'precision': 0, 'type': 10}, {'expression': '"SHAPE_LENG_2"', 'length': 30, 'name': 'SHAPE_LENG_2', 'precision': 15, 'type': 6}, {'expression': '"SHAPE_AREA_2"', 'length': 30, 'name': 'SHAPE_AREA_2', 'precision': 15, 'type': 6}],
            'INPUT': outputs['Intersection']['OUTPUT'],
            'OUTPUT': parameters['Ss']
        }
        outputs['RefactorFields'] = processing.run('qgis:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Ss'] = outputs['RefactorFields']['OUTPUT']
        return results

    def name(self):
        return 'Prepare_district_data'

    def displayName(self):
        return 'Prepare_district_data'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Prepare_district_data()

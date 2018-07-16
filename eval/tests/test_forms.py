from django.test import TestCase
from django.contrib.auth.models import Group

from eval.forms import EvaluatorCreationForm


class EvaluatorCreationFormTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Create the SurveyCreators and Evaluators groups
        Group.objects.create(name='SurveyCreators')
        Group.objects.create(name='Evaluators')
        # Create more groups for testing
        Group.objects.create(name='Group01')

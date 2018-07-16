import random
import string

from django.contrib.auth.models import Group, Permission
from django.test import Client, TestCase
from django.urls import reverse

from eval.models import Evaluator, SurveyCreator
from eval.views import EvaluatorCreateView


class TestStandardGroups(TestCase):
    """
    This class should be subclassed, not used directly.
    Set up the groups and give them permissions.
    """
    
    @classmethod
    def setUpTestData(cls):
        # Create the SurveyCreators and Evaluators groups
        scs = Group.objects.create(name='SurveyCreators')
        evs = Group.objects.create(name='Evaluators')
        # Give SurveyCreators permission to add Evaluators.
        scs.permissions.add(Permission.objects.get(codename='add_evaluator'))
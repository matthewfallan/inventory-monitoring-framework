from django.contrib.auth.models import Group, Permission
from django.test import TestCase

from eval.models import Evaluator, SurveyCreator
from .tests import TestStandardGroups


class SurveyCreatorModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
    
    def add_survey_creator(self):
        # Create a SurveyCreator.
        SurveyCreator.objects.create(
            first_name='Mary',
            last_name='Sue',
        )
    
    def test_survey_creators_group(self):
        # Test if the SurveyCreators group does not exist initially.
        self.assertNotIn('SurveyCreators', [group.name for group in Group.objects.all()])
        self.add_survey_creator()
        # Test if the SurveyCreators group was created when a SurveyCreator was created.
        self.assertIn('SurveyCreators', [group.name for group in Group.objects.all()])
        # Test if the SurveyCreators group has the default permissions.
        scs = Group.objects.get(name='SurveyCreators')
        permissions = ['view_evaluator', 'add_evaluator', 'change_evaluator', 'delete_evaluator']
        for permission in Permission.objects.all():
            if permission in scs.permissions.all():
                self.assertIn(permission.codename, permissions)
            else:
                self.assertNotIn(permission.codename, permissions)
        # Test if all SurveyCreators are members of the SurveyCreators group.        
        for sc in SurveyCreator.objects.all():
            self.assertIn(scs, sc.groups.all())
        
    def test_first_name_label(self):
        self.add_survey_creator()
        sc = SurveyCreator.objects.get(pk=1)
        # Test if the first_name label is 'first name'.
        field_label = sc._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label, 'first name')


class EvaluatorModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
    
    def test_evaluators_group(self):
        # Test if the Evaluators group does not exist initially.
        self.assertNotIn('Evaluators', [group.name for group in Group.objects.all()])
        # Create an Evaluator.
        Evaluator.objects.create(
            first_name='Marty',
            last_name='Stu',
        )
        # Test if the Evaluators group was created when an Evaluator was created.
        self.assertIn('Evaluators', [group.name for group in Group.objects.all()])
        # Test if the Evaluators group has the default permissions.
        evs = Group.objects.get(name='Evaluators')
        permissions = []
        for permission in Permission.objects.all():
            if permission in evs.permissions.all():
                self.assertIn(permission.codename, permissions)
            else:
                self.assertNotIn(permission.codename, permissions)
        # Test if all SurveyCreators are members of the SurveyCreators group.        
        for ev in Evaluator.objects.all():
            self.assertIn(evs, ev.groups.all())
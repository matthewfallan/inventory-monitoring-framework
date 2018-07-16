import random
import string
from html.parser import HTMLParser

from django.contrib.auth.models import Group, Permission
from django.test import Client, TestCase
from django.urls import reverse

from eval.models import Evaluator, SurveyCreator, User
from eval.views import EvaluatorCreateView
from .tests import TestStandardGroups


LOGIN_REQUIRED_MESSAGE = "Please login to see this page."
NO_PERMISSION_MESSAGE = "Your account doesn't have access to this page."


def get_random_string(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def get_random_evaluator_creation_form_data(groups):
    password = get_random_string(8)
    return {
        'username': get_random_string(6),
        'first_name': get_random_string(6),
        'last_name': get_random_string(6),
        'email': '{}@example.com'.format(get_random_string(6)),
        'groups': groups,
        'password1': password,
        'password2': password,
    }


class TemplateResponseContentParser(HTMLParser):
    def __init__(self):
        super().__init__()


class GroupdFieldContentParser(TemplateResponseContentParser):
    """
    Parse HTML and identify the group options and their values.
    """
    def __init__(self):
        super().__init__()
        # Is the parser currently parsing the groups?
        self.parsing_groups = False
        # Is the parser currently parsing a specific group?
        self.parsing_group = False
        # Store groups here.
        self.groups = dict()
        
    def handle_starttag(self, tag, attrs):
        if not self.parsing_groups:
            # The group options are in an unordered list called 'id_groups'.
            if tag == 'ul' and dict(attrs).get('id') == 'id_groups':
                self.parsing_groups = True
    
    def handle_startendtag(self, tag, attrs):
        # If the parser is currently parsing the groups and encounters an input tag.
        if self.parsing_groups and tag == 'input':
            # The groups are within input tags.
            self.group_value = dict(attrs)['value']
            self.parsing_group = True
    
    def handle_data(self, data):
        if self.parsing_group:
            # If the parser is processing a group, the data are the group name.
            self.group_name = data.strip()
    
    def handle_endtag(self, tag):
        if self.parsing_group and tag == 'label':
            # Groups end with label tags.
            # Add the group to the groups dict.
            self.groups[self.group_name] = self.group_value
            self.group_value = None
            self.group_name = None
            self.parsing_group = False
            
        if self.parsing_groups and tag == 'ul':
            # The group list has ended.
            self.parsing_groups = False


class DashboardTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create users with various permissions.
        names = [
            'no_permissions',
            'view_evaluator',
        ]
        for name in names:
            user = User.objects.create(username=name)
            print(user)
            input()
            for permission in Permission.objects.all():
                if permission.codename in name:
                    user.permissions.add(permission)
    
    def test_need_login(self):
        response = self.client.get('', follow=True)
        assertEqual(response.status_code, 200)
        assertIn(LOGIN_REQUIRED_MESSAGE, response.context.decode())
        
    def test_list_view_permissions(self):
        for user in User.objects.all():
            pass


class EvaluatorListViewTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create several groups.
        groups = [
            'NoMembers',
            'OnlyEvaluator1',
            'OnlyEvaluator2',
            'OnlySurveyCreator',
            'Evaluators1And2',
            'SurveyCreatorAndEvaluator1',
            'SurveyCreatorAndEvaluator2',
        ]
        for group in groups:
            Group.objects.create(name=group)
        # Create a SurveyCreator and two Evaluators.
        for name, user_type in cls.get_users().items():
            user_type.objects.create(username=name)
            # Give the user a password and add the user to the appropriate groups.
            user = user_type.objects.last()
            user.set_password('pswd')
            user.save()
            for group in groups:
                if name in group:
                    user.groups.add(Group.objects.get(name=group))
    
    @classmethod
    def get_users(cls):
        # Define a SurveyCreator and two Evaluators.
        return {
            'SurveyCreator': SurveyCreator,
            'Evaluator1': Evaluator,
            'Evaluator2': Evaluator,
        }
    
    def test_need_to_login(self):
        # Test if the user needs to login to see the Evaluator list page.
        response = self.client.get(reverse('evaluators'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(LOGIN_REQUIRED_MESSAGE, response.content.decode())
    
    def test_evaluator_does_not_have_permission(self):
        # Test if an Evaluator can login.
        login = self.client.login(username='Evaluator1', password='pswd')
        self.assertTrue(login)
        # Test if the Evaluator does not have permission to view this page.
        response = self.client.get(reverse('evaluators'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(NO_PERMISSION_MESSAGE, response.content.decode())
        
    def test_survey_creator_list(self):
        # Test if a SurveyCreator can login.
        login = self.client.login(username='SurveyCreator', password='pswd')
        self.assertTrue(login)
        sc = SurveyCreator.objects.get(username='SurveyCreator')
        # Test if a SurveyCreator has permission to view this page.
        response = self.client.get(reverse('evaluators'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(NO_PERMISSION_MESSAGE, response.content.decode())
        self.assertIn("Evaluators", response.content.decode())
        # Test if the response lists only the Evaluators in the same group as the SurveyCreator.
        evaluator_list = response.context['object_list']
        for evaluator in Evaluator.objects.all():
            common_groups = [group for group in Group.objects.all() if group in sc.groups.all() and group in evaluator.groups.all()]
            if evaluator in evaluator_list:
                self.assertTrue(common_groups)
            else:
                self.assertFalse(common_groups)


class EvaluatorCreateViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create more groups for testing.
        Group.objects.create(name='NoMembers')
        Group.objects.create(name='OnlySurveyCreator')
        Group.objects.create(name='SurveyCreatorAndEvaluator1')
        Group.objects.create(name='SurveyCreatorAndEvaluator2')
        # Create a SurveyCreator.
        sc = SurveyCreator.objects.create(username='sc')
        sc.set_password('pswd')
        sc.save()
        # Add the SurveyCreator to some of the groups.
        sc.groups.add(Group.objects.get(name='OnlySurveyCreator'))
        sc.groups.add(Group.objects.get(name='SurveyCreatorAndEvaluator1'))
        sc.groups.add(Group.objects.get(name='SurveyCreatorAndEvaluator2'))

    def test_can_get_login_page(self):
        # Get the login page.
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_survey_creator_can_create_evaluator(self):
        # Login with SurveyCreator account.
        login = self.client.login(username='sc', password='pswd')
        # Test if login succeeded.
        self.assertTrue(login)
        # Set the user to the SurveyCreator.
        user = SurveyCreator.objects.get(username='sc')
        # Test if the SurveyCreator is an active user.
        self.assertTrue(user.is_active)
        # Test if the SurveyCreator has permission to create an Evaluator.
        self.assertTrue(user.has_perm('eval.add_evaluator'))
        # Test if the SurveyCreator can view the creation form.
        response = self.client.get(reverse('create-evaluator'), follow=True)
        self.assertEqual(response.status_code, 200)
        # Test if the SurveyCreator can select only groups to which she belongs.
        group_parser = GroupdFieldContentParser()
        group_parser.feed(response.content.decode())
        groups = group_parser.groups
        self.assertIn('OnlySurveyCreator', groups)
        self.assertIn('SurveyCreatorAndEvaluator1', groups)
        self.assertIn('SurveyCreatorAndEvaluator2', groups)
        self.assertNotIn('NoMembers', groups)
        # Make the data for the form.
        group_names = ['SurveyCreatorAndEvaluator1', 'SurveyCreatorAndEvaluator2']
        group_values = [groups[name] for name in group_names]
        form_data = get_random_evaluator_creation_form_data(group_values)
        response = self.client.get(reverse('create-evaluator'))
        # Post the data to create the Evaluator.
        response = self.client.post(reverse('create-evaluator'), form_data, follow=True)
        # Test if the Evaluator was created.
        self.assertEqual(Evaluator.objects.count(), 1)
        # Get the Evaluator object from the database.
        evaluator = Evaluator.objects.last()
        # Test if the Evaluator is in the Evaluators group and the other selected groups.
        for group in Group.objects.filter(name__in=group_names + ['Evaluators']):
            self.assertIn(group, evaluator.groups.all())
        # Test if the Evaluator is not in any of the other groups.
        for group in Group.objects.exclude(name__in=group_names + ['Evaluators']):
            self.assertNotIn(group, evaluator.groups.all())
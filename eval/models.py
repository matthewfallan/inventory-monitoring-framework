from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import settings


class User(AbstractUser):
    """
    This is a custom User class. It is used for authentication and is the base class of SurveyCreator and Evaluator classes.
    """
    # Assign default identification flags.
    is_surveycreator = False
    is_evaluator = False

    def get_significant_groups(self):
        """
        Return the user's groups other than the groups SurveyCreators and Evaluators.
        """
        return self.groups.exclude(name__in=['SurveyCreators', 'Evaluators'])

    def __str__(self):
        return "{}, {}".format(self.last_name, self.first_name)


class SurveyCreator(User):
    """
    A SurveyCreator has permission to create, edit, and delete Evaluators and create, assign, and analyze surveys.
    """
    is_surveycreator = True
    class Meta:
        # These names appear on the admin site.
        verbose_name = 'SurveyCreator'
        verbose_name_plural = 'SurveyCreators'


@receiver(post_save, sender=SurveyCreator)
def add_survey_creator_to_groups(sender, **kwargs):
    # Add each new SurveyCreator to the SurveyCreators group.
    group, created = Group.objects.get_or_create(name='SurveyCreators')
    sender.objects.last().groups.add(group)


class Evaluator(User):
    """
    An Evaluator has permission to take a survey assigned by an SurveyCreator.
    """
    is_evaluator = True
    class Meta:
        # These names appear on the admin site.
        verbose_name = 'Evaluator'
        verbose_name_plural = 'Evaluators'
        # Define permissions for manipulating Evaluator data. 
        permissions = (
            ('view_evaluator', 'Can view Evaluator'),
        )

@receiver(post_save, sender=Evaluator)
def add_evaluator_to_groups(sender, **kwargs):
    # Add each new Evaluator to the Evaluators group.
    group, created = Group.objects.get_or_create(name='Evaluators')
    sender.objects.last().groups.add(group)

@receiver(post_save, sender=Group)
def assign_group_permissions(sender, **kwargs):
    # Give default permissions to the groups when they are created.
    group = sender.objects.last()
    if group.name == 'SurveyCreators':
        # SurveyCreators have the following permissions:
        permissions = [
            'view_evaluator',
            'add_evaluator',
            'change_evaluator',
            'delete_evaluator',
        ]
    elif group.name == 'Evaluators':
        # Evaluators have the following permissions:
        permissions = []#['take_survey',]
    else:
        # Other groups have no default permissions.
        permissions = []
    for permission in permissions:
        group.permissions.add(Permission.objects.get(codename=permission))


class Survey(models.Model):
    pass
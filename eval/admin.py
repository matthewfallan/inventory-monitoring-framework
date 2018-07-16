from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import SurveyCreator, Evaluator

# Register your models here.

@admin.register(SurveyCreator)
class SurveyCreatorAdmin(UserAdmin):
    """
    This provides the interface through which the superuser can create a SurveyCreator.
    """
    model = SurveyCreator


@admin.register(Evaluator)
class EvaluatorAdmin(UserAdmin):
    """
    This provides the interface through which the superuser can view an Evaluator.
    """
    model = Evaluator

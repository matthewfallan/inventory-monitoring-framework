from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

from .models import Evaluator
from . import settings


class EvaluatorCreationForm(UserCreationForm):
    """
    This form enables a SurveyCreator to create an Evaluator.
    """
    def __init__(self, *args, **kwargs):
        try:
            # The user who is creating the Evaluator must be known
            # user cannot be passed as a separate argument (i.e. outside of kwargs)
            # user must be removed from kwargs before super(EvaluatorCreationForm, self).__init__ is called
            user = kwargs.pop('user')
        except KeyError:
            raise KeyError("An EvaluatorCreationForm requires a 'user' keyword argument.")
        # Initialize the EvaluatorCreationForm.
        super().__init__(*args, **kwargs)
        # Allow the user to assign the Evaluator to only the groups of which the user is a member
        # Exclude the SurveyCreators and Evaluators groups
        # The Evaluator CANNOT be a member of the SurveyCreators group
        # The Evaluator will be assigned to the Evaluators group later
        self.fields['groups'] = forms.ModelMultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            queryset=Group.objects.exclude(name__in=['SurveyCreators', 'Evaluators']).filter(pk__in=[group.pk for group in user.groups.all()]),
        )
            
    # Specify that these fields are required
    first_name = forms.CharField(max_length=settings.USERNAME_MAX_LENGTH, required=True)
    last_name = forms.CharField(max_length=settings.USERNAME_MAX_LENGTH, required=True)
    email = forms.CharField(widget=forms.EmailInput, max_length=settings.EMAIL_MAX_LENGTH, required=True)
    
    class Meta:
        model = Evaluator
        fields = ('username', 'first_name', 'last_name', 'email', 'groups', 'password1', 'password2')

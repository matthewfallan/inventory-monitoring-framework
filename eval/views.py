from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView

from .forms import EvaluatorCreationForm
from .models import Evaluator


@login_required
def index(request):
    """
    View function for Dashboard page.
    """
    # Render the HTML.
    return render(request, 'index.html')


class EvaluatorListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """
    This view lists all of the Evaluators in a group.
    """
    # List Evaluators.
    model = Evaluator
    # The current user must have permission to view an Evaluator.
    permission_required = ('eval.view_evaluator',)
    # Location of the template (required).
    template_name = 'eval/evaluator_list.html'

    def get_queryset(self):
        # Only return Evaluators that share at least one group (besides the groups SurveyCreators or Evaluators) with the user.
        user_groups = self.request.user.get_significant_groups()
        return [evaluator for evaluator in Evaluator.objects.all() if any([group in user_groups for group in evaluator.groups.all()])]


class EvaluatorCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    This view lets a SurveyCreator create an Evaluator.
    """
    # The current user must have permission to create an Evaluator.
    permission_required = ('eval.add_evaluator',)
    # Location of the template (required).
    template_name = 'eval/evaluator_form.html'
    # Redirect to the dashboard after creating the Evaluator.
    #FIXME: redirect to evaluator list page.
    success_url = '/'

    def get_form(self):
        # Mimics django.views.generic.edit.FormMixin.get_form.
        kwargs = self.get_form_kwargs()
        # Add the user keyword to kwargs before creating the form.
        kwargs['user'] = self.request.user
        return EvaluatorCreationForm(**kwargs)

    def form_valid(self, form, *args, **kwargs):
        # Add the Evaluator to each selected group (which is not done automatically).
        # NOTE: this step does not add the Evaluator to the Evaluators group.
        evaluator = form.save()
        groups = form.cleaned_data['groups']
        for group in groups:
            evaluator.groups.add(group)
        return super().form_valid(form, *args, **kwargs)
    
    def form_invalid(self, form, *args, **kwargs):
        return super().form_invalid(form, *args, **kwargs)


class EvaluatorUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    pass


class SurveyListView(LoginRequiredMixin, generic.ListView):
    pass

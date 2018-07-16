from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create_evaluator/', views.EvaluatorCreateView.as_view(), name='create-evaluator'),
    path('evaluators/', views.EvaluatorListView.as_view(), name='evaluators'),
    path('surveys/', views.SurveyListView.as_view(), name='surveys'),
]

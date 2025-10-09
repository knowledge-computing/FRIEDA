from django.urls import path
from .views import SurveyResponseCreateView

urlpatterns = [
    path('submit/', SurveyResponseCreateView.as_view(), name='submit')
]

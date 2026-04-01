# api/views.py
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import FormParser, MultiPartParser
from .models import SurveyResponse
from .serializers import SurveyResponseSerializer

class SurveyResponseCreateView(generics.CreateAPIView):
    queryset = SurveyResponse.objects.all()
    serializer_class = SurveyResponseSerializer
    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [FormParser, MultiPartParser]

    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        next_url = (request.data.get('next_url') or '').strip()
        if next_url:
            sep = '&' if '?' in next_url else '?'
            return HttpResponseRedirect(f"{next_url}{sep}ok=1")
        return resp
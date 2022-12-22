
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from wgapi.wg_serializer import WGTokenObtainPairSerializer, RegisterSerializer

from .models import *
from .wg_serializer import *

class WGTokenObtainPairView(TokenObtainPairView):
    serializer_class = WGTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = WiseGroceryUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/login/',
        '/api/register/',
        '/api/token/refresh/'
    ]
    return Response(routes)

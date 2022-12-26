import json
from django.db.models import Case, F, Q, OuterRef, Subquery, Sum, When
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from wgapi.wg_serializer import WGTokenObtainPairSerializer, RegisterSerializer

from .filters import *
from .models import *
from .permissions import *
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

class EquipmentTypeViewSet(viewsets.ModelViewSet):
    queryset = EquipmentType.objects.prefetch_related('equipment_set')
    serializer_class = EquipmentTypeSerializer
    permission_classes = [IsAuthenticated, IsOwner]

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.prefetch_related('stockitem_set')
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = EquipmentFilterSet

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related('replacement_products', 'stockitem_set', 'recipeproduct_set')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = ProductFilterSet

class StockItemViewSet(viewsets.ModelViewSet):
    queryset = StockItem.objects.prefetch_related('product', 'equipment')
    serializer_class = StockItemSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = StockItemFilterSet

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.prefetch_related('items')
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = RecipeFilterSet

class RecipeProductViewSet(viewsets.ModelViewSet):
    queryset = RecipeProduct.objects.prefetch_related('recipe', 'product')
    serializer_class = RecipeProductSerializer
    permission_classes = [IsAuthenticated, IsOwner]

class CookingPlanViewSet(viewsets.ModelViewSet):
    queryset = CookingPlan.objects.prefetch_related('recipe')
    serializer_class = CookingPlanSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = CookingPlanFilterSet

class PurchaseItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseItem.objects.prefetch_related('product', 'shop_plan')
    serializer_class = PurchaseItemSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = PurchaseItemFilterSet

class ShoppingPlanViewSet(viewsets.ModelViewSet):
    queryset = ShoppingPlan.objects.prefetch_related('purchaseitem_set')
    serializer_class = ShoppingPlanSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = ShoppingPlanFilterSet

class ConversionRuleViewSet(viewsets.ModelViewSet):
    queryset = ConversionRule.objects.prefetch_related('purchaseitem_set')
    serializer_class = ConversionRuleSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_fields = ('product', 'from_unit', 'to_unit', 'created_by')

class ConfigViewSet(viewsets.ModelViewSet):
    queryset = Config.objects.prefetch_related('purchaseitem_set')
    serializer_class = ConfigSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_fields = ('created_by')

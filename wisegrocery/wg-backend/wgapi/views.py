from django.urls import reverse
from rest_framework import generics, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

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
        request.build_absolute_uri('/api/login/'),
        request.build_absolute_uri('/api/register/'),
        request.build_absolute_uri('/api/token/refresh/'),
        request.build_absolute_uri('/api/equipment_types/'),
        request.build_absolute_uri('/api/equipments/'),
        request.build_absolute_uri('/api/products/'),
        request.build_absolute_uri('/api/stock_items/'),
        request.build_absolute_uri('/api/recipes/'),
        request.build_absolute_uri('/api/recipe_product/'),
        request.build_absolute_uri('/api/cooking_plans/'),
        request.build_absolute_uri('/api/purchase/'),
        request.build_absolute_uri('/api/purchase_items/'),
        request.build_absolute_uri('/api/conversion_rules/'),
        request.build_absolute_uri('/api/config/'),
    ]
    return Response(routes)

class EquipmentTypeViewSet(viewsets.ModelViewSet):
    queryset = EquipmentType.objects.prefetch_related('equipment_set')
    serializer_class = EquipmentTypeSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def perform_create(self, serializer):
        serializer.save(creaated_by=self.request.user)

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.prefetch_related('stockitem_set')
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = EquipmentFilterSet

    def perform_create(self, serializer):
        serializer.save(creaated_by=self.request.user)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related('replacement_products', 'stockitem_set', 'recipeproduct_set')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = ProductFilterSet

    def perform_create(self, serializer):
        serializer.save(creaated_by=self.request.user)

class StockItemViewSet(viewsets.ModelViewSet):
    queryset = StockItem.objects.prefetch_related('product', 'equipment')
    serializer_class = StockItemSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = StockItemFilterSet

    def perform_create(self, serializer):
        serializer.save(creaated_by=self.request.user)

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.prefetch_related('items')
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = RecipeFilterSet

    def perform_create(self, serializer):
        serializer.save(creaated_by=self.request.user)

class RecipeProductViewSet(viewsets.ModelViewSet):
    queryset = RecipeProduct.objects.prefetch_related('recipe', 'product')
    serializer_class = RecipeProductSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def perform_create(self, serializer):
        serializer.save(creaated_by=self.request.user)

class CookingPlanViewSet(viewsets.ModelViewSet):
    queryset = CookingPlan.objects.prefetch_related('recipe')
    serializer_class = CookingPlanSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = CookingPlanFilterSet

    def perform_create(self, serializer):
        serializer.save(creaated_by=self.request.user)

class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.prefetch_related('PurchaseItemSet')
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = PurchaseFilterSet

    def perform_create(self, serializer):
        serializer.save(creaated_by=self.request.user)

class PurchaseItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseItem.objects.prefetch_related('purchase', 'product')
    serializer_class = PurchaseItemSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = PurchaseItemFilterSet

    def perform_create(self, serializer):
        serializer.save(creaated_by=self.request.user)

# class ShoppingPlanViewSet(viewsets.ModelViewSet):
#     queryset = ShoppingPlan.objects.prefetch_related('purchaseitem_set')
#     serializer_class = ShoppingPlanSerializer
#     permission_classes = [IsAuthenticated, IsOwner]
#     filterset_class = ShoppingPlanFilterSet

#     def perform_create(self, serializer):
#         serializer.save(creaated_by=self.request.user)

class ConversionRuleViewSet(viewsets.ModelViewSet):
    queryset = ConversionRule.objects.prefetch_related('products')
    serializer_class = ConversionRuleSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_fields = ('products', 'from_unit', 'to_unit', 'created_by')

    def perform_create(self, serializer):
        serializer.save(creaated_by=self.request.user)

class ConfigViewSet(viewsets.ModelViewSet):
    queryset = Config.objects.all()
    serializer_class = ConfigSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_fields = ('created_by')

    def perform_create(self, serializer):
        serializer.save(creaated_by=self.request.user)

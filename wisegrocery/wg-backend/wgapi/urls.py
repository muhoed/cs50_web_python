from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import *

app_name = "wisegrocery"

router = routers.SimpleRouter()
router.register(r'equipment_types', EquipmentTypeViewSet)
router.register(r'equipments', EquipmentViewSet)
router.register(r'products', ProductViewSet)
router.register(r'stock_items', StockItemViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'recipe_product', RecipeProductViewSet)
router.register(r'cooking_plans', CookingPlanViewSet)
router.register(r'purchase_items', PurchaseItemViewSet)
router.register(r'shopping_plans', ShoppingPlanViewSet)
router.register(r'conversion_rules', ConversionRuleViewSet)
router.register(r'config', ConfigViewSet)

urlpatterns = [
    path('', getRoutes),
    path('login/', WGTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
]

urlpatterns += router.urls

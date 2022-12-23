from django.db.models import F, OuterRef, Subquery, Sum
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from wgapi.wg_serializer import WGTokenObtainPairSerializer, RegisterSerializer

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

    @action(detail=False)
    def get_equipment_with_free_space_by_tempreture(self, request, min_temp=None, max_temp=None):
        stock_items = StockItem.objects.filter(
            pk=OuterRef('pk'),
            status_not_in=[
                wg_enumeration.STOCK_STATUSES.COOKED, 
                wg_enumeration.STOCK_STATUSES.WASTED,
                ]
            )
        conv_rule = ConversionRule.objects.filter(
            product=OuterRef('product'),
            unit_to=wg_enumeration.VolumeUnits.LITER,
            unit_from=OuterRef('unit')
            ).values('ratio')
        stock_items.annotate(conv_ratio=Subquery(conv_rule))
        selected_equipment = Equipment.objects.annotate(
            used_volume=Sum(Subquery(stock_items.volume * stock_items.conv_ratio))
        ).filter(volume__gt=F('used_volume'))

        if min_temp and max_temp:
            selected_equipment = selected_equipment.filter(
                min_temperature__gte=min_temp,
                max_temperature__lte=max_temp
            )
        elif min_temp:
            selected_equipment = selected_equipment.filter(
                min_temperature__gte=min_temp
            )
        elif max_temp:
            selected_equipment = selected_equipment.filter(
                max_temperature__lte=max_temp
            )

        selected_equipment = selected_equipment.prefetch_related('stockitem_set')

        serializer = self.get_serializer(selected_equipment, many=True)
        return Response(serializer.data)

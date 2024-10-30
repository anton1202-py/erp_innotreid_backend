from drf_spectacular.utils import extend_schema, OpenApiTypes, OpenApiParameter, OpenApiExample
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from apps.product.serializer import ClasterSerializer, WarehouseSerializer
from rest_framework import status
from apps.company.permission_class import IsSuperUser

from .models import Claster, Company, WarehouseYandex

PARAMETRS = [
    OpenApiParameter('claster_to', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Claster"),
    OpenApiParameter('region_name', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Region name")]

class ClasterApiView(APIView):
    permission_classes = [IsSuperUser]
   
    @extend_schema(
        description='Get all Claster and region name',
        tags=["Claster"],
        responses={200: ClasterSerializer(many=True)},
        parameters=PARAMETRS
    )
    def get(self, requests: Request, company_id):
        company = get_object_or_404(Company,id=company_id)
        claster_to = requests.query_params.get("claster_to","")
        region_name = requests.query_params.get("region_name","")
        
        claster = Claster.objects.filter(company=company, region_name__contains=region_name, claster_to__contains=claster_to)
        serializer = ClasterSerializer(claster,many=True)

        return Response(serializer.data, status.HTTP_200_OK)
    
    @extend_schema(
        description='Create Claster and region name',
        tags=["Claster"],
        responses={201: ClasterSerializer(many=True)},
        request=ClasterSerializer,
        examples=[
        OpenApiExample(
            'Example 1',
            summary='Simple example',
            description='This is a simple example of input.',
            value={
                "claster_to": "string",
                "region_name": "string"
            },
            request_only=True,  # This indicates that the example is only for the request body.
        ),
    ]
    )
    def post(self,request: Request, company_id):
        company = get_object_or_404(Company, id=company_id)
        data = request.data.copy()
        data['company'] = company_id
        serializer = ClasterSerializer(data=data)
        del data
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
class ClasterUpdateAndDeleteApiView(APIView):
    permission_classes = [IsSuperUser]
   
    @extend_schema(
        description='Delete Claster',
        tags=["Claster"],
        responses={200: {"message": "Claster is succesfully deleted"}},
    )
    def delete(self, requests: Request, claster_id):
        claster = get_object_or_404(Claster, id=claster_id)
        claster.delete()
        return Response({"message": "Claster is succesfully deleted"}, status.HTTP_200_OK)
    
    @extend_schema(
        description='Create Claster and region name',
        tags=["Claster"],
        responses={200: ClasterSerializer()},
        request=ClasterSerializer,
        examples=[
        OpenApiExample(
            'Example 1',
            summary='Simple example',
            description='This is a simple example of input.',
            value={
                    "claster_to": "string",
                    "region_name": "string"
            },
            request_only=True,  # Only applicable for request bodies
        ),
    ]
    )
    def put(self,request: Request, claster_id):
        claster = get_object_or_404(Claster, id=claster_id)
        company_id = claster.company.pk
        data = request.data.copy()
        data['company'] = company_id
        serializer = ClasterSerializer(claster,data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
PARAMETRS = [
    OpenApiParameter('claster_to', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Claster"),
    OpenApiParameter('warehouse_id', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="Warehouse ID from yandexmarket")]

class WarehouseApiView(APIView):
    permission_classes = [IsSuperUser]
   
    @extend_schema(
        description='Get all Yandex Warehouse and Claster',
        tags=["Warehouse Yandex"],
        responses={200: WarehouseSerializer(many=True)},
        parameters=PARAMETRS
    )
    def get(self, requests: Request, company_id):
        company = get_object_or_404(Company,id=company_id)
        claster_to = requests.query_params.get("claster_to","")
        region_name = requests.query_params.get("warehouse_id","")
        
        claster = WarehouseYandex.objects.filter(company=company, warehouse_id__contains=region_name, claster_to__contains=claster_to)
        serializer = WarehouseSerializer(claster,many=True)

        return Response(serializer.data, status.HTTP_200_OK)
    
    @extend_schema(
        description='Create Warehouse Yandex and claster',
        tags=["Warehouse Yandex"],
        responses={201: WarehouseSerializer(many=True)},
        request=ClasterSerializer,
        examples=[
        OpenApiExample(
            'Example 1',
            summary='Simple example',
            description='This is a simple example of input.',
            value={
                "claster_to": "string",
                "warehouse_id": 0
            },
            request_only=True,  # This indicates that the example is only for the request body.
        ),
    ]
    )
    def post(self,request: Request, company_id):
        company = get_object_or_404(Company, id=company_id)
        data = request.data.copy()
        data['company'] = company_id
        serializer = WarehouseSerializer(data=data)
        del data
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
class WarehouseUpdateAndDeleteApiView(APIView):
    permission_classes = [IsSuperUser]
   
    @extend_schema(
        description='Delete Yandex Warehouse',
        tags=["Warehouse Yandex"],
        responses={200: {"message": "Claster is succesfully deleted"}},
    )
    def delete(self, requests: Request, warehouseyandex_id):
        claster = get_object_or_404(WarehouseYandex, id=warehouseyandex_id)
        claster.delete()
        return Response({"message": "Warehouse Yandex is succesfully deleted"}, status.HTTP_200_OK)
    
    @extend_schema(
        description='Create Yandex Werehouse and Claster',
        tags=["Warehouse Yandex"],
        responses={200: WarehouseSerializer()},
        request=ClasterSerializer,
        examples=[
        OpenApiExample(
            'Example 1',
            summary='Simple example',
            description='This is a simple example of input.',
            value={
                    "claster_to": "string",
                    "warehouse_id": 0
            },
            request_only=True,  # Only applicable for request bodies
        ),
    ]
    )
    def put(self,request: Request, warehouseyandex_id):
        claster = get_object_or_404(WarehouseYandex, id=warehouseyandex_id)
        company_id = claster.company.pk
        data = request.data.copy()
        data['company'] = company_id
        serializer = WarehouseSerializer(claster,data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    


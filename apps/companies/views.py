from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.companies.models import Company
from apps.companies.serializers import CompanySerializer, CompanyCreateAndUpdateSerializers, CompaniesSerializers


class CompaniesView(APIView):

    @swagger_auto_schema(
        operation_description="Get all companies",
        tags=['Company'],
        responses={200: CompanySerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        companies = Company.obj.get_user_companies(request.user)
        serializer = CompanySerializer(companies, many=True, context={'request': request})
        return Response(serializer.data)


class CompanyListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=CompanyCreateAndUpdateSerializers,
        operation_description="Get all companies",
        tags=['Company'],
        responses={200: CompanyCreateAndUpdateSerializers(many=True)}
    )
    def post(self, request, *args, **kwargs):
        serializer = CompanyCreateAndUpdateSerializers(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Get all companies",
        tags=['Company'],
        responses={200: CompanySerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        companies = Company.obj.get_user_companies(request.user)
        serializer = CompaniesSerializers(companies, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompanyDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all companies",
        tags=['Company'],
        responses={200: CompaniesSerializers(many=True)}
    )
    def get(self, request, *args, **kwargs):
        company = get_object_or_404(Company, uuid=kwargs.get('uuid'))
        serializer = CompaniesSerializers(company, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=CompanyCreateAndUpdateSerializers,
        operation_description="Update company",
        tags=['Company'],
        responses={200: CompanyCreateAndUpdateSerializers(many=True)}
    )
    def put(self, request, *args, **kwargs):
        company = get_object_or_404(Company, uuid=kwargs.get('uuid'))
        serializer = CompanyCreateAndUpdateSerializers(company, data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete company",
        tags=['Company'],
        responses={204: openapi.Response('No Content')}
    )
    def delete(self, request, *args, **kwargs):
        company = get_object_or_404(Company, uuid=kwargs.get('uuid'))
        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
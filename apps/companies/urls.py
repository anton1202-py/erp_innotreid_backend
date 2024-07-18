from django.urls import path
from apps.companies.views import *

urlpatterns = [

    # URL pattern for listing companies
    path('companies/login', CompaniesView.as_view(), name='company-list'),

    # URL pattern for creating companies
    path('companies/create', CompanyListView.as_view(), name='company-create'),

    # URL pattern for updating companies
    path('company/<uuid:uuid>/update_or_delete', CompanyDetailView.as_view(), name='company-update'),

]
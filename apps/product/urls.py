from django.urls import path
from .views import ClasterApiView, ClasterUpdateAndDeleteApiView, WarehouseApiView, WarehouseUpdateAndDeleteApiView
urlpatterns = [
    path('<uuid:company_id>', ClasterApiView.as_view(), name='claster'),
    path('<int:claster_id>', ClasterUpdateAndDeleteApiView.as_view(), name='claster-update-and-delete'),
    path('warehouse/<uuid:company_id>', WarehouseApiView.as_view(), name='warehouse'),
    path('warehouse/<int:warehouseyandex_id>', WarehouseUpdateAndDeleteApiView.as_view(), name='warehouse-update-and-delete'),
]
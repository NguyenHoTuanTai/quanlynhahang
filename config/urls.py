from django.contrib import admin
from django.urls import path
from core import views  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.trang_chu, name='trang_chu'),  

    path('mon/<int:mon_id>/', views.chi_tiet_mon, name='chi_tiet_mon'),
]
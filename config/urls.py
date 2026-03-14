from django.contrib import admin
from django.urls import path
from core import views  

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.trang_chu, name='trang_chu'),  

    path('mon/<int:mon_id>/', views.chi_tiet_mon, name='chi_tiet_mon'),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('redirect/', views.redirect_after_login, name='redirect'),
]


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
    path('dat-ban/', views.dat_ban_view, name='dat_ban'),
    path('thanh-toan/<int:dat_ban_id>/', views.thanh_toan_view, name='thanh_toan'),
    path('nhan-vien/', views.man_hinh_nhan_vien, name='man_hinh_nhan_vien'),
    path('quan-ly-dat-ban/', views.quan_ly_dat_ban, name='quan_ly_dat_ban'),
    path('dashboard/', views.man_hinh_nhan_vien, name='dashboard'),
    path('thuc-don/', views.thuc_don, name='thuc_don'),
    path('ban/<int:ban_id>/', views.chi_tiet_ban, name='chi_tiet_ban'),
    path('hoan-tat-dat-ban/', views.hoan_tat_dat_ban, name='hoan_tat_dat_ban'),
    path('register/', views.register, name='register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('tai-khoan/', views.tai_khoan, name='tai_khoan'),
    path('danh-gia/', views.danh_gia_view, name='danh_gia_view'),
    path('lich-su-dat/', views.lich_su_dat_ban_view, name='lich_su_dat_ban'),
]


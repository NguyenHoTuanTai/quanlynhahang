from django.contrib import admin
from django.urls import path
from core import views  

# Nhúng module xử lý đăng nhập/đăng xuất có sẵn của Django
from django.contrib.auth import views as auth_views

urlpatterns = [

    # Truy cập trang Admin mặc định của Django
    path('admin/', admin.site.urls),
    # Trang chủ mặc định khi vào web (VD: abc.com/)
    path('', views.trang_chu, name='trang_chu'),  
    
    # Trang danh sách toàn bộ menu thực đơn món ăn
    path('thuc-don/', views.thuc_don, name='thuc_don'),

    # Trang xem chi tiết 1 món ăn (có truyền id của món ăn vào URL)
    path('mon/<int:mon_id>/', views.chi_tiet_mon, name='chi_tiet_mon'),

    # Trang thông tin tài khoản cá nhân của người dùng
    path('tai-khoan/', views.tai_khoan, name='tai_khoan'),

    # Trang cho phép khách hàng viết đánh giá, nhận xét
    path('danh-gia/', views.danh_gia_view, name='danh_gia_view'),
    # Giao diện để khách hàng chọn ngày, giờ, số người đặt bàn
    path('dat-ban/', views.dat_ban_view, name='dat_ban'),

    # Trang thông báo thành công sau khi khách hoàn tất đặt bàn
    path('hoan-tat-dat-ban/', views.hoan_tat_dat_ban, name='hoan_tat_dat_ban'),

    # Xem danh sách lịch sử các đơn đã đặt của khách hàng
    path('lich-su-dat/', views.lich_su_dat_ban_view, name='lich_su_dat_ban'),

    # Màn hình chính tổng quan dành cho nhân viên
    path('nhan-vien/', views.man_hinh_nhan_vien, name='man_hinh_nhan_vien'),
    
    # Đường dẫn phụ 'dashboard' cũng trỏ về cùng một màn hình nhân viên ở trên
    path('dashboard/', views.man_hinh_nhan_vien, name='dashboard'), 

    # Màn hình để nhân viên xác nhận hoặc hủy các đơn khách vừa đặt
    path('quan-ly-dat-ban/', views.quan_ly_dat_ban, name='quan_ly_dat_ban'),

    # Xem chi tiết trạng thái của 1 bàn cụ thể trong nhà hàng
    path('ban/<int:ban_id>/', views.chi_tiet_ban, name='chi_tiet_ban'),

    # Trang đăng nhập (sử dụng giao diện login.html tự tạo)
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    # Xử lý đăng xuất, sau khi đăng xuất tự động chuyển hướng về trang chủ (/)
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # Trang chuyển hướng trung gian sau khi đăng nhập (để tự động phân quyền chia ra Admin/Nhân viên/Khách)
    path('redirect/', views.redirect_after_login, name='redirect'),

    # Trang đăng ký tài khoản mới cho khách hàng
    path('register/', views.register, name='register'),

    # Trang xử lý quên mật khẩu
    path('forgot-password/', views.forgot_password, name='forgot_password'),

    # xử lý nút thanh toán
    path('thanh-toan/<int:don_hang_id>/', views.xu_ly_thanh_toan, name='thanh_toan'),

    path('qr-thanh-toan/<int:don_hang_id>/', views.qr_thanh_toan_nhanh, name='qr_thanh_toan_nhanh'),
    path('api/kiem-tra-don/<int:don_hang_id>/', views.kiem_tra_trang_thai_don, name='kiem_tra_trang_thai_don'),
    path('thong-ke/', views.thong_ke, name='thong_ke'),
]
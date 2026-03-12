from django.shortcuts import render, get_object_or_404
from django.shortcuts import render
from .models import MonAn, LoaiMon  # Nhớ gọi thêm LoaiMon nhé

def trang_chu(request):
    # Lấy toàn bộ Loại món và Món ăn từ CSDL
    danh_sach_loai = LoaiMon.objects.all()
    danh_sach_mon = MonAn.objects.all()
    
    # Gói dữ liệu lại
    context = {
        'danh_sach_loai': danh_sach_loai,
        'danh_sach_mon': danh_sach_mon
    }
    return render(request, 'trang_chu.html', context)

def chi_tiet_mon(request, mon_id):
    # Tìm món ăn trong CSDL dựa vào ID
    mon = get_object_or_404(MonAn, id=mon_id)
    # Gửi dữ liệu món ăn đó sang trang HTML mới
    return render(request, 'chi_tiet_mon.html', {'mon': mon})
from django.shortcuts import render, redirect, get_object_or_404
from .models import MonAn, LoaiMon  
from .models import Ban, DatBan, DonHang, ChiTietDonHang
from django.http import HttpResponse
from django.contrib import messages
from datetime import datetime, timedelta
from django.contrib.auth.decorators import user_passes_test

from django.shortcuts import redirect

def trang_chu(request):
    danh_sach_loai = LoaiMon.objects.all()
    danh_sach_mon = MonAn.objects.all()
    
    context = {
        'danh_sach_loai': danh_sach_loai,
        'danh_sach_mon': danh_sach_mon
    }
    return render(request, 'trang_chu.html', context)

def chi_tiet_mon(request, mon_id):
    mon = get_object_or_404(MonAn, id=mon_id)
    return render(request, 'chi_tiet_mon.html', {'mon': mon})

def redirect_after_login(request):
    if request.user.is_staff:   # admin
        return redirect('/admin')
    else:                       # user thường
        return redirect('/')
    
def dat_ban_view(request):
    if request.method == 'POST':
        ten_khach = request.POST.get('ten_khach_hang')
        sdt = request.POST.get('so_dien_thoai')
        ngay = request.POST.get('ngay_dat')      
        gio_str = request.POST.get('gio_dat')     
        so_nguoi = request.POST.get('so_nguoi')
        ghi_chu = request.POST.get('ghi_chu', '')

        tien_coc = int(request.POST.get('tong_tien_coc', 0))

        if not so_nguoi:
            messages.error(request, "❌ Vui lòng nhập số người")
            return redirect('dat_ban')

        so_nguoi = int(so_nguoi)
        
        if tien_coc == 0:
            messages.error(request, "❌ Vui lòng chọn loại bàn trước khi đặt!")
            return redirect('dat_ban')
       
        DatBan.objects.create(
            ten_khach_hang=ten_khach,
            so_dien_thoai=sdt,
            ngay_dat=ngay,
            gio_dat=gio_str,
            so_nguoi=so_nguoi,
            ghi_chu=ghi_chu,
            tong_tien_coc=tien_coc,  
            ban=None,  
            trang_thai='ChoXacNhan'
        )

        messages.success(request, '✅ Đặt bàn thành công! Vui lòng chờ xác nhận.')
        return redirect('dat_ban')

    return render(request, 'dat_ban.html')
        
def thanh_toan_view(request, dat_ban_id):
    don = get_object_or_404(DatBan, id=dat_ban_id)
    
    if request.method == 'POST':
        don.trang_thai = 'DaCoc' 
        don.save()
        return HttpResponse(f"<h2> Đặt bàn thành công!</h2> <p>Cảm ơn {don.ten_khach_hang}. Bàn của bạn (ID: {don.id}) đã được giữ.</p>")
        
    return render(request, 'thanh_toan.html', {'don': don})


def kiem_tra_nhan_vien(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(kiem_tra_nhan_vien, login_url='/admin/login/')
def man_hinh_nhan_vien(request):

    danh_sach_ban = Ban.objects.all().order_by('so_ban')

    don_hang_dang_cho = DonHang.objects.exclude(
        trang_thai_don='DaThanhToan'
    ).order_by('-thoi_gian_tao')

    if request.method == "POST":
        action = request.POST.get("action")
        ban_id = request.POST.get("ban_id")

        if action == "pay" and ban_id:
            ban = Ban.objects.filter(id=ban_id).first()

            if ban:
                don = DonHang.objects.filter(
                    ban=ban,
                    trang_thai_don="DangPhucVu"
                ).first()

                if don:    

                    don.trang_thai_don = "DaThanhToan"
                    don.save()
                    
                    ban.trang_thai = "Trong"
                    ban.save()

        return redirect('man_hinh_nhan_vien')

    for don in don_hang_dang_cho:
        tong = 0
        chi_tiet_list = don.chitietdonhang_set.all()

        for item in chi_tiet_list:
            tong += item.so_luong * item.gia_luc_ban

        don.tong_tien = tong  

    return render(request, 'nhan_vien/dashboard.html', {
        'danh_sach_ban': danh_sach_ban,
        'don_hang_dang_cho': don_hang_dang_cho,
    })
def quan_ly_dat_ban(request):
    if request.method == "POST":
        id = request.POST.get('id')
        action = request.POST.get('action')
        ban_id = request.POST.get('ban_id')

        dat_ban = DatBan.objects.get(id=id)
        
        tien_coc = request.POST.get('tong_tien_coc')
        if tien_coc:
            dat_ban.tong_tien_coc = int(tien_coc)

        if action == "confirm":
            dat_ban.trang_thai = "DaXacNhan"

            if ban_id:
                dat_ban.ban_id = ban_id

                ban = Ban.objects.get(id=ban_id)
                ban.trang_thai = "DaDat"
                ban.save()

            dat_ban.save()

        elif action == "cancel":
            dat_ban.trang_thai = "DaHuy"

            if dat_ban.ban:
                ban = dat_ban.ban
                ban.trang_thai = "Trong"
                ban.save()

            dat_ban.save()

        elif action == "delete":
            dat_ban.delete()
            return redirect('quan_ly_dat_ban')  

        elif action == "change_table":
            if ban_id:
                # trả bàn cũ
                if dat_ban.ban:
                    ban_cu = dat_ban.ban
                    ban_cu.trang_thai = "Trong"
                    ban_cu.save()

                # gán bàn mới
                dat_ban.ban_id = ban_id

                ban_moi = Ban.objects.get(id=ban_id)
                ban_moi.trang_thai = "DaDat"
                ban_moi.save()

                dat_ban.save()

        return redirect('quan_ly_dat_ban')

    dat_ban_list = DatBan.objects.all().order_by('-id')
    ban_list = Ban.objects.all()

    return render(request, 'quan_ly_dat_ban.html', {
        'dat_ban_list': dat_ban_list,
        'ban_list': ban_list
    })

def thuc_don(request):
    danh_sach_loai = LoaiMon.objects.all()
    danh_sach_mon = MonAn.objects.all()

    # ===== GET PARAMS =====
    ban_id = request.GET.get("ban_id")
    loai_id = request.GET.get("loai")
    gia = request.GET.get("gia")

    # ===== FIX ban_id =====
    try:
        ban_id = int(ban_id)
    except (TypeError, ValueError):
        ban_id = None

    ban = Ban.objects.filter(id=ban_id).first() if ban_id else None

    # ===== FILTER =====
    if loai_id:
        danh_sach_mon = danh_sach_mon.filter(loai_mon_id=loai_id)

    if gia == "duoi100":
        danh_sach_mon = danh_sach_mon.filter(gia_ban__lt=100000)
    elif gia == "100-200":
        danh_sach_mon = danh_sach_mon.filter(gia_ban__gte=100000, gia_ban__lte=200000)
    elif gia == "tren200":
        danh_sach_mon = danh_sach_mon.filter(gia_ban__gt=200000)

    # ===== HANDLE POST =====
    if request.method == "POST":
        action = request.POST.get("action")
        post_ban_id = request.POST.get("ban_id")

        # fix ban_id POST
        try:
            post_ban_id = int(post_ban_id)
        except (TypeError, ValueError):
            return redirect("thuc_don")

        ban = Ban.objects.get(id=post_ban_id)

        don, _ = DonHang.objects.get_or_create(
            ban=ban,
            trang_thai_don="DangPhucVu"
        )

        # ===== ADD MÓN =====
        if action == "add":
            mon_id = request.POST.get("mon_id")
            mon = MonAn.objects.get(id=mon_id)

            chi_tiet, created = ChiTietDonHang.objects.get_or_create(
                don_hang=don,
                mon_an=mon,
                defaults={
                    "so_luong": 1,
                    "gia_luc_ban": mon.gia_ban
                }
            )

            if not created:
                chi_tiet.so_luong += 1
                chi_tiet.save()

            ban.trang_thai = "DangPhucVu"
            ban.save()

        # ===== UPDATE / DELETE =====
        elif action == "update_all":
            delete_id = request.POST.get("delete_id")

            if delete_id:
                ChiTietDonHang.objects.filter(id=delete_id).delete()
            else:
                chi_tiet_list = ChiTietDonHang.objects.filter(don_hang=don)

                for item in chi_tiet_list:
                    so_luong = request.POST.get(f"so_luong_{item.id}")

                    if so_luong:
                        so_luong = int(so_luong)

                        if so_luong <= 0:
                            item.delete()
                        else:
                            item.so_luong = so_luong
                            item.save()

            return redirect("chi_tiet_ban", ban_id=post_ban_id)

        # ===== REDIRECT SAU ADD =====
        params = []
        if post_ban_id:
            params.append(f"ban_id={post_ban_id}")
        if loai_id:
            params.append(f"loai={loai_id}")
        if gia:
            params.append(f"gia={gia}")

        query = "&".join(params)

        return redirect(f"/thuc-don/?{query}")

    # ===== CART =====
    chi_tiet_list = []
    tong_tien = 0

    if ban:
        don = DonHang.objects.filter(
            ban=ban,
            trang_thai_don="DangPhucVu"
        ).first()

        if don:
            chi_tiet_list = ChiTietDonHang.objects.filter(don_hang=don)

            for item in chi_tiet_list:
                tong_tien += item.so_luong * item.gia_luc_ban

    return render(request, "thuc_don.html", {
        "danh_sach_mon": danh_sach_mon,
        "danh_sach_loai": danh_sach_loai,
        "ban_id": ban_id,
        "ban": ban,
        "chi_tiet_list": chi_tiet_list,
        "tong_tien": tong_tien
    })
def chi_tiet_ban(request, ban_id):
    ban = get_object_or_404(Ban, id=ban_id)
    
    don = DonHang.objects.filter(
        ban=ban,
        trang_thai_don="DangPhucVu"
    ).first()
    
    if request.method == "POST":
        action = request.POST.get("action")
        mon_id = request.POST.get("mon_id")
        
        if action == "add" and not don:
            don = DonHang.objects.create(
                ban=ban,
                trang_thai_don="DangPhucVu"
            )
        
        if action == "add":
            mon = MonAn.objects.get(id=mon_id)

            chi_tiet, created = ChiTietDonHang.objects.get_or_create(
                don_hang=don,
                mon_an=mon,
                defaults={
                    'so_luong': 1,
                    'gia_luc_ban': mon.gia_ban
                }
            )

            if not created:
                chi_tiet.so_luong += 1
                chi_tiet.save()
            
            ban.trang_thai = "DangPhucVu"
            ban.save()
        
        elif action == "tang":
            chi_tiet = ChiTietDonHang.objects.filter(
                don_hang=don,
                mon_an_id=mon_id
            ).first()

            if chi_tiet:
                chi_tiet.so_luong += 1
                chi_tiet.save()

                ban.trang_thai = "DangPhucVu"
                ban.save()
        
        elif action == "giam":
            chi_tiet = ChiTietDonHang.objects.filter(
                don_hang=don,
                mon_an_id=mon_id
            ).first()

            if chi_tiet:
                if chi_tiet.so_luong > 1:
                    chi_tiet.so_luong -= 1
                    chi_tiet.save()
                else:
                    chi_tiet.delete()
        
        elif action == "remove":
            ChiTietDonHang.objects.filter(
                don_hang=don,
                mon_an_id=mon_id
            ).delete()
        
        elif action == "pay":
            if don:
                don.trang_thai_don = "DaThanhToan"
                don.save()

            ban.trang_thai = "Trong"
            ban.save()

            return redirect('dashboard')
        
        if don and not ChiTietDonHang.objects.filter(don_hang=don).exists():
            ban.trang_thai = "Trong"
            ban.save()

        return redirect('chi_tiet_ban', ban_id=ban_id)
    
    chi_tiet_list = []
    tong_tien = 0

    if don:
        chi_tiet_list = ChiTietDonHang.objects.filter(don_hang=don)
        tong_tien = sum(item.so_luong * item.gia_luc_ban for item in chi_tiet_list)

    return render(request, 'chi_tiet_ban.html', {
        'ban': ban,
        'don': don,
        'chi_tiet_list': chi_tiet_list,
        'tong_tien': tong_tien
    })
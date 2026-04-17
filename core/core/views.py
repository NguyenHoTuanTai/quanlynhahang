from django.shortcuts import render, redirect, get_object_or_404
from .models import MonAn, LoaiMon, DanhGia, ThanhToan
from .models import Ban, DatBan, DonHang, ChiTietDonHang, User, Profile, DanhGia
from django.http import HttpResponse
from django.contrib import messages
from datetime import datetime, timedelta
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import Avg
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from .models import DonHang, ThanhToan
import random
import string

def trang_chu(request):
    # Lấy toàn bộ Loại món và Món ăn từ Database
    danh_sach_loai = LoaiMon.objects.all()
    danh_sach_mon = MonAn.objects.all()
    
    # Lấy tham số tìm kiếm và lọc từ URL (VD: ?q=sup&loai=2)
    tu_khoa = request.GET.get('q', '')     
    loai_id = request.GET.get('loai', '')  

    # Nếu có từ khóa, lọc món ăn theo tên (icontains: tìm gần đúng, không phân biệt hoa thường)
    if tu_khoa:
        danh_sach_mon = danh_sach_mon.filter(ten_mon__icontains=tu_khoa) 
        
    # Nếu có ID loại món, lọc danh sách món theo ID đó
    if loai_id and loai_id.isdigit():
        danh_sach_mon = danh_sach_mon.filter(loai_mon_id=loai_id)

    # ĐOẠN NÀY DƯ THỪA: Đã lấy ở trên rồi, gọi lại sẽ làm mất kết quả filter ở trên
    # danh_sach_loai = LoaiMon.objects.all()
    # danh_sach_mon = MonAn.objects.all()

    danh_sach_mon_da_an = []
    if request.user.is_authenticated:
        # TODO: Cần logic lấy món user ĐÃ ĂN thật, hiện tại đang gán bừa bằng toàn bộ món
        danh_sach_mon_da_an = danh_sach_mon 

    # Nếu có form submit đánh giá gửi lên (Đang để pass, chưa viết logic)
    if request.method == 'POST' and 'submit_danh_gia' in request.POST:
        pass

    # Lấy tất cả đánh giá, kèm theo thông tin món ăn (select_related giúp query nhanh hơn)
    toan_bo_danh_gia = DanhGia.objects.select_related('mon_an').order_by('-thoi_gian_tao')
    
    tong_danh_gia = toan_bo_danh_gia.count()
    # Tính điểm trung bình, làm tròn 1 chữ số thập phân
    diem_trung_binh = round(toan_bo_danh_gia.aggregate(Avg('diem_danh_gia'))['diem_danh_gia__avg'], 1) if tong_danh_gia > 0 else 0.0

    # Phân trang: Mỗi trang hiện 5 đánh giá
    paginator = Paginator(toan_bo_danh_gia, 5) 
    page_number = request.GET.get('page') 
    page_obj = paginator.get_page(page_number)

    # đếm số sao đánh giá
    sao_5 = toan_bo_danh_gia.filter(diem_danh_gia=5).count()
    sao_4 = toan_bo_danh_gia.filter(diem_danh_gia=4).count()
    sao_3 = toan_bo_danh_gia.filter(diem_danh_gia=3).count()
    sao_2 = toan_bo_danh_gia.filter(diem_danh_gia=2).count()
    sao_1 = toan_bo_danh_gia.filter(diem_danh_gia=1).count()

    def tinh_pt(sao):
        return (sao / tong_danh_gia * 100) if tong_danh_gia > 0 else 0

    pt_5 = tinh_pt(sao_5)
    pt_4 = tinh_pt(sao_4)
    pt_3 = tinh_pt(sao_3)
    pt_2 = tinh_pt(sao_2)
    pt_1 = tinh_pt(sao_1)


    # Đóng gói dữ liệu gửi ra giao diện HTML
    context = {
        'danh_sach_loai': danh_sach_loai,
        'danh_sach_mon': danh_sach_mon,
        'page_obj': page_obj,                
        'tong_danh_gia': tong_danh_gia,        
        'diem_trung_binh': diem_trung_binh,    
        'danh_sach_mon_da_an': danh_sach_mon_da_an, 

        'sao_5': sao_5,
        'sao_4': sao_4,
        'sao_3': sao_3,
        'sao_2': sao_2,
        'sao_1': sao_1,

        'pt_5': pt_5,
        'pt_4': pt_4,
        'pt_3': pt_3,
        'pt_2': pt_2,
        'pt_1': pt_1,
    }
    return render(request, 'trang_chu.html', context)

def chi_tiet_mon(request, mon_id):
    # Tìm món ăn theo ID, nếu không thấy sẽ báo lỗi 404
    mon = get_object_or_404(MonAn, id=mon_id)
    return render(request, 'chi_tiet_mon.html', {'mon': mon})

def redirect_after_login(request):
    # Nếu đang dở dang việc đặt bàn trước khi login, điều hướng lại trang hoàn tất
    if 'tam_thoi_dat_ban' in request.session:
        return redirect('/hoan-tat-dat-ban/')

    # Admin thì vào trang quản trị, User thường thì về Trang chủ
    if request.user.is_staff:   
        return redirect('/admin')
    else:                       
        return redirect('/')
    
def dat_ban_view(request):
    if request.method == 'POST':
        # Lấy dữ liệu khách hàng nhập từ Form
        ten_khach = request.POST.get('ten_khach_hang')
        sdt = request.POST.get('so_dien_thoai')
        ngay = request.POST.get('ngay_dat')      
        gio_str = request.POST.get('gio_dat')     
        so_nguoi = request.POST.get('so_nguoi')
        ghi_chu = request.POST.get('ghi_chu', '')
        tien_coc = int(request.POST.get('tong_tien_coc', 0))

        if not so_nguoi:
            messages.error(request, "Vui lòng nhập số người")
            return redirect('dat_ban')

        so_nguoi = int(so_nguoi)
        
        if tien_coc == 0:
            messages.error(request, "Vui lòng chọn loại bàn trước khi đặt!")
            return redirect('dat_ban')

        # Validate ngày tháng: Không cho đặt lùi về ngày trong quá khứ
        try:
            ngay_dat_hop_le = datetime.strptime(ngay, '%Y-%m-%d').date()
            ngay_hien_tai = datetime.today().date()

            if ngay_dat_hop_le < ngay_hien_tai:
                messages.error(request, "Lỗi: Không thể đặt bàn cho ngày trong quá khứ!")
                return redirect('dat_ban')

        except ValueError:
            messages.error(request, "Lỗi: Ngày tháng bạn chọn không hợp lệ (Không tồn tại trên lịch)!")
            return redirect('dat_ban')
       
        # Nếu chưa đăng nhập, lưu tạm data vào Session rồi bắt đi đăng nhập
        if not request.user.is_authenticated:
            request.session['tam_thoi_dat_ban'] = {
                'ten_khach_hang': ten_khach,
                'so_dien_thoai': sdt,
                'ngay_dat': ngay,
                'gio_dat': gio_str,
                'so_nguoi': so_nguoi,
                'ghi_chu': ghi_chu,
                'tong_tien_coc': tien_coc
            }
            messages.warning(request, "Vui lòng đăng nhập tài khoản để hoàn tất đặt bàn!")
            return redirect('/login/') 
        
        # Nếu đã login, lưu thẳng Đơn đặt bàn vào DB
        DatBan.objects.create(
            user=request.user,
            ten_khach_hang=ten_khach,
            so_dien_thoai=sdt,
            ngay_dat=ngay,
            gio_dat=gio_str,
            so_nguoi=so_nguoi,
            ghi_chu=ghi_chu,
            tong_tien_coc=tien_coc,  
            ban=None,  # Chờ nhân viên xếp bàn sau
            trang_thai='ChoXacNhan'
        )

        messages.success(request, '✅ Đặt bàn thành công! Vui lòng chờ xác nhận.')
        return redirect('dat_ban')

    return render(request, 'dat_ban.html')


# Decorator kiểm tra quyền truy cập: Chỉ nhân viên (is_staff) mới được vào
def kiem_tra_nhan_vien(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(kiem_tra_nhan_vien, login_url='/admin/login/')
def man_hinh_nhan_vien(request):
    # Lấy danh sách bàn xếp theo số thứ tự
    danh_sach_ban = Ban.objects.all().order_by('so_ban')

    # Lấy các đơn hàng Đang phục vụ (chưa thanh toán)
    don_hang_dang_cho = DonHang.objects.exclude(
        trang_thai_don='DaThanhToan'
    ).order_by('-thoi_gian_tao')

    # Xử lý các thao tác của nhân viên (VD: Bấm nút Thanh toán)
    if request.method == "POST":
        action = request.POST.get("action")
        ban_id = request.POST.get("ban_id")

        # Xử lý nút thanh toán
        if action == "pay" and ban_id:
            ban = Ban.objects.filter(id=ban_id).first()

            if ban:
                # Tìm đơn hàng đang phục vụ của bàn đó
                don = DonHang.objects.filter(
                    ban=ban,
                    trang_thai_don="DangPhucVu"
                ).first()

                if don:    
                    # Cập nhật lại trạng thái Đơn = Đã thanh toán, Bàn = Trống
                    don.trang_thai_don = "DaThanhToan"
                    don.save()
                    
                    ban.trang_thai = "Trong"
                    ban.save()

        return redirect('man_hinh_nhan_vien')

    # Tính tổng tiền cho từng đơn hàng đang chờ
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
    # View dùng cho Admin/Nhân viên quản lý các booking của khách
    if request.method == "POST":
        id = request.POST.get('id')
        action = request.POST.get('action')
        ban_id = request.POST.get('ban_id')

        dat_ban = DatBan.objects.get(id=id)
        
        # Cập nhật tiền cọc
        tien_coc = request.POST.get('tong_tien_coc')
        if tien_coc:
            dat_ban.tong_tien_coc = int(tien_coc)

        # Xử lý nút: Xác nhận đơn đặt bàn
        if action == "confirm":
            dat_ban.trang_thai = "DaXacNhan"

            # Nếu có gán bàn luôn thì set trạng thái Bàn đó thành Đã Đặt
            if ban_id:
                dat_ban.ban_id = ban_id
                ban = Ban.objects.get(id=ban_id)
                ban.trang_thai = "DaDat"
                ban.save()

            dat_ban.save()

        # Xử lý nút: Hủy đặt bàn
        elif action == "cancel":
            dat_ban.trang_thai = "DaHuy"

            # Nếu đơn đó đã được gán bàn, thì nhả cái bàn đó ra (trở về Trống)
            if dat_ban.ban:
                ban = dat_ban.ban
                ban.trang_thai = "Trong"
                ban.save()

            dat_ban.save()

        # Xử lý nút: Xóa hẳn đơn khỏi hệ thống
        elif action == "delete":
            dat_ban.delete()
            return redirect('quan_ly_dat_ban')  

        # Xử lý nút: Đổi sang bàn khác
        elif action == "change_table":
            if ban_id:
                # 1. Trả lại bàn cũ
                if dat_ban.ban:
                    ban_cu = dat_ban.ban
                    ban_cu.trang_thai = "Trong"
                    ban_cu.save()

                # 2. Gán bàn mới vào đơn và cập nhật trạng thái bàn mới
                dat_ban.ban_id = ban_id
                ban_moi = Ban.objects.get(id=ban_id)
                ban_moi.trang_thai = "DaDat"
                ban_moi.save()

                dat_ban.save()

        return redirect('quan_ly_dat_ban')

    # Lấy list booking mới nhất đưa lên đầu
    dat_ban_list = DatBan.objects.all().order_by('-id')
    ban_list = Ban.objects.all()

    return render(request, 'quan_ly_dat_ban.html', {
        'dat_ban_list': dat_ban_list,
        'ban_list': ban_list
    })

def thuc_don(request):
    # Lấy dữ liệu cơ bản để hiển thị Menu
    danh_sach_loai = LoaiMon.objects.all()
    danh_sach_mon = MonAn.objects.all()

    # ===== GET PARAMS =====
    ban_id = request.GET.get("ban_id")
    loai_id = request.GET.get("loai")
    gia = request.GET.get("gia")

    # ===== FIX ban_id =====
    # Ép kiểu ban_id, bỏ qua nếu lỗi (tránh crash khi URL bị sửa bậy)
    try:
        ban_id = int(ban_id)
    except (TypeError, ValueError):
        ban_id = None

    ban = Ban.objects.filter(id=ban_id).first() if ban_id else None

    # ===== FILTER =====
    # Lọc danh sách món ăn theo Loại và Khoảng giá
    if loai_id:
        danh_sach_mon = danh_sach_mon.filter(loai_mon_id=loai_id)

    if gia == "duoi100":
        danh_sach_mon = danh_sach_mon.filter(gia_ban__lt=100000)
    elif gia == "100-200":
        danh_sach_mon = danh_sach_mon.filter(gia_ban__gte=100000, gia_ban__lte=200000)
    elif gia == "tren200":
        danh_sach_mon = danh_sach_mon.filter(gia_ban__gt=200000)

    # ===== HANDLE POST =====
    # Xử lý khi nhân viên thao tác Thêm món hoặc Cập nhật giỏ hàng
    if request.method == "POST":
        action = request.POST.get("action")
        post_ban_id = request.POST.get("ban_id")

        try:
            post_ban_id = int(post_ban_id)
        except (TypeError, ValueError):
            return redirect("thuc_don")

        ban = Ban.objects.get(id=post_ban_id)

        # Lấy đơn hàng đang phục vụ của bàn, nếu chưa có thì tự động tạo mới
        don, _ = DonHang.objects.get_or_create(
            ban=ban,
            trang_thai_don="DangPhucVu"
        )

        # ===== ADD MÓN =====
        if action == "add":
            mon_id = request.POST.get("mon_id")
            mon = MonAn.objects.get(id=mon_id)

            # Thêm món vào chi tiết, nếu đã tồn tại thì cộng dồn số lượng
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

        # Xóa món hoặc cập nhật số lượng hàng loạt từ giỏ hàng
        elif action == "update_all":
            delete_id = request.POST.get("delete_id")

            if delete_id:
                ChiTietDonHang.objects.filter(id=delete_id).delete()

                
                return redirect(f"/thuc-don/?ban_id={post_ban_id}")

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
        # Giữ nguyên các tham số filter trên URL sau khi reload trang
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
    # Tính tổng tiền và danh sách món của bàn hiện tại để hiển thị giỏ hàng
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
        
        # Nhóm xử lý các thao tác tương tác với món ăn trong chi tiết bàn
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
            chi_tiet = ChiTietDonHang.objects.filter(don_hang=don, mon_an_id=mon_id).first()
            if chi_tiet:
                chi_tiet.so_luong += 1
                chi_tiet.save()
                ban.trang_thai = "DangPhucVu"
                ban.save()
        
        elif action == "giam":
            chi_tiet = ChiTietDonHang.objects.filter(don_hang=don, mon_an_id=mon_id).first()
            if chi_tiet:
                if chi_tiet.so_luong > 1:
                    chi_tiet.so_luong -= 1
                    chi_tiet.save()
                else:
                    chi_tiet.delete() # Xóa món nếu giảm số lượng về 0
        
        elif action == "remove":
            ChiTietDonHang.objects.filter(don_hang=don, mon_an_id=mon_id).delete()
        
        elif action == "pay":
            # Xử lý nút Thanh Toán: Chốt đơn và giải phóng bàn
            if don:
                don.trang_thai_don = "DaThanhToan"
                don.save()

            ban.trang_thai = "Trong"
            ban.save()
            return redirect('dashboard')
        
        # Đề phòng trường hợp xóa hết món trong đơn thì tự động trả bàn về Trống
        if don and not ChiTietDonHang.objects.filter(don_hang=don).exists():
            ban.trang_thai = "Trong"
            ban.save()

        return redirect('chi_tiet_ban', ban_id=ban_id)
    
    # Render dữ liệu ra file HTML
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

# Ràng buộc phải login mới được gọi hàm này
@login_required(login_url='/login/')
def hoan_tat_dat_ban(request):
    list(messages.get_messages(request)) # Clear messages rác

    # Lấy thông tin đặt bàn lưu tạm ở Session (do lúc đặt khách chưa login)
    if 'tam_thoi_dat_ban' in request.session:
        data = request.session['tam_thoi_dat_ban']
        
        # Tạo đơn đặt bàn chính thức vào DB
        DatBan.objects.create(
            ten_khach_hang=data['ten_khach_hang'],
            so_dien_thoai=data['so_dien_thoai'],
            ngay_dat=data['ngay_dat'],
            gio_dat=data['gio_dat'],
            so_nguoi=data['so_nguoi'],
            ghi_chu=data['ghi_chu'],
            tong_tien_coc=data['tong_tien_coc'],
            ban=None,
            trang_thai='ChoXacNhan'
        )
        
        # Xóa Session tạm sau khi lưu thành công
        del request.session['tam_thoi_dat_ban']
        messages.success(request, 'Đăng nhập và Đặt bàn thành công! Vui lòng chờ xác nhận.')
    
    return redirect('dat_ban') 



def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # check mật khẩu
        if password1 != password2:
            messages.error(request, "Mật khẩu không khớp")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email đã tồn tại")
            return redirect("register")

        # validate password
        try:
            validate_password(password1)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        messages.success(request, "Đăng ký thành công!")
        return redirect("login")

    return render(request, "register.html")

def forgot_password(request):
    new_password = None

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        try:
            user = User.objects.get(username=username, email=email)

            # tạo mật khẩu mới
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            # cập nhật mật khẩu
            user.set_password(new_password)
            user.save()

            messages.success(request, "Đã tạo mật khẩu mới!")

        except User.DoesNotExist:
            messages.error(request, "Sai tài khoản hoặc email!")

    return render(request, "forgot_password.html", {
        "new_password": new_password
    })

# Bắt buộc phải đăng nhập mới được vào xem thông tin tài khoản
@login_required
def tai_khoan(request):
    # Lấy thông tin Profile của user, nếu chưa có thì tự động tạo mới
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # NHÁNH 1: XỬ LÝ CẬP NHẬT THÔNG TIN CÁ NHÂN
        if "doi_mat_khau" not in request.POST:
            request.user.email = request.POST.get("email")
            profile.so_dien_thoai = request.POST.get("so_dien_thoai")
            profile.dia_chi = request.POST.get("dia_chi")

            request.user.save() # Lưu vào bảng User mặc định của Django
            profile.save()      # Lưu vào bảng Profile mở rộng

            messages.success(request, "Cập nhật thành công!")
        
        # NHÁNH 2: XỬ LÝ ĐỔI MẬT KHẨU
        else:
            old = request.POST.get("mat_khau_cu")
            new = request.POST.get("mat_khau_moi")

            # Kiểm tra xem mật khẩu cũ nhập vào có đúng không
            if request.user.check_password(old):
                request.user.set_password(new)
                request.user.save()
                messages.success(request, "Đổi mật khẩu thành công!")
                
                # Sau khi đổi pass, Django sẽ tự đăng xuất, nên cần redirect về trang login
                return redirect("/login/")
            else:
                messages.error(request, "Mật khẩu cũ không đúng!")

    return render(request, "tai_khoan.html", {"profile": profile})

def danh_gia_view(request):
    # Xử lý khi khách hàng bấm gửi đánh giá
    if request.method == "POST":
        ten_khach_hang = request.POST.get("ten_khach_hang")
        mon_an_id = request.POST.get("mon_an")
        diem_danh_gia = request.POST.get("diem_danh_gia")
        noi_dung = request.POST.get("noi_dung")

        # Đảm bảo nhập đủ thông tin mới cho lưu
        if ten_khach_hang and mon_an_id and diem_danh_gia and noi_dung:
            mon_an = MonAn.objects.get(id=mon_an_id)
            DanhGia.objects.create(
                ten_khach_hang=ten_khach_hang,
                mon_an=mon_an,
                diem_danh_gia=int(diem_danh_gia),
                noi_dung=noi_dung
            )

            messages.success(request, "🎉 Gửi đánh giá thành công!")
            return redirect('danh_gia_view')

        else:
            messages.error(request, "Vui chọn sao")

    # Hiển thị form đánh giá và danh sách các đánh giá cũ (mới nhất lên đầu)
    mon_ans = MonAn.objects.all()
    danh_gias = DanhGia.objects.all().order_by('-thoi_gian_tao')
    
    return render(request, 'danh_gia.html', {
        'mon_ans': mon_ans,
        'danh_gias': danh_gias
    })

def lich_su_dat_ban_view(request):
    # Lọc ra danh sách đặt bàn CỦA RIÊNG user đang đăng nhập, xếp theo thứ tự mới nhất
    don_dat_ban = DatBan.objects.filter(user=request.user).order_by('-id')

    return render(request, 'lich_su_dat_ban.html', {
        'don_dat_ban': don_dat_ban
    })

def thanh_toan_don(request, don_id):
    # Lấy thông tin đơn hàng và chi tiết các món đã gọi
    don = get_object_or_404(DonHang, id=don_id)
    
    # Lấy danh sách chi tiết đơn (Tùy tên related_name của bồ)
    chi_tiet_don = don.chitietdonhang_set.all() 

    # Lấy thông tin khách hàng
    khach_hang = getattr(don, 'khach_hang', None)

    # Tính toán các khoản tiền CƠ BẢN
    tong_tien_mon = sum(item.thanh_tien for item in chi_tiet_don)
    thue_vat = round(tong_tien_mon * 8 / 100) # Thuế VAT 8%
    
    # Tính toán ƯU ĐÃI THÀNH VIÊN
    giam_gia_thanh_vien = 0
    if khach_hang and hasattr(khach_hang, 'hang_thanh_vien'):
        if khach_hang.hang_thanh_vien.ten_hang == 'Vàng':
            giam_gia_thanh_vien = int(tong_tien_mon * 0.10)
        elif khach_hang.hang_thanh_vien.ten_hang == 'Bạc':
            giam_gia_thanh_vien = int(tong_tien_mon * 0.05)

    # Các biến mặc định cho Voucher
    giam_gia_voucher = 0
    thong_bao_voucher = ""
    voucher_code = ""

    # XỬ LÝ KHI NGƯỜI DÙNG BẤM NÚT (POST REQUEST)
    if request.method == 'POST':
        action = request.POST.get('action')

        # Hành động 1: Nhập mã Voucher và bấm "Áp dụng"
        if action == 'ap_dung_voucher':
            voucher_code = request.POST.get('voucher_code', '').strip()
            
            # Tạm thời để hardcode demo, sau này bồ nối với bảng Voucher thật
            if voucher_code == "GIAM50K":
                giam_gia_voucher = 50000
                thong_bao_voucher = "Áp dụng mã giảm 50K thành công!"
            elif voucher_code == "FREESHIP":
                thong_bao_voucher = "Mã này chỉ dùng cho đơn mang về!"
            elif voucher_code != "":
                thong_bao_voucher = "Mã giảm giá không hợp lệ hoặc đã hết hạn!"

        # Hành động 2: Bấm nút "Xác nhận thanh toán" chốt đơn
        elif action == 'chot_don_thanh_toan':
            # Lấy phương thức thanh toán khách chọn
            phuong_thuc = request.POST.get('phuong_thuc', 'TienMat')
            kieu_thanh_toan = "Tiền mặt" if phuong_thuc == "TienMat" else "Chuyển khoản (QR)"
            
            # Cập nhật trạng thái Đơn hàng (Đã sửa thành trang_thai_don theo chuẩn DB của bồ)
            don.trang_thai_don = 'DaThanhToan' 
            don.save()

            # Giải phóng bàn (đổi màu xanh trên sơ đồ)
            if don.ban:
                don.ban.trang_thai = 'Trong' # Hoặc 'Trống' tùy chữ gán trong database
                don.ban.save()

            # Cộng điểm tích lũy cho khách hàng (nếu có)
            if khach_hang:
                # Quy tắc: 10.000đ = 1 điểm
                tong_thanh_toan_cuoi = tong_tien_mon + thue_vat - giam_gia_thanh_vien - float(request.POST.get('giam_gia_voucher_hidden', 0))
                diem_cong_them = int(tong_thanh_toan_cuoi / 10000)
                
                khach_hang.diem_tich_luy += diem_cong_them
                khach_hang.save()

            # BẮN THÔNG BÁO THÀNH CÔNG GỒM PHƯƠNG THỨC THANH TOÁN!
            messages.success(request, f"🎉 Thanh toán thành công đơn #{don.id} bằng {kieu_thanh_toan}!")
            
            return redirect('/nhan-vien/') 

    # CHUẨN BỊ DỮ LIỆU HIỂN THỊ RA GIAO DIỆN
    tong_thanh_toan = tong_tien_mon + thue_vat - giam_gia_thanh_vien - giam_gia_voucher
    
    if tong_thanh_toan < 0:
        tong_thanh_toan = 0

    # Dự kiến số điểm khách sẽ nhận được
    diem_tich_luy_du_kien = int(tong_thanh_toan / 10000) if khach_hang else 0

    context = {
        'don': don,
        'chi_tiet_don': chi_tiet_don,
        'khach_hang': khach_hang,
        'tong_tien_mon': tong_tien_mon,
        'thue_vat': thue_vat,
        'giam_gia_thanh_vien': giam_gia_thanh_vien,
        'giam_gia_voucher': giam_gia_voucher,
        'thong_bao_voucher': thong_bao_voucher,
        'tong_thanh_toan': tong_thanh_toan,
        'diem_tich_luy_du_kien': diem_tich_luy_du_kien,
    }

    return render(request, 'thanh_toan.html', context)






def xu_ly_thanh_toan(request, don_hang_id):
    don_hang = get_object_or_404(DonHang, id=don_hang_id)
    chi_tiet_don = don_hang.chitietdonhang_set.all()
    
    # 1. TÍNH TIỀN CƠ BẢN VÀ THUẾ VAT (8%)
    tong_tien_mon = sum(item.thanh_tien for item in chi_tiet_don)
    thue_vat = int(float(tong_tien_mon) * 0.08)
    
    giam_gia_voucher = 0
    thong_bao_khach = ""
    thong_bao_voucher = ""

    if request.method == 'POST':
        action = request.POST.get('action')

        # --- LUÔN KIỂM TRA VOUCHER ĐẦU TIÊN ---
        ma_voucher = request.POST.get('voucher_code', '').strip()
        if ma_voucher == 'GIAM50K':
            giam_gia_voucher = 50000
            thong_bao_voucher = "✅ Đã áp dụng mã GIAM50K (-50.000đ)"
        elif ma_voucher != '':
            thong_bao_voucher = "❌ Mã giảm giá không hợp lệ hoặc đã hết hạn!"

        # --- NÚT 1: TÌM KHÁCH HÀNG BẰNG SĐT ---
        if action == 'tim_khach_hang':
            # Dùng replace để triệt tiêu mọi khoảng trắng lỡ tay gõ dư
            sdt_nhap = request.POST.get('so_dien_thoai', '').strip().replace(" ", "")
            
            if not sdt_nhap:
                thong_bao_khach = "⚠️ Vui lòng nhập số điện thoại!"
                don_hang.khach_hang = None
                don_hang.save()
            else:
                # Bắt đầu tìm trong bảng Profile
                khach = Profile.objects.filter(so_dien_thoai=sdt_nhap).first()
                
                if khach:
                    don_hang.khach_hang = khach
                    don_hang.save()
                    # Thêm thông báo thành công cho nhân viên yên tâm
                    thong_bao_khach = f"✅ Đã tìm thấy khách: {khach.user.username}" 
                else:
                    don_hang.khach_hang = None
                    don_hang.save()
                    thong_bao_khach = f"❌ Không tìm thấy khách hàng với SĐT '{sdt_nhap}'!"

        # --- NÚT 2: CHỐT ĐƠN THANH TOÁN ---
        elif action == 'chot_don_thanh_toan':
            giam_gia_tv_chot = 0
            if don_hang.khach_hang and don_hang.khach_hang.hang_thanh_vien:
                phan_tram = don_hang.khach_hang.hang_thanh_vien.phan_tram_giam_gia or 0
                giam_gia_tv_chot = int(float(tong_tien_mon) * (phan_tram / 100.0))
            
            tong_thanh_toan_chot = float(tong_tien_mon) + thue_vat - giam_gia_tv_chot - giam_gia_voucher
            tong_thanh_toan_chot = max(0, int(tong_thanh_toan_chot)) 

            phuong_thuc = request.POST.get('phuong_thuc', 'TienMat')
            
            # Đổi tên hiển thị cho đẹp để đưa vào thông báo
            kieu_thanh_toan = "Tiền mặt" if phuong_thuc == "TienMat" else "Chuyển khoản (QR)"

            thanh_toan, created = ThanhToan.objects.get_or_create(don_hang=don_hang)
            thanh_toan.phuong_thuc = phuong_thuc
            thanh_toan.trang_thai_thanh_toan = 'Đã thanh toán'
            thanh_toan.thoi_gian_thanh_toan = timezone.now()
            thanh_toan.save()

            don_hang.tong_tien = tong_thanh_toan_chot
            don_hang.trang_thai_don = 'DaThanhToan'
            
            if don_hang.ban:
                don_hang.ban.trang_thai = 'Trong' 
                don_hang.ban.save()
            don_hang.save()
            
            if don_hang.khach_hang:
                diem_cong = int(tong_thanh_toan_chot / 100000)
                don_hang.khach_hang.diem_tich_luy += diem_cong
                don_hang.khach_hang.save()
            
            
            dat_ban = DatBan.objects.filter(ban=don_hang.ban_id).first()

            if dat_ban:
                dat_ban.trang_thai = 'DaThanhToan'
                dat_ban.save()

            # 🔥 BẮN THÔNG BÁO THÀNH CÔNG VÀ CHUYỂN HƯỚNG VỀ ĐÚNG TRANG SƠ ĐỒ BÀN
            messages.success(request, f"Thanh toán thành công đơn #{don_hang.id} bằng {kieu_thanh_toan}!")
            return redirect('dashboard') 

    # 2. TÍNH TOÁN LẠI ĐỂ HIỂN THỊ RA GIAO DIỆN MỖI LẦN TẢI
    giam_gia_thanh_vien = 0
    if don_hang.khach_hang and don_hang.khach_hang.hang_thanh_vien:
        phan_tram = don_hang.khach_hang.hang_thanh_vien.phan_tram_giam_gia or 0
        giam_gia_thanh_vien = int(float(tong_tien_mon) * (phan_tram / 100.0))

    tong_thanh_toan = float(tong_tien_mon) + thue_vat - giam_gia_thanh_vien - giam_gia_voucher
    tong_thanh_toan = max(0, int(tong_thanh_toan))
    
    diem_tich_luy_du_kien = int(tong_thanh_toan / 100000) if don_hang.khach_hang else 0

    context = {
        'don': don_hang,
        'chi_tiet_don': chi_tiet_don,
        'khach_hang': don_hang.khach_hang,
        'tong_tien_mon': tong_tien_mon,
        'thue_vat': thue_vat,
        'giam_gia_thanh_vien': giam_gia_thanh_vien,
        'giam_gia_voucher': int(giam_gia_voucher),
        'tong_thanh_toan': tong_thanh_toan,
        'diem_tich_luy_du_kien': diem_tich_luy_du_kien,
        'thong_bao_khach': thong_bao_khach,
        'thong_bao_voucher': thong_bao_voucher
    }
    return render(request, 'thanh_toan.html', context)
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from cloudinary.models import CloudinaryField
# -------------------------------------------------------------
# CÁC BẢNG HỆ THỐNG MẶC ĐỊNH (Không cần thay đổi)
# -------------------------------------------------------------
class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)
    class Meta:
        managed = False
        db_table = 'auth_group'

class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)
    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)

class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)

class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'auth_user'

class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)

class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)
    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)

class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    class Meta:
        managed = False
        db_table = 'django_admin_log'

class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)

class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'django_migrations'

class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'django_session'


# -------------------------------------------------------------
# CÁC BẢNG NGHIỆP VỤ (Đã thêm ràng buộc chặt chẽ)
# -------------------------------------------------------------

class Ban(models.Model):
    TRANG_THAI_CHOICES = [
        ('Trong', 'Trống'),
        ('DaDat', 'Đã đặt'),
        ('DangSuDung', 'Đang sử dụng'),
    ]
    so_ban = models.CharField(unique=True, max_length=20, verbose_name="Số bàn")
    so_ghe = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Số ghế") # Số ghế phải >= 1
    trang_thai = models.CharField(max_length=50, choices=TRANG_THAI_CHOICES, default='Trong', verbose_name="Trạng thái")

    class Meta:
        managed = False
        db_table = 'ban'
        verbose_name = 'Bàn'
        verbose_name_plural = 'Quản lý Bàn'

    def __str__(self):
        return f"Bàn {self.so_ban}"


class LoaiMon(models.Model):
    ten_loai = models.CharField(max_length=100, unique=True, verbose_name="Tên loại")
    mo_ta = models.TextField(blank=True, null=True, verbose_name="Mô tả")

    class Meta:
        managed = False
        db_table = 'loai_mon'
        verbose_name = 'Loại món'
        verbose_name_plural = 'Quản lý Loại món'

    def __str__(self):
        return f"Loại: {self.ten_loai}"


class MonAn(models.Model):
    loai_mon = models.ForeignKey(LoaiMon, models.DO_NOTHING, verbose_name="Loại món")
    ten_mon = models.CharField(max_length=200, verbose_name="Tên món")
    mo_ta = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    gia_ban = models.DecimalField(max_digits=18, decimal_places=0, validators=[MinValueValidator(0)], verbose_name="Giá bán") # Giá không được âm
    

    hinh_anh = CloudinaryField(
        'image',
        folder='mon_an',
        blank=True,
        null=True
    )
    trang_thai_ban = models.BooleanField(default=True, verbose_name="Đang mở bán")

    class Meta:
        managed = False
        db_table = 'mon_an'
        verbose_name = 'Món ăn'
        verbose_name_plural = 'Quản lý Món ăn'

    def __str__(self):
        return self.ten_mon


class HangThanhVien(models.Model):
    ten_hang = models.CharField(max_length=50, unique=True, verbose_name="Tên hạng")
    phan_tram_giam_gia = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)], # Chỉ từ 0 -> 100%
        verbose_name="% Giảm giá"
    )
    diem_toi_thieu = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name="Điểm tối thiểu")

    class Meta:
        managed = True
        db_table = 'hang_thanh_vien'
        verbose_name = 'Hạng thành viên'
        verbose_name_plural = 'Quản lý Hạng thành viên'

    def __str__(self):
        return self.ten_hang


class DonHang(models.Model):
    TRANG_THAI_CHOICES = [
        ('ChoXacNhan', 'Chờ xác nhận'),
        ('DangChuanBi', 'Đang chuẩn bị'),
        ('HoanThanh', 'Hoàn thành'),
        ('DaHuy', 'Đã hủy'),
    ]
    ban = models.ForeignKey(Ban, models.DO_NOTHING, blank=True, null=True, verbose_name="Bàn")
    nhan_vien = models.ForeignKey('NhanVien', models.DO_NOTHING, blank=True, null=True, verbose_name="Nhân viên tạo")
    khach_hang = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Khách hàng")
    trang_thai_don = models.CharField(max_length=50, choices=TRANG_THAI_CHOICES, default='ChoXacNhan', verbose_name="Trạng thái đơn")
    tong_tien = models.DecimalField(max_digits=18, decimal_places=0, default=0, validators=[MinValueValidator(0)], verbose_name="Tổng tiền gốc")
    thoi_gian_tao = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian tạo")
    
    voucher = models.ForeignKey('Voucher', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Voucher áp dụng")
    tien_giam_gia = models.DecimalField(max_digits=18, decimal_places=0, default=0, validators=[MinValueValidator(0)], verbose_name="Tiền được giảm")

    class Meta:
        managed = True
        db_table = 'don_hang'
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Quản lý Đơn hàng'

    def __str__(self):
        return f"Đơn hàng #{self.id}"

    def clean(self):
        # Ràng buộc: Tiền giảm giá không được lớn hơn tổng tiền gốc
        if self.tong_tien and self.tien_giam_gia:
            if self.tien_giam_gia > self.tong_tien:
                raise ValidationError({'tien_giam_gia': 'Tiền giảm giá không được lớn hơn tổng tiền của đơn hàng.'})

    @property
    def tong_thanh_toan(self):
        tien_goc = self.tong_tien if self.tong_tien else 0
        tien_giam = self.tien_giam_gia if self.tien_giam_gia else 0
        thanh_toan = tien_goc - tien_giam
        return thanh_toan if thanh_toan > 0 else 0


class ChiTietDonHang(models.Model):
    don_hang = models.ForeignKey(DonHang, models.DO_NOTHING, verbose_name="Đơn hàng")
    mon_an = models.ForeignKey(MonAn, models.DO_NOTHING, verbose_name="Món ăn")
    so_luong = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Số lượng") # Số lượng >= 1
    gia_luc_ban = models.DecimalField(max_digits=18, decimal_places=0, validators=[MinValueValidator(0)], verbose_name="Giá lúc bán")
    ghi_chu = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ghi chú thêm")

    class Meta:
        managed = False
        db_table = 'chi_tiet_don_hang'
        verbose_name = 'Chi tiết đơn hàng'
        verbose_name_plural = 'Quản lý Chi tiết đơn hàng'

    def __str__(self):
        return f"Chi tiết #{self.id} - Đơn {self.don_hang_id}"

    @property
    def thanh_tien(self):
        return self.so_luong * self.gia_luc_ban


class DanhGia(models.Model):
    mon_an = models.ForeignKey(MonAn, models.DO_NOTHING, verbose_name="Món ăn")
    ten_khach_hang = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tên khách")
    diem_danh_gia = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], # Điểm chỉ từ 1 đến 5 sao
        verbose_name="Điểm (1-5)"
    )
    noi_dung = models.TextField(blank=True, null=True, verbose_name="Nội dung")
    thoi_gian_tao = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian")

    class Meta:
        managed = False
        db_table = 'danh_gia'
        verbose_name = 'Đánh giá'
        verbose_name_plural = 'Quản lý Đánh giá'

    def __str__(self):
        return f"Đánh giá {self.diem_danh_gia} Sao - Món {self.mon_an.ten_mon}"


class NhanVien(models.Model):
    ho_ten = models.CharField(max_length=150, verbose_name="Họ và tên")
    vi_tri = models.CharField(max_length=50, blank=True, null=True, verbose_name="Vị trí/Chức vụ")
    so_dien_thoai = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name="Email") # Dùng EmailField để chuẩn format
    ngay_vao_lam = models.DateField(blank=True, null=True, verbose_name="Ngày vào làm")

    class Meta:
        managed = False
        db_table = 'nhan_vien'
        verbose_name = 'Nhân viên'
        verbose_name_plural = 'Quản lý Nhân viên'

    def __str__(self):
        return f"NV: {self.ho_ten}"


class ThanhToan(models.Model):
    PHUONG_THUC_CHOICES = [
        ('TienMat', 'Tiền mặt'),
        ('ChuyenKhoan', 'Chuyển khoản'),
        ('The', 'Thẻ ngân hàng'),
    ]
    TRANG_THAI_TT_CHOICES = [
        ('ChuaThanhToan', 'Chưa thanh toán'),
        ('DaThanhToan', 'Đã thanh toán'),
        ('HoanTien', 'Đã hoàn tiền'),
    ]
    don_hang = models.OneToOneField(DonHang, models.DO_NOTHING, verbose_name="Đơn hàng")
    phuong_thuc = models.CharField(max_length=50, choices=PHUONG_THUC_CHOICES, default='TienMat', verbose_name="Phương thức")
    trang_thai_thanh_toan = models.CharField(max_length=50, choices=TRANG_THAI_TT_CHOICES, default='ChuaThanhToan', verbose_name="Trạng thái")
    thoi_gian_thanh_toan = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian TT")

    class Meta:
        managed = False
        db_table = 'thanh_toan'
        verbose_name = 'Thanh toán'
        verbose_name_plural = 'Quản lý Thanh toán'

    def __str__(self):
        return f"Thanh toán Đơn #{self.don_hang_id} - {self.get_phuong_thuc_display()}"


class DatBan(models.Model):
    TRANG_THAI_DAT_CHOICES = [
        ('ChoXacNhan', 'Chờ xác nhận'),
        ('DaXacNhan', 'Đã xác nhận'),
        ('HoanThanh', 'Khách đã đến (Hoàn thành)'),
        ('DaHuy', 'Đã hủy'),
    ]
    ban = models.ForeignKey('Ban', on_delete=models.SET_NULL, db_column='ban_id', blank=True, null=True, verbose_name="Bàn được xếp")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tài khoản khách")
    ten_khach_hang = models.CharField(max_length=150, verbose_name="Tên khách hàng")
    so_dien_thoai = models.CharField(max_length=20, verbose_name="Số điện thoại")
    ngay_dat = models.DateField(verbose_name="Ngày đặt")
    gio_dat = models.TimeField(verbose_name="Giờ đến")
    so_nguoi = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Số người") # Số người >= 1
    ghi_chu = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    tong_tien_coc = models.DecimalField(max_digits=18, decimal_places=0, default=0, validators=[MinValueValidator(0)], verbose_name="Tiền cọc")
    trang_thai = models.CharField(max_length=50, choices=TRANG_THAI_DAT_CHOICES, default="ChoXacNhan", verbose_name="Trạng thái")
    thoi_gian_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'dat_ban'
        verbose_name = 'Đơn Đặt Bàn'
        verbose_name_plural = 'Quản lý Đặt Bàn'

    def clean(self):
        # Ràng buộc: Không được đặt bàn trong quá khứ
        if self.ngay_dat:
            if self.ngay_dat < timezone.now().date():
                raise ValidationError({'ngay_dat': 'Không thể đặt bàn vào ngày trong quá khứ.'})

    def __str__(self):
        return f"{self.ten_khach_hang} - {self.ngay_dat} {self.gio_dat}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Tài khoản")
    so_dien_thoai = models.CharField(max_length=15, blank=True, verbose_name="Số điện thoại")
    dia_chi = models.CharField(max_length=255, blank=True, verbose_name="Địa chỉ")
    diem_tich_luy = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name="Điểm tích lũy")
    hang_thanh_vien = models.ForeignKey(HangThanhVien, models.DO_NOTHING, blank=True, null=True, verbose_name="Hạng thành viên")
    
    def save(self, *args, **kwargs):
        # Tự động xếp hạng theo điểm
        hang_xung_dang = HangThanhVien.objects.filter(
            diem_toi_thieu__lte=self.diem_tich_luy
        ).order_by('-diem_toi_thieu').first()

        if hang_xung_dang and self.hang_thanh_vien != hang_xung_dang:
            self.hang_thanh_vien = hang_xung_dang

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Hồ sơ khách hàng'
        verbose_name_plural = 'Quản lý Hồ sơ'
        
    def __str__(self):
        return self.user.username
    

class Voucher(models.Model):
    LOAI_GIAM_GIA = [
        ('TienMat', 'Giảm thẳng tiền (VNĐ)'),
        ('PhanTram', 'Giảm theo phần trăm (%)'),
    ]

    ma_code = models.CharField(max_length=50, unique=True, verbose_name="Mã giảm giá")
    loai_giam = models.CharField(max_length=20, choices=LOAI_GIAM_GIA, default='TienMat', verbose_name="Loại giảm")
    gia_tri = models.DecimalField(max_digits=18, decimal_places=0, validators=[MinValueValidator(0)], verbose_name="Giá trị giảm (VNĐ hoặc %)")
    
    so_luong_gioi_han = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Số lượng tối đa", help_text="Phải lớn hơn 0")
    so_luong_da_dung = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name="Số lượng đã dùng")
    
    ngay_het_han = models.DateTimeField(blank=True, null=True, verbose_name="Ngày hết hạn")
    kich_hoat = models.BooleanField(default=True, verbose_name="Đang hoạt động")

    class Meta:
        managed = True
        db_table = 'voucher'
        verbose_name = 'Mã giảm giá'
        verbose_name_plural = 'Quản lý Mã giảm giá'

    def clean(self):
            # 1. Gọi hàm clean mặc định của Django để chạy các bộ chặn số âm trước
            super().clean()
            
            # 2. Kiểm tra nếu người dùng nhập số lượng giới hạn hợp lệ (không trống, không âm)
            # thì mới chạy logic so sánh nâng cao bên dưới.
            if self.so_luong_gioi_han is not None and self.so_luong_gioi_han >= 1:
                
                if self.so_luong_da_dung > self.so_luong_gioi_han:
                    # Gán lỗi trực tiếp vào ô 'so_luong_gioi_han' (ô này có hiển thị trên form admin)
                    raise ValidationError({
                        'so_luong_gioi_han': 'Số lượng đã dùng hiện tại không thể lớn hơn số lượng giới hạn mới.'
                    })

    def hop_le(self):
        if not self.kich_hoat:
            return False, "Mã giảm giá đã bị khóa."
        if self.ngay_het_han and self.ngay_het_han < timezone.now():
            return False, "Mã giảm giá đã hết hạn sử dụng."
        if self.so_luong_da_dung >= self.so_luong_gioi_han:
            return False, "Mã giảm giá đã hết lượt sử dụng."
        return True, "Hợp lệ"
        
    def __str__(self):
        return f"{self.ma_code} - Giảm {self.gia_tri} ({self.get_loai_giam_display()})"
from django.db import models
from django.contrib.auth.models import User

# (Thường được sinh ra tự động để quản lý User, Phân quyền, Session, v.v.)

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


# (managed = False: Các bảng này đã được tạo cứng bằng SQL từ trước)
# Quản lý danh sách các bàn trong quán (Số bàn, số ghế, trống/đã đặt)
class Ban(models.Model):
    so_ban = models.CharField(unique=True, max_length=20)
    so_ghe = models.IntegerField()
    trang_thai = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ban'
        verbose_name = 'Bàn'
        verbose_name_plural = 'Quản lý Bàn'

    def __str__(self):
        return f"Bàn {self.so_ban}"

# Danh mục phân loại món ăn (Ví dụ: Đồ nướng, Đồ lẩu, Nước uống...)
class LoaiMon(models.Model):
    ten_loai = models.CharField(max_length=100)
    mo_ta = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'loai_mon'
        verbose_name = 'Loại món'
        verbose_name_plural = 'Quản lý Loại món'

    def __str__(self):
        return f"Loại: {self.ten_loai}"

# Quản lý chi tiết từng món ăn (Tên, giá, hình ảnh...)
class MonAn(models.Model):
    loai_mon = models.ForeignKey(LoaiMon, models.DO_NOTHING)
    ten_mon = models.CharField(max_length=200)
    mo_ta = models.TextField(blank=True, null=True)
    gia_ban = models.DecimalField(max_digits=18, decimal_places=0)
    hinh_anh = models.CharField(max_length=255, blank=True, null=True)
    trang_thai_ban = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mon_an'
        verbose_name = 'Món ăn'
        verbose_name_plural = 'Quản lý Món ăn'

    def __str__(self):
        return self.ten_mon

# Hạng thành viên
class HangThanhVien(models.Model):
    ten_hang = models.CharField(max_length=50)
    phan_tram_giam_gia = models.IntegerField(blank=True, null=True, default=0)
    diem_toi_thieu = models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        managed = True
        db_table = 'hang_thanh_vien'
        verbose_name = 'Hạng thành viên'
        verbose_name_plural = 'Quản lý Hạng thành viên'

    def __str__(self):
        return self.ten_hang



# Lưu trữ đơn hàng tổng của một bàn (Gồm tổng tiền, trạng thái...)
class DonHang(models.Model):
    ban = models.ForeignKey(Ban, models.DO_NOTHING, blank=True, null=True)
    nhan_vien = models.ForeignKey('NhanVien', models.DO_NOTHING, blank=True, null=True)
    trang_thai_don = models.CharField(max_length=50, blank=True, null=True)
    tong_tien = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    thoi_gian_tao = models.DateTimeField(blank=True, null=True)
    khach_hang = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True, blank=True)
    
    # --- 2 TRƯỜNG MỚI THÊM VÀO ĐỂ QUẢN LÝ VOUCHER ---
    voucher = models.ForeignKey('Voucher', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Voucher áp dụng")
    tien_giam_gia = models.DecimalField(max_digits=18, decimal_places=0, default=0, blank=True, null=True, verbose_name="Tiền được giảm")

    class Meta:
        managed = True
        db_table = 'don_hang'
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Quản lý Đơn hàng'

    def __str__(self):
        return f"Đơn hàng #{self.id}"
    
    @property
    def tong_thanh_toan(self):
        # Tính số tiền khách thực tế phải trả sau khi trừ voucher
        tien_goc = self.tong_tien if self.tong_tien else 0
        tien_giam = self.tien_giam_gia if self.tien_giam_gia else 0
        thanh_toan = tien_goc - tien_giam
        return thanh_toan if thanh_toan > 0 else 0


# Chi tiết bên trong 1 đơn hàng (Khách gọi món gì, số lượng bao nhiêu)
class ChiTietDonHang(models.Model):
    don_hang = models.ForeignKey('DonHang', models.DO_NOTHING)
    mon_an = models.ForeignKey('MonAn', models.DO_NOTHING)
    so_luong = models.IntegerField()
    gia_luc_ban = models.DecimalField(max_digits=18, decimal_places=0)
    ghi_chu = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chi_tiet_don_hang'
        verbose_name = 'Chi tiết đơn hàng'
        verbose_name_plural = 'Quản lý Chi tiết đơn hàng'

    def __str__(self):
        return f"Chi tiết đơn #{self.don_hang_id} - {self.mon_an.ten_mon}"
    
    @property
    def thanh_tien(self):
        # Tự động tính thành tiền bằng số lượng nhân đơn giá
        return self.so_luong * self.gia_luc_ban

# Feedback, đánh giá của khách hàng về món ăn
class DanhGia(models.Model):
    mon_an = models.ForeignKey('MonAn', models.DO_NOTHING)
    ten_khach_hang = models.CharField(max_length=100, blank=True, null=True)
    diem_danh_gia = models.IntegerField(blank=True, null=True)
    noi_dung = models.TextField(blank=True, null=True)
    thoi_gian_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'danh_gia'
        verbose_name = 'Đánh giá'
        verbose_name_plural = 'Quản lý Đánh giá'

    def __str__(self):
        return f"Đánh giá của {self.ten_khach_hang} - {self.diem_danh_gia} Sao"

# Thông tin nhân viên phục vụ/quản lý
class NhanVien(models.Model):
    ho_ten = models.CharField(max_length=150)
    vi_tri = models.CharField(max_length=50, blank=True, null=True)
    so_dien_thoai = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    ngay_vao_lam = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nhan_vien'
        verbose_name = 'Nhân viên'
        verbose_name_plural = 'Quản lý Nhân viên'

    def __str__(self):
        return f"Nhân viên {self.ho_ten}"

# Hóa đơn thanh toán cho các đơn hàng
class ThanhToan(models.Model):
    don_hang = models.OneToOneField(DonHang, models.DO_NOTHING)
    phuong_thuc = models.CharField(max_length=50, blank=True, null=True)
    trang_thai_thanh_toan = models.CharField(max_length=50, blank=True, null=True)
    thoi_gian_thanh_toan = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'thanh_toan'
        verbose_name = 'Thanh toán'
        verbose_name_plural = 'Quản lý Thanh toán'

    def __str__(self):
        return f"Thanh toán Đơn #{self.don_hang_id} - {self.phuong_thuc}"


# (managed = True: Django sẽ tự động sinh/quản lý bảng này khi migrate)
# Bảng lưu thông tin khách hàng đặt bàn trước
class DatBan(models.Model):
    ban = models.ForeignKey(
        'Ban',
        on_delete=models.SET_NULL,
        db_column='ban_id',
        blank=True,
        null=True,
        verbose_name="Bàn được xếp"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tài khoản khách đặt")
    ten_khach_hang = models.CharField(max_length=150, verbose_name="Tên khách hàng")
    so_dien_thoai = models.CharField(max_length=20, verbose_name="Số điện thoại")
    ngay_dat = models.DateField(verbose_name="Ngày đặt")
    gio_dat = models.TimeField(verbose_name="Giờ đến")
    so_nguoi = models.IntegerField(verbose_name="Số người")
    ghi_chu = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    tong_tien_coc = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True, verbose_name="Tiền cọc")
    trang_thai = models.CharField(max_length=50, default="ChoXacNhan", verbose_name="Trạng thái")
    thoi_gian_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True  # Django sẽ quản lý bảng này
        db_table = 'dat_ban'
        verbose_name = 'Đơn Đặt Bàn'
        verbose_name_plural = 'Quản lý Đặt Bàn'

    def __str__(self):
        return f"{self.ten_khach_hang} - {self.ngay_dat} {self.gio_dat}"

# Bảng mở rộng thông tin cho User (Thêm SDT, địa chỉ, điểm tích lũy...)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    so_dien_thoai = models.CharField(max_length=15, blank=True)
    dia_chi = models.CharField(max_length=255, blank=True)
    diem_tich_luy = models.IntegerField(default=0)
    hang_thanh_vien = models.ForeignKey(HangThanhVien, models.DO_NOTHING, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # TỰ ĐỘNG XÉT THĂNG HẠNG DỰA TRÊN ĐIỂM TÍCH LŨY
        # Lấy hạng có điểm tối thiểu nhỏ hơn hoặc bằng điểm hiện tại của khách, 
        # ưu tiên lấy hạng cao nhất (sắp xếp giảm dần)
        hang_xung_dang = HangThanhVien.objects.filter(
            diem_toi_thieu__lte=self.diem_tich_luy
        ).order_by('-diem_toi_thieu').first()

        # Nếu tìm thấy hạng và nó khác hạng hiện tại thì mới cập nhật
        if hang_xung_dang and self.hang_thanh_vien != hang_xung_dang:
            self.hang_thanh_vien = hang_xung_dang

        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.user.username
    
# Quản lý mã giảm giá (Voucher)
class Voucher(models.Model):
    LOAI_GIAM_GIA = [
        ('TienMat', 'Giảm thẳng tiền (VNĐ)'),
        ('PhanTram', 'Giảm theo phần trăm (%)'),
    ]

    ma_code = models.CharField(max_length=50, unique=True, verbose_name="Mã giảm giá")
    loai_giam = models.CharField(max_length=20, choices=LOAI_GIAM_GIA, default='TienMat', verbose_name="Loại giảm")
    gia_tri = models.DecimalField(max_digits=18, decimal_places=0, verbose_name="Giá trị giảm (VNĐ hoặc %)")
    
    so_luong_gioi_han = models.IntegerField(verbose_name="Số lượng tối đa", help_text="Nhập số lần mã này có thể được sử dụng")
    so_luong_da_dung = models.IntegerField(default=0, verbose_name="Số lượng đã dùng")
    
    ngay_het_han = models.DateTimeField(blank=True, null=True, verbose_name="Ngày hết hạn")
    kich_hoat = models.BooleanField(default=True, verbose_name="Đang hoạt động")

    class Meta:
        managed = True
        db_table = 'voucher'
        verbose_name = 'Mã giảm giá'
        verbose_name_plural = 'Quản lý Mã giảm giá'

    def __str__(self):
        return f"{self.ma_code} - Giảm {self.gia_tri} ({self.loai_giam})"

    # Hàm kiểm tra mã còn dùng được không
    def hop_le(self):
        from django.utils import timezone
        
        if not self.kich_hoat:
            return False, "Mã giảm giá đã bị khóa."
        if self.ngay_het_han and self.ngay_het_han < timezone.now():
            return False, "Mã giảm giá đã hết hạn sử dụng."
        if self.so_luong_da_dung >= self.so_luong_gioi_han:
            return False, "Mã giảm giá đã hết lượt sử dụng."
        return True, "Hợp lệ"
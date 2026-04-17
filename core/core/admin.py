from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Ban, ChiTietDonHang, DanhGia, DonHang, LoaiMon, MonAn, NhanVien, ThanhToan, DatBan


class NhanVienAdminForm(forms.ModelForm):
    class Meta:
        model = NhanVien
        fields = '__all__'

    # clean() tự động chạy khi bấm nút "Lưu" để kiểm tra lỗi
    def clean(self):
        cleaned_data = super().clean()
        sdt = cleaned_data.get('so_dien_thoai')
        
        # Bắt lỗi nhập số điện thoại sai định dạng
        if sdt:
            if not sdt.isdigit():
                self.add_error('so_dien_thoai', "Số điện thoại chỉ được chứa các chữ số!")
            elif len(sdt) < 10 or len(sdt) > 11:
                self.add_error('so_dien_thoai', "Số điện thoại phải có 10 số!")
            elif not sdt.startswith('0'):
                self.add_error('so_dien_thoai', "Số điện thoại phải bắt đầu bằng số 0!")
        return cleaned_data


class BanAdminForm(forms.ModelForm):
    class Meta:
        model = Ban
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        # Đảm bảo số ghế/sức chứa không được nhập số âm hoặc bằng 0
        for field in ['so_ghe', 'suc_chua']:
            if field in cleaned_data:
                val = cleaned_data.get(field)
                if val is not None and val <= 0:
                    self.add_error(field, "Số lượng ghế/sức chứa phải lớn hơn 0!")
        return cleaned_data


class MonAnAdminForm(forms.ModelForm):
    class Meta:
        model = MonAn
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        # Chống nhập giá bán bị âm
        for field in ['gia', 'gia_ban']:
            if field in cleaned_data:
                val = cleaned_data.get(field)
                if val is not None and val < 0:
                    self.add_error(field, "Giá không được là số âm!")
        return cleaned_data


class ChiTietDonHangAdminForm(forms.ModelForm):
    class Meta:
        model = ChiTietDonHang
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        # Mua hàng thì số lượng phải từ 1 trở lên
        if 'so_luong' in cleaned_data:
            val = cleaned_data.get('so_luong')
            if val is not None and val <= 0:
                self.add_error('so_luong', "Số lượng phải lớn hơn 0!")
        return cleaned_data


class DonHangAdminForm(forms.ModelForm):
    class Meta:
        model = DonHang
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        # Chống nhập tổng tiền bị âm
        for field in ['tong_tien', 'tong_cong']:
            if field in cleaned_data:
                val = cleaned_data.get(field)
                if val is not None and val < 0:
                    self.add_error(field, "Tổng tiền không được là số âm!")
        return cleaned_data


class ThanhToanAdminForm(forms.ModelForm):
    class Meta:
        model = ThanhToan
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        for field in ['so_tien', 'tong_tien']:
            if field in cleaned_data:
                val = cleaned_data.get(field)
                if val is not None and val < 0:
                    self.add_error(field, "Số tiền không được là số âm!")
        return cleaned_data


class DanhGiaAdminForm(forms.ModelForm):
    class Meta:
        model = DanhGia
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        # Đánh giá sao thì chỉ được nằm trong khoảng từ 1 đến 5 sao
        for field in ['diem', 'so_sao', 'rating']:
            if field in cleaned_data:
                val = cleaned_data.get(field)
                if val is not None and (val < 1 or val > 5):
                    self.add_error(field, "Điểm đánh giá phải từ 1 đến 5!")
        return cleaned_data


class DatBanAdminForm(forms.ModelForm):
    class Meta:
        model = DatBan
        fields = '__all__'

    # Dùng clean_<tên_field> để bắt lỗi cho từng trường cụ thể
    def clean_so_dien_thoai(self):
        sdt = self.cleaned_data.get('so_dien_thoai')
        if sdt:
            if not sdt.isdigit():
                raise ValidationError("Số điện thoại chỉ được chứa các chữ số!")
            if len(sdt) < 10 or len(sdt) > 11:
                raise ValidationError("Số điện thoại phải có 10 số!")
            if not sdt.startswith('0'):
                raise ValidationError("Số điện thoại phải bắt đầu bằng số 0!")
        return sdt

    def clean_so_nguoi(self):
        so_nguoi = self.cleaned_data.get('so_nguoi')
        if so_nguoi is not None and so_nguoi <= 0:
            raise ValidationError("Số người phải lớn hơn 0!")
        return so_nguoi

    def clean_tong_tien_coc(self):
        tien = self.cleaned_data.get('tong_tien_coc')
        if tien is not None and tien < 0:
            raise ValidationError("Tiền cọc không được là số âm!")
        return tien


# ĐĂNG KÝ VÀ TÙY BIẾN GIAO DIỆN ADMIN

# Áp dụng các Form kiểm tra dữ liệu ở trên vào từng Model tương ứng
@admin.register(NhanVien)
class NhanVienAdmin(admin.ModelAdmin):
    form = NhanVienAdminForm

@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    form = BanAdminForm

@admin.register(MonAn)
class MonAnAdmin(admin.ModelAdmin):
    form = MonAnAdminForm

@admin.register(ChiTietDonHang)
class ChiTietDonHangAdmin(admin.ModelAdmin):
    form = ChiTietDonHangAdminForm

@admin.register(DonHang)
class DonHangAdmin(admin.ModelAdmin):
    form = DonHangAdminForm

@admin.register(ThanhToan)
class ThanhToanAdmin(admin.ModelAdmin):
    form = ThanhToanAdminForm

@admin.register(DanhGia)
class DanhGiaAdmin(admin.ModelAdmin):
    form = DanhGiaAdminForm

# Riêng bảng Đặt Bàn có tùy biến giao diện hiển thị chi tiết hơn
@admin.register(DatBan)
class DatBanAdmin(admin.ModelAdmin):
    form = DatBanAdminForm
    
    # Các cột sẽ hiển thị ra ở màn hình danh sách Đặt bàn
    list_display = ('ten_khach_hang', 'so_dien_thoai', 'ngay_dat', 'gio_dat', 'so_nguoi', 'tong_tien_coc', 'ban', 'trang_thai')
    
    # Cho phép chỉnh sửa nhanh cột 'ban' và 'trang_thai' ngay ngoài danh sách mà không cần bấm vào chi tiết
    list_editable = ('ban', 'trang_thai')
    
    # Tạo bộ lọc (Filter) bên tay phải theo Trạng thái và Ngày đặt
    list_filter = ('trang_thai', 'ngay_dat')
    
    # Thêm thanh tìm kiếm theo Tên khách và SĐT
    search_fields = ('ten_khach_hang', 'so_dien_thoai')
    
    # Sắp xếp mặc định: Đơn tạo mới nhất sẽ lên đầu
    ordering = ('-thoi_gian_tao',)

# Loại món không cần form kiểm tra phức tạp nên chỉ cần đăng ký đơn giản như vầy
admin.site.register(LoaiMon)
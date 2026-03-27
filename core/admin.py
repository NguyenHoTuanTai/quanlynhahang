from django.contrib import admin
from .models import Ban, ChiTietDonHang, DanhGia, DonHang, LoaiMon, MonAn, NhanVien, ThanhToan, DatBan

admin.site.register(Ban)
admin.site.register(ChiTietDonHang)
admin.site.register(DanhGia)
admin.site.register(DonHang)
admin.site.register(LoaiMon)
admin.site.register(MonAn)
admin.site.register(NhanVien)
admin.site.register(ThanhToan)

@admin.register(DatBan)
class DatBanAdmin(admin.ModelAdmin):
    list_display = ('ten_khach_hang', 'so_dien_thoai', 'ngay_dat', 'gio_dat', 'so_nguoi', 'tong_tien_coc', 'ban', 'trang_thai')
    list_editable = ('ban', 'trang_thai')
    list_filter = ('trang_thai', 'ngay_dat')
    search_fields = ('ten_khach_hang', 'so_dien_thoai')
    ordering = ('-thoi_gian_tao',)
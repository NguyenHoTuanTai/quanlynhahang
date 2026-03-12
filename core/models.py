from django.db import models


class Ban(models.Model):
    so_ban = models.CharField(unique=True, max_length=20)
    so_ghe = models.IntegerField()
    trang_thai = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'ban'


class NhanVien(models.Model):
    ho_ten = models.CharField(max_length=150)
    vi_tri = models.CharField(max_length=50, blank=True, null=True)
    so_dien_thoai = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    ngay_vao_lam = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'nhan_vien'


class LoaiMon(models.Model):
    ten_loai = models.CharField(max_length=100)
    mo_ta = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'loai_mon'


class MonAn(models.Model):
    loai_mon = models.ForeignKey(LoaiMon, on_delete=models.CASCADE)
    ten_mon = models.CharField(max_length=200)
    mo_ta = models.TextField(blank=True, null=True)
    gia_ban = models.DecimalField(max_digits=18, decimal_places=0)
    hinh_anh = models.CharField(max_length=255, blank=True, null=True)
    trang_thai_ban = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = 'mon_an'


class DonHang(models.Model):
    ban = models.ForeignKey(Ban, on_delete=models.SET_NULL, blank=True, null=True)
    nhan_vien = models.ForeignKey(NhanVien, on_delete=models.SET_NULL, blank=True, null=True)
    trang_thai_don = models.CharField(max_length=50, blank=True, null=True)
    tong_tien = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    thoi_gian_tao = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'don_hang'


class ChiTietDonHang(models.Model):
    don_hang = models.ForeignKey(DonHang, on_delete=models.CASCADE)
    mon_an = models.ForeignKey(MonAn, on_delete=models.CASCADE)
    so_luong = models.IntegerField()
    gia_luc_ban = models.DecimalField(max_digits=18, decimal_places=0)
    ghi_chu = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'chi_tiet_don_hang'


class DanhGia(models.Model):
    mon_an = models.ForeignKey(MonAn, on_delete=models.CASCADE)
    ten_khach_hang = models.CharField(max_length=100, blank=True, null=True)
    diem_danh_gia = models.IntegerField(blank=True, null=True)
    noi_dung = models.TextField(blank=True, null=True)
    thoi_gian_tao = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'danh_gia'


class ThanhToan(models.Model):
    don_hang = models.OneToOneField(DonHang, on_delete=models.CASCADE)
    phuong_thuc = models.CharField(max_length=50, blank=True, null=True)
    trang_thai_thanh_toan = models.CharField(max_length=50, blank=True, null=True)
    thoi_gian_thanh_toan = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'thanh_toan'
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150, db_collation='Vietnamese_CI_AS')

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
    name = models.CharField(max_length=255, db_collation='Vietnamese_CI_AS')
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100, db_collation='Vietnamese_CI_AS')

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128, db_collation='Vietnamese_CI_AS')
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150, db_collation='Vietnamese_CI_AS')
    first_name = models.CharField(max_length=150, db_collation='Vietnamese_CI_AS')
    last_name = models.CharField(max_length=150, db_collation='Vietnamese_CI_AS')
    email = models.CharField(max_length=254, db_collation='Vietnamese_CI_AS')
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


class Ban(models.Model):
    so_ban = models.CharField(unique=True, max_length=20, db_collation='Vietnamese_CI_AS')
    so_ghe = models.IntegerField()
    trang_thai = models.CharField(max_length=50, db_collation='Vietnamese_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ban'


class ChiTietDonHang(models.Model):
    don_hang = models.ForeignKey('DonHang', models.DO_NOTHING)
    mon_an = models.ForeignKey('MonAn', models.DO_NOTHING)
    so_luong = models.IntegerField()
    gia_luc_ban = models.DecimalField(max_digits=18, decimal_places=0)
    ghi_chu = models.CharField(max_length=255, db_collation='Vietnamese_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chi_tiet_don_hang'


class DanhGia(models.Model):
    mon_an = models.ForeignKey('MonAn', models.DO_NOTHING)
    ten_khach_hang = models.CharField(max_length=100, db_collation='Vietnamese_CI_AS', blank=True, null=True)
    diem_danh_gia = models.IntegerField(blank=True, null=True)
    noi_dung = models.TextField(db_collation='Vietnamese_CI_AS', blank=True, null=True)
    thoi_gian_tao = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'danh_gia'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(db_collation='Vietnamese_CI_AS', blank=True, null=True)
    object_repr = models.CharField(max_length=200, db_collation='Vietnamese_CI_AS')
    action_flag = models.SmallIntegerField()
    change_message = models.TextField(db_collation='Vietnamese_CI_AS')
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100, db_collation='Vietnamese_CI_AS')
    model = models.CharField(max_length=100, db_collation='Vietnamese_CI_AS')

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255, db_collation='Vietnamese_CI_AS')
    name = models.CharField(max_length=255, db_collation='Vietnamese_CI_AS')
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40, db_collation='Vietnamese_CI_AS')
    session_data = models.TextField(db_collation='Vietnamese_CI_AS')
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DonHang(models.Model):
    ban = models.ForeignKey(Ban, models.DO_NOTHING, blank=True, null=True)
    nhan_vien = models.ForeignKey('NhanVien', models.DO_NOTHING, blank=True, null=True)
    trang_thai_don = models.CharField(max_length=50, db_collation='Vietnamese_CI_AS', blank=True, null=True)
    tong_tien = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    thoi_gian_tao = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'don_hang'


class LoaiMon(models.Model):
    ten_loai = models.CharField(max_length=100, db_collation='Vietnamese_CI_AS')
    mo_ta = models.TextField(db_collation='Vietnamese_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'loai_mon'


class MonAn(models.Model):
    loai_mon = models.ForeignKey(LoaiMon, models.DO_NOTHING)
    ten_mon = models.CharField(max_length=200, db_collation='Vietnamese_CI_AS')
    mo_ta = models.TextField(db_collation='Vietnamese_CI_AS', blank=True, null=True)
    gia_ban = models.DecimalField(max_digits=18, decimal_places=0)
    hinh_anh = models.CharField(max_length=255, db_collation='Vietnamese_CI_AS', blank=True, null=True)
    trang_thai_ban = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mon_an'


class NhanVien(models.Model):
    ho_ten = models.CharField(max_length=150, db_collation='Vietnamese_CI_AS')
    vi_tri = models.CharField(max_length=50, db_collation='Vietnamese_CI_AS', blank=True, null=True)
    so_dien_thoai = models.CharField(max_length=20, db_collation='Vietnamese_CI_AS', blank=True, null=True)
    email = models.CharField(max_length=100, db_collation='Vietnamese_CI_AS', blank=True, null=True)
    ngay_vao_lam = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nhan_vien'


class ThanhToan(models.Model):
    don_hang = models.OneToOneField(DonHang, models.DO_NOTHING)
    phuong_thuc = models.CharField(max_length=50, db_collation='Vietnamese_CI_AS', blank=True, null=True)
    trang_thai_thanh_toan = models.CharField(max_length=50, db_collation='Vietnamese_CI_AS', blank=True, null=True)
    thoi_gian_thanh_toan = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'thanh_toan'

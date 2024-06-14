from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone

import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, email=None, **extra_fields):
        if not username:
            raise ValueError("The username field must be set")
        username = self.normalize_email(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)


class Company(models.Model):
    """  """
    id = models.IntegerField(primary_key=True, editable=False, unique=True, verbose_name='Уникальный идентификатор')
    name = models.CharField(_(" "), max_length=250, null=True, blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, verbose_name="",
                               related_name="", default=None)
    created_at = models.DateField(auto_now_add=True, verbose_name="")
    updated_at = models.DateField(auto_now_add=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "company_table"
        verbose_name = ""
        verbose_name_plural = ""


class Wildberries(models.Model):
    """  """
    id = models.IntegerField(primary_key=True, editable=False, unique=True, verbose_name='Уникальный идентификатор')
    wb_api_key = models.CharField(_(""), max_length=1000, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True,
                                related_name="WildberriesCompany", verbose_name="")
    created_at = models.DateField(auto_now_add=True, verbose_name="")
    updated_at = models.DateField(auto_now_add=False)

    def __str__(self):
        return f"Wildberries : {self.company.name}"

    class Meta:
        db_table = "wildberries_table"
        verbose_name = ""
        verbose_name_plural = ""


class Ozon(models.Model):
    """  """
    id = models.IntegerField(primary_key=True, editable=False, unique=True, verbose_name='Уникальный идентификатор')
    api_token = models.CharField(_(""), max_length=1000, null=True, blank=True)
    client_id = models.CharField(_(""), max_length=1000, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True,
                                related_name="OzonCompany", verbose_name="")
    created_at = models.DateField(auto_now_add=True, verbose_name="")
    updated_at = models.DateField(auto_now_add=False)

    def __str__(self):
        return f"Ozon : {self.company.name}"

    class Meta:
        db_table = "ozon_table"
        verbose_name = ""
        verbose_name_plural = ""


class YandexMarket(models.Model):
    """  """
    id = models.IntegerField(primary_key=True, editable=False, unique=True, verbose_name='Уникальный идентификатор')
    api_key_bearer = models.CharField(_(""), max_length=1000, null=True, blank=True)
    fby_campaign_id = models.CharField(_(""), max_length=1000, null=True, blank=True)
    fbs_campaign_id = models.CharField(_(""), max_length=1000, null=True, blank=True)
    business_id = models.CharField(_(""), max_length=1000, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True,
                                related_name="YandexMarketCompany", verbose_name="")
    created_at = models.DateField(auto_now_add=True, verbose_name="")
    updated_at = models.DateField(auto_now_add=False)

    def __str__(self):
        return f"YandexMarket : {self.company.name}"

    class Meta:
        db_table = "yandexMarket_table"
        verbose_name = ""
        verbose_name_plural = ""


class CustomUser(AbstractUser):
    """ """
    class Text:
        WRONG_PASSWORD_OR_LOGIN_ENTERED = "Wrong login or password"
        USER_WITH_SUCH_EMAIL_ALREADY_EXISTS = "A user with this email already exists"
        USER_WITH_SUCH_EMAIL_DOES_NOT_EXIST = "A user with this email already exists"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(_(''), max_length=18)
    email = models.EmailField(_(''), max_length=255, unique=True)
    username = models.CharField(_(''), max_length=255, null=False, blank=False, unique=True)
    avatar = models.ImageField(_(''), upload_to="path/")
    company = models.ManyToManyField(Company, null=True, blank=True, related_name="UserCompany", verbose_name="")
    is_active = models.BooleanField(_(''), default=True)
    is_staff = models.BooleanField(_(''), default=False)
    date_joined = models.DateTimeField(_(''), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.phone

    class Meta:
        db_table = "user_table"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Product(models.Model):
    """  """
    id = models.IntegerField(primary_key=True, editable=False, unique=True, verbose_name='Уникальный идентификатор')
    vendor_code = models.CharField(_(""), max_length=1000, null=True, blank=True)
    place_in_warehouse = models.CharField(_(""), max_length=500, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True,
                                related_name="ProductCompany", verbose_name="")



    def __str__(self):
        return self.vendor_code

    class Meta:
        db_table = "product_table"
        verbose_name = ""
        verbose_name_plural = ""


class WildberriesProductSales(models.Model):
    """  """
    id = models.IntegerField(primary_key=True, editable=False, unique=True, verbose_name='Уникальный идентификатор')
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name="")
    remain_quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name="")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name="WildberriesProduct", verbose_name="")
    wildberries = models.ForeignKey(Wildberries, on_delete=models.CASCADE, null=True, blank=True,
                                related_name="WildberriesProduct", verbose_name="")
    created_at = models.DateField(auto_now_add=True, verbose_name="")
    updated_at = models.DateField(auto_now_add=False)

    def __str__(self):
        return self.product.vendor_code

    class Meta:
        db_table = "wildberries_product_table"
        verbose_name = ""
        verbose_name_plural = ""


class OzonProductSales(models.Model):
    """  """
    id = models.IntegerField(primary_key=True, editable=False, unique=True, verbose_name='Уникальный идентификатор')
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name="")
    remain_quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name="")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True,
                                related_name="OzonProduct", verbose_name="")
    ozon = models.ForeignKey(Wildberries, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name="OzonProduct", verbose_name="")
    created_at = models.DateField(auto_now_add=True, verbose_name="")
    updated_at = models.DateField(auto_now_add=False)

    def __str__(self):
        return self.product.vendor_code

    class Meta:
        db_table = "ozon_product_table"
        verbose_name = ""
        verbose_name_plural = ""


class YandexMarketProductSales(models.Model):
    """  """
    id = models.IntegerField(primary_key=True, editable=False, unique=True, verbose_name='Уникальный идентификатор')
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name="")
    remain_quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name="")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True,
                                related_name="YandexMarketProduct", verbose_name="")
    yandex_market = models.ForeignKey(Wildberries, on_delete=models.CASCADE, null=True, blank=True,
                             related_name="YandexMarketProduct", verbose_name="")
    created_at = models.DateField(auto_now_add=True, verbose_name="")
    updated_at = models.DateField(auto_now_add=False)

    def __str__(self):
        return self.product.vendor_code

    class Meta:
        db_table = "yandex_market_product_table"
        verbose_name = ""
        verbose_name_plural = ""


class InProduction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, verbose_name="",
                                related_name="")
    need_to_produce_quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name="")
    created_at = models.DateField(auto_now_add=True, verbose_name="")
    updated_at = models.DateField(auto_now_add=False)

    def __str__(self):
        return self.product.vendor_code

    class Meta:
        db_table = "in_production_product_table"
        verbose_name = ""
        verbose_name_plural = ""


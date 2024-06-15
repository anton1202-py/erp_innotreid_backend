from django.db import models
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    """
    Модель компании для хранения информации о компаниях.
    """
    id = models.IntegerField(primary_key=True, editable=False, unique=True, verbose_name='Уникальный идентификатор')
    name = models.CharField(_("Имя компании"), max_length=250, null=True, blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name="Родительская компания", related_name="children", default=None)
    created_at = models.DateField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateField(auto_now=False, verbose_name="Дата обновления")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "company_table"
        verbose_name = "Компания"
        verbose_name_plural = "Компании"

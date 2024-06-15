from django.contrib import admin
from apps.companies.models import Company


class CompanyAdmin(admin.ModelAdmin):
    """
    Админская панель для управления компаниями.
    """

    # Поля, которые будут отображаться в списке компаний в админке
    list_display = ('id', 'name', 'parent', 'created_at', 'updated_at')

    # Поля, по которым можно фильтровать список компаний
    list_filter = ('created_at', 'updated_at')

    # Поля, которые будут использоваться для поиска компаний
    search_fields = ('name', 'parent__name')

    # Параметры для редактирования компании
    fieldsets = (
        (None, {'fields': ('name', 'parent')}),
        ('Дата', {'fields': ('created_at', 'updated_at')}),
    )

    # Поля, которые должны быть уникальны для каждой компании
    ordering = ('id', 'name')


# Регистрация модели компании и админской панели
admin.site.register(Company, CompanyAdmin)

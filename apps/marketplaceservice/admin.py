from django.contrib import admin
from apps.marketplaceservice.models import Wildberries, Ozon, YandexMarket


class WildberriesAdmin(admin.ModelAdmin):
    """
    Административная панель для управления моделью Wildberries.
    """
    list_display = ('id', 'wb_api_key', 'company', 'created_at', 'updated_at')
    list_filter = ('company', 'created_at', 'updated_at')
    search_fields = ('wb_api_key', 'company__name')
    fieldsets = (
        (None, {
            'fields': ('wb_api_key', 'company')
        }),
        ('Дата', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    ordering = ('id',)


class OzonAdmin(admin.ModelAdmin):
    """
    Административная панель для управления моделью Ozon.
    """
    list_display = ('id', 'api_token', 'client_id', 'company', 'created_at', 'updated_at')
    list_filter = ('company', 'created_at', 'updated_at')
    search_fields = ('api_token', 'client_id', 'company__name')
    fieldsets = (
        (None, {
            'fields': ('api_token', 'client_id', 'company')
        }),
        ('Дата', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    ordering = ('id',)


class YandexMarketAdmin(admin.ModelAdmin):
    """
    Административная панель для управления моделью YandexMarket.
    """
    list_display = ('id', 'api_key_bearer', 'fby_campaign_id', 'fbs_campaign_id', 'business_id', 'company',
                    'created_at', 'updated_at')
    list_filter = ('company', 'created_at', 'updated_at')
    search_fields = ('api_key_bearer', 'fby_campaign_id', 'fbs_campaign_id', 'business_id', 'company__name')
    fieldsets = (
        (None, {
            'fields': ('api_key_bearer', 'fby_campaign_id', 'fbs_campaign_id', 'business_id', 'company')
        }),
        ('Дата', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    ordering = ('id',)


# Регистрация моделей и их административных панелей
admin.site.register(Wildberries, WildberriesAdmin)
admin.site.register(Ozon, OzonAdmin)
admin.site.register(YandexMarket, YandexMarketAdmin)

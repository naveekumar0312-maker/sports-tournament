from django.contrib import admin
from .models import District, Taluk, Village, LocalArea

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'lgd_code', 'state_name', 'is_active', 'created_at')
    list_filter = ('state_name', 'is_active')
    search_fields = ('name', 'lgd_code', 'state_name')
    ordering = ('name',)

@admin.register(Taluk)
class TalukAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'lgd_code', 'is_active', 'created_at')
    list_filter = ('district', 'is_active')
    search_fields = ('name', 'lgd_code', 'district__name')
    ordering = ('district__name', 'name')

@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ('get_district', 'taluk', 'name', 'lgd_code', 'pin_code', 'is_active')
    list_filter = ('taluk__district', 'taluk', 'is_active')
    search_fields = ('name', 'lgd_code', 'pin_code', 'taluk__name', 'taluk__district__name')
    ordering = ('taluk__district__name', 'taluk__name', 'name')

    def get_district(self, obj):
        return obj.taluk.district.name if obj.taluk and obj.taluk.district else "-"
    get_district.short_description = 'District'
    get_district.admin_order_field = 'taluk__district__name'

@admin.register(LocalArea)
class LocalAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'taluk', 'pincode')
    list_filter = ('taluk__district', 'taluk')
    search_fields = ('name', 'taluk__name', 'pincode')



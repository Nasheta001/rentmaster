from django.contrib import admin
from .models import Property, Unit, Tenant, Payment, Announcement, MaintenanceRequest, LeaseEvent, Agreement


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'landlord', 'total_units', 'vacant_units', 'created_at']
    list_filter = ['city', 'landlord']
    search_fields = ['name', 'address', 'city']


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['unit_number', 'prop', 'unit_type', 'rent_amount', 'status']
    list_filter = ['status', 'prop__landlord']
    search_fields = ['unit_number', 'prop__name']


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'unit', 'rent_amount', 'move_in_date', 'is_active']
    list_filter = ['is_active', 'landlord']
    search_fields = ['first_name', 'last_name', 'phone', 'email']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'tenant', 'amount_paid', 'amount_expected', 'period_month', 'period_year', 'status']
    list_filter = ['status', 'period_year', 'period_month', 'payment_method']
    search_fields = ['tenant__first_name', 'tenant__last_name', 'receipt_number']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'landlord', 'audience', 'priority', 'created_at']
    list_filter = ['audience', 'priority']


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit', 'tenant', 'priority', 'status', 'reported_date']
    list_filter = ['status', 'priority']


@admin.register(LeaseEvent)
class LeaseEventAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'event_type', 'event_date']
    list_filter = ['event_type']


@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ['title', 'agreement_type', 'landlord', 'is_public', 'created_at']
    list_filter = ['agreement_type', 'is_public']

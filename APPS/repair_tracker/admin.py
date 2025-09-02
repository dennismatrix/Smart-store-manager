# repair_tracker/admin.py
from django.contrib import admin
from django.contrib import messages
from .models import Repair, Revenue

@admin.register(Repair)
class RepairAdmin(admin.ModelAdmin):
    list_display = ['owner_name', 'phone_name', 'status', 'charges', 'created_at']
    list_filter = ['status']
    search_fields = ['owner_name', 'owner_phone', 'phone_name']
    actions = ['reset_repairs', 'mark_as_collected', 'delete_selected']

    def reset_repairs(self, request, queryset):
        queryset.update(status='IN_PROGRESS', collected_at=None)
        # Delete associated revenue records
        for repair in queryset:
            Revenue.objects.filter(repair=repair).delete()
        self.message_user(request, f"{queryset.count()} repairs have been reset to 'In Progress'.")
    reset_repairs.short_description = "Reset selected repairs to 'In Progress'"

    def mark_as_collected(self, request, queryset):
        from django.utils import timezone
        now = timezone.now()
        
        for repair in queryset:
            repair.status = 'COLLECTED'
            repair.collected_at = now
            repair.save()
            
            # Create revenue record if it doesn't exist
            Revenue.objects.get_or_create(
                repair=repair,
                defaults={
                    'amount': repair.charges,
                    'collected_at': now
                }
            )
        
        self.message_user(request, f"{queryset.count()} repairs marked as collected.")
    mark_as_collected.short_description = "Mark selected repairs as collected"

    def delete_selected(self, request, queryset):
        # Delete associated revenue records first
        for repair in queryset:
            Revenue.objects.filter(repair=repair).delete()
        
        # Then delete the repairs
        deletion_count = queryset.count()
        queryset.delete()
        
        self.message_user(request, f"{deletion_count} repairs have been permanently deleted.")
    delete_selected.short_description = "Delete selected repairs permanently"

@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = ['repair', 'amount', 'collected_at']
    list_filter = ['collected_at']
    search_fields = ['repair__owner_name']
    actions = ['delete_selected']

    def delete_selected(self, request, queryset):
        deletion_count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{deletion_count} revenue records have been permanently deleted.")
    delete_selected.short_description = "Delete selected revenue records permanently"
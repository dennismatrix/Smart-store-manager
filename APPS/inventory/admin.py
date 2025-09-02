from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import now
from .models import Category, Item, Sale, StockAlert

@admin.register(Category)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "buying_price", "selling_price", "quantity", "low_stock_warning")
    list_filter = ("category",)
    search_fields = ("name", "category__name")

    def low_stock_warning(self, obj):
        """Show low stock warning in red"""
        return format_html(
            '<span style="color: red;">Low Stock!</span>' if obj.is_low_stock() else "OK"
        )
    
    actions = ["reset_inventory"]

    def reset_inventory(self, request, queryset):
        """Custom action to reset selected inventory items"""
        queryset.update(quantity=0)
        self.message_user(request, "Selected inventory has been reset.")

    reset_inventory.short_description = "Reset selected inventory (set quantity to 0)"

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("item", "quantity_sold", "selling_price", "profit", "sold_at")
    list_filter = ("sold_at",)
    search_fields = ("item__name",)

    def profit(self, obj):
        """Calculate profit per sale"""
        return (obj.selling_price - obj.item.buying_price) * obj.quantity_sold

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ("item", "is_alert_active")
    actions = ["reset_alerts"]

    def reset_alerts(self, request, queryset):
        """Reset stock alerts"""
        queryset.update(is_alert_active=False)
        self.message_user(request, "Stock alerts reset.")

    reset_alerts.short_description = "Reset selected stock alerts"

# Global reset action
def reset_all_inventory(modeladmin, request, queryset):
    """Reset all inventory data including items, sales, and alerts"""
    Item.objects.all().update(quantity=0)
    Sale.objects.all().delete()
    StockAlert.objects.all().update(is_alert_active=False)
    modeladmin.message_user(request, "All inventory data has been reset.")

reset_all_inventory.short_description = "RESET ALL INVENTORY DATA (Caution!)"

admin.site.add_action(reset_all_inventory)

from django.db import models
from django.utils.timezone import now

class Category(models.Model):
    """Stores product categories"""
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    """Stores inventory items"""
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    low_stock_threshold = models.PositiveIntegerField(default=5)  # Alerts when below this

    def sell_item(self, quantity_sold, selling_price=None):
        """Handles item sale, reduces stock, and records sale"""
        if self.quantity >= quantity_sold:
            self.quantity -= quantity_sold
            Sale.objects.create(
                item=self,
                quantity_sold=quantity_sold,
                selling_price=selling_price or self.selling_price
            )
            self.save()
            return True
        return False

    def is_low_stock(self):
        """Check if stock is below threshold"""
        return self.quantity <= self.low_stock_threshold

    def __str__(self):
        return f"{self.name} - {self.quantity} left"

class Sale(models.Model):
    """Stores sales transactions"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    sold_at = models.DateTimeField(default=now)

    def profit(self):
        """Calculate profit per sale"""
        return (self.selling_price - self.item.buying_price) * self.quantity_sold

    def __str__(self):
        return f"Sold {self.quantity_sold} of {self.item.name} on {self.sold_at.strftime('%Y-%m-%d')}"

class StockAlert(models.Model):
    """Stores alerts for low-stock items"""
    item = models.OneToOneField(Item, on_delete=models.CASCADE)
    is_alert_active = models.BooleanField(default=False)

    def check_stock(self):
        """Updates alert status based on stock level"""
        self.is_alert_active = self.item.is_low_stock()
        self.save()
    
    def __str__(self):
        return f"Low Stock Alert: {self.item.name} ({self.item.quantity} left)"

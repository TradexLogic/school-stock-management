from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Campus(models.Model):
    """প্রতিটি Branch/Campus"""
    name = models.CharField(max_length=200, verbose_name="Campus Name")
    address = models.TextField(blank=True, null=True, verbose_name="Address")
    admin = models.OneToOneField(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='campus', verbose_name="Campus Admin"
    )
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Campus"
        verbose_name_plural = "Campuses"
        ordering = ['name']

    def __str__(self):
        return self.name

    def total_stock_value(self):
        total = 0
        for ci in self.campus_inventories.all():
            total += ci.quantity * ci.product.selling_price
        return total

    def total_products(self):
        return self.campus_inventories.filter(quantity__gt=0).count()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def product_count(self):
        return self.products.count()


class Vendor(models.Model):
    name = models.CharField(max_length=200, verbose_name="Vendor Name")
    mobile = models.CharField(max_length=20, verbose_name="Mobile Number")
    address = models.TextField(blank=True, null=True, verbose_name="Address")
    bank_account = models.CharField(
        max_length=200, blank=True, null=True,
        verbose_name="Bank Account Details"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vendor"
        verbose_name_plural = "Vendors"
        ordering = ['name']

    def __str__(self):
        return self.name

    def total_purchase_amount(self):
        total = 0
        for log in self.stock_logs.filter(transaction_type='IN'):
            total += log.quantity * log.product.purchase_price
        return total


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Product Name")
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT,
        related_name='products', verbose_name="Category"
    )
    purchase_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Purchase Price (৳)"
    )
    selling_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Selling Price (৳)"
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name="Current Stock")
    opening_stock = models.PositiveIntegerField(default=0, verbose_name="Opening Stock")
    low_stock_threshold = models.PositiveIntegerField(
        default=10, verbose_name="Low Stock Alert Threshold"
    )
    vendor = models.ForeignKey(
        'Vendor', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='products', verbose_name="Vendor"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category})"

    @property
    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold

    @property
    def stock_value(self):
        return self.quantity * self.purchase_price

    @property
    def sales_value(self):
        return self.quantity * self.selling_price

    @property
    def profit_margin(self):
        return self.selling_price - self.purchase_price


class CampusInventory(models.Model):
    """প্রতিটি Campus এ কোন product কতটুকু আছে"""
    campus = models.ForeignKey(
        Campus, on_delete=models.CASCADE,
        related_name='campus_inventories',
        verbose_name="Campus"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='campus_inventories',
        verbose_name="Product"
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name="Quantity")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Updated By"
    )

    class Meta:
        verbose_name = "Campus Inventory"
        verbose_name_plural = "Campus Inventories"
        unique_together = ['campus', 'product']
        ordering = ['product__name']

    def __str__(self):
        return f"{self.campus.name} — {self.product.name} ({self.quantity})"

    @property
    def total_value(self):
        return self.quantity * self.product.selling_price


class ActivityLog(models.Model):
    """User activity log"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name="User"
    )
    action = models.CharField(max_length=500, verbose_name="Action")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.action}"


class StockLog(models.Model):
    STOCK_IN = 'IN'
    STOCK_OUT = 'OUT'
    TYPE_CHOICES = [
        (STOCK_IN, 'Stock IN (Purchase/Receive)'),
        (STOCK_OUT, 'Stock OUT (Sale/Issue)'),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='stock_logs', verbose_name="Product"
    )
    transaction_type = models.CharField(
        max_length=3, choices=TYPE_CHOICES,
        verbose_name="Transaction Type"
    )
    quantity = models.PositiveIntegerField(verbose_name="Quantity")
    vendor = models.ForeignKey(
        Vendor, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='stock_logs', verbose_name="Vendor"
    )
    note = models.TextField(blank=True, null=True, verbose_name="Note/Reason")
    voucher_number = models.CharField(
        max_length=50, unique=True, blank=True,
        verbose_name="Voucher Number"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Created By"
    )
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="Date & Time"
    )

    class Meta:
        verbose_name = "Stock Log"
        verbose_name_plural = "Stock Logs"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.voucher_number} — {self.product.name} ({self.transaction_type})"

    def save(self, *args, **kwargs):
        if not self.voucher_number:
            import time
            prefix = 'SIN' if self.transaction_type == 'IN' else 'SOUT'
            timestamp = str(int(time.time() * 1000))[-6:]
            last = StockLog.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.voucher_number = f"{prefix}-{str(next_id).zfill(4)}-{timestamp}"

        is_new = self.pk is None
        if is_new:
            super().save(*args, **kwargs)
            product = self.product
            if self.transaction_type == self.STOCK_IN:
                product.quantity += self.quantity
            elif self.transaction_type == self.STOCK_OUT:
                if self.quantity > product.quantity:
                    raise ValueError(
                        f"Insufficient stock! Available: {product.quantity}"
                    )
                product.quantity -= self.quantity
            product.save(update_fields=['quantity', 'updated_at'])
        else:
            super().save(*args, **kwargs)


# ✅ FIXED: CampusStockLog এখন StockLog এর বাইরে — আলাদা top-level class
class CampusStockLog(models.Model):
    STOCK_IN = 'IN'
    STOCK_OUT = 'OUT'
    TYPE_CHOICES = [
        (STOCK_IN, 'Stock IN'),
        (STOCK_OUT, 'Stock OUT'),
    ]

    campus = models.ForeignKey(
        Campus, on_delete=models.CASCADE,
        related_name='campus_stock_logs',
        verbose_name="Campus"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='campus_stock_logs',
        verbose_name="Product"
    )
    transaction_type = models.CharField(
        max_length=3, choices=TYPE_CHOICES,
        verbose_name="Type"
    )
    quantity = models.PositiveIntegerField(verbose_name="Quantity")
    note = models.TextField(blank=True, null=True, verbose_name="Note")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Created By"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Campus Stock Log"
        verbose_name_plural = "Campus Stock Logs"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.campus.name} — {self.product.name} ({self.transaction_type})"
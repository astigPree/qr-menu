from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models


class Business(models.Model):
    BUSINESS_TYPES = [
        ("restaurant", "Restaurant"),
        ("cafe", "Cafe"),
        ("ktv", "KTV"),
        ("small_business", "Small Business"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="owned_businesses",
    )
    contact_person = models.CharField(max_length=120, blank=True)
    contact_number = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    description = models.TextField(blank=True)
    business_type = models.CharField(
        max_length=40,
        choices=BUSINESS_TYPES,
        default="restaurant",
    )
    logo = models.ImageField(upload_to="business_logos/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "businesses"

    def __str__(self):
        return self.name


class Category(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(max_length=100)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["business", "sort_order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.business} - {self.name}"


class Product(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="products",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    full_description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["business", "category", "sort_order", "name"]

    def __str__(self):
        return f"{self.business} - {self.name}"

    def clean(self):
        if self.category_id and self.business_id and self.category.business_id != self.business_id:
            raise ValidationError({
                "category": "Category must belong to the selected business.",
            })


class QRLocation(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="qr_locations",
    )
    code = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)  # e.g. Table 1
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["business", "label"]

    def __str__(self):
        return f"{self.business} - {self.label}"


class ScanLog(models.Model):
    qr_location = models.ForeignKey(
        QRLocation,
        on_delete=models.SET_NULL,
        null=True,
        related_name="scan_logs",
    )
    scanned_at = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ["-scanned_at"]

    def __str__(self):
        return f"{self.qr_location} - {self.scanned_at:%Y-%m-%d %H:%M}"

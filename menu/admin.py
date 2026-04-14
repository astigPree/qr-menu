from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Business, Category, Product, QRLocation, ScanLog


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "business_type",
        "owner",
        "contact_person",
        "contact_number",
        "is_active",
        "preview_menu_link",
        "created_at",
    )
    list_filter = ("is_active", "business_type", "created_at")
    search_fields = ("name", "slug", "owner__username", "contact_person", "contact_number", "email")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "logo_preview", "preview_menu_link")
    fieldsets = (
        ("Business details", {
            "fields": (
                "name",
                "slug",
                "owner",
                "business_type",
                "is_active",
                "logo",
                "logo_preview",
            )
        }),
        ("Contact", {
            "fields": (
                "contact_person",
                "contact_number",
                "email",
                "address",
                "description",
            )
        }),
        ("System", {
            "fields": ("created_at", "preview_menu_link"),
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height:64px;width:64px;object-fit:contain;" alt="">', obj.logo.url)
        return "-"

    def preview_menu_link(self, obj):
        qr_location = obj.qr_locations.filter(is_active=True).first()
        if not qr_location:
            return "Create an active QR location first"
        url = reverse("menu:customer_menu", args=[qr_location.code])
        return format_html('<a href="{}" target="_blank" rel="noopener">Open Menu</a>', url)

    logo_preview.short_description = "Logo preview"
    preview_menu_link.short_description = "Preview menu"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "business", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("business", "is_active")
    search_fields = ("name", "business__name")
    autocomplete_fields = ("business",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "business",
        "category",
        "price",
        "is_available",
        "is_featured",
        "sort_order",
        "updated_at",
    )
    list_editable = ("price", "is_available", "is_featured", "sort_order")
    list_filter = ("business", "category", "is_available", "is_featured", "created_at")
    search_fields = ("name", "description", "full_description", "business__name", "category__name")
    autocomplete_fields = ("business", "category")
    readonly_fields = ("created_at", "updated_at", "image_preview")
    fieldsets = (
        ("Placement", {
            "fields": ("business", "category", "sort_order")
        }),
        ("Product details", {
            "fields": (
                "name",
                "description",
                "full_description",
                "price",
                "image",
                "image_preview",
            )
        }),
        ("Status", {
            "fields": ("is_available", "is_featured")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:72px;width:96px;object-fit:cover;border-radius:6px;" alt="">', obj.image.url)
        return "-"

    image_preview.short_description = "Image preview"


@admin.register(QRLocation)
class QRLocationAdmin(admin.ModelAdmin):
    list_display = ("label", "business", "code", "is_active", "menu_link", "created_at")
    list_editable = ("is_active",)
    list_filter = ("business", "is_active", "created_at")
    search_fields = ("label", "code", "business__name")
    autocomplete_fields = ("business",)
    readonly_fields = ("created_at", "menu_link")
    fieldsets = (
        ("QR location", {
            "fields": ("business", "label", "code", "is_active")
        }),
        ("Preview", {
            "fields": ("menu_link", "created_at")
        }),
    )

    def menu_link(self, obj):
        if not obj.pk:
            return "Save this QR location first"
        url = reverse("menu:customer_menu", args=[obj.code])
        return format_html('<a href="{}" target="_blank" rel="noopener">/m/{}</a>', url, obj.code)

    menu_link.short_description = "Menu link"


@admin.register(ScanLog)
class ScanLogAdmin(admin.ModelAdmin):
    list_display = ("qr_location", "business_name", "scanned_at", "ip")
    list_filter = ("qr_location__business", "scanned_at")
    search_fields = ("qr_location__code", "qr_location__label", "qr_location__business__name", "ip", "user_agent")
    readonly_fields = ("qr_location", "scanned_at", "ip", "user_agent")

    def business_name(self, obj):
        if obj.qr_location:
            return obj.qr_location.business
        return "-"

    business_name.short_description = "Business"

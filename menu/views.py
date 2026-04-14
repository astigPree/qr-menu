from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import (
    BusinessForm,
    CategoryForm,
    ClientBusinessProfileForm,
    ClientCategoryForm,
    ClientProductForm,
    ClientQRLocationForm,
    ProductForm,
    QRLocationForm,
)
from .models import Business, Category, Product, QRLocation, ScanLog


owner_required = user_passes_test(
    lambda user: user.is_active and user.is_staff,
    login_url="menu:owner_login",
)


def landing_page(request):
    return render(request, "menu/landing.html")


def customer_menu(request, code):
    qr_location = QRLocation.objects.select_related("business").filter(
        code=code,
        is_active=True,
        business__is_active=True,
    ).first()
    if qr_location:
        ScanLog.objects.create(
            qr_location=qr_location,
            ip=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
        )

    business = qr_location.business if qr_location else None

    products = Product.objects.filter(
        business=business,
        category__business=business,
        category__is_active=True,
    ).order_by(
        "sort_order",
        "name",
    )
    categories = list(Category.objects.filter(
        business=business,
        is_active=True,
    ).order_by(
        "sort_order",
        "name",
    ).prefetch_related(
        Prefetch("products", queryset=products, to_attr="menu_products")
    ))
    has_menu_items = any(category.menu_products for category in categories)

    return render(
        request,
        "menu/customer_menu.html",
        {
            "categories": categories,
            "has_menu_items": has_menu_items,
            "qr_code": code,
            "qr_location": qr_location,
            "business_name": business.name if business else "Anson QR Menu",
        },
    )


@owner_required
def owner_dashboard(request):
    recent_businesses = Business.objects.order_by("-created_at")[:6]
    businesses = Business.objects.all()
    qr_locations = QRLocation.objects.select_related("business").filter(is_active=True)

    preview_links = []
    for business in recent_businesses:
        qr_location = next(
            (location for location in qr_locations if location.business_id == business.id),
            None,
        )
        preview_links.append(
            {
                "business": business,
                "qr_location": qr_location,
                "url": reverse("menu:customer_menu", args=[qr_location.code]) if qr_location else None,
            }
        )

    return render(
        request,
        "menu/owner_dashboard.html",
        {
            "stats": [
                {"label": "Total Businesses", "value": businesses.count()},
                {"label": "Active Businesses", "value": businesses.filter(is_active=True).count()},
                {"label": "Categories", "value": Category.objects.count()},
                {"label": "Products", "value": Product.objects.count()},
                {"label": "QR Locations", "value": QRLocation.objects.count()},
            ],
            "recent_businesses": recent_businesses,
            "preview_links": preview_links,
            "admin_links": [
                {"label": "Businesses", "url": reverse("menu:owner_businesses"), "description": "Register, edit, activate, and preview businesses."},
                {"label": "Categories", "url": reverse("menu:owner_categories"), "description": "Create and sort categories per business."},
                {"label": "Products", "url": reverse("menu:owner_products"), "description": "Manage prices, images, availability, and featured items."},
                {"label": "QR Locations", "url": reverse("menu:owner_qr_locations"), "description": "Create table, counter, and room menu links."},
            ],
            "active_page": "dashboard",
        },
    )


@owner_required
def owner_businesses(request):
    businesses = Business.objects.all()
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    business_type = request.GET.get("type", "").strip()

    if query:
        businesses = businesses.filter(name__icontains=query)
    if status == "active":
        businesses = businesses.filter(is_active=True)
    elif status == "inactive":
        businesses = businesses.filter(is_active=False)
    if business_type:
        businesses = businesses.filter(business_type=business_type)

    return render(request, "menu/owner_businesses.html", {
        "businesses": businesses,
        "business_types": Business.BUSINESS_TYPES,
        "query": query,
        "status": status,
        "business_type": business_type,
        "active_page": "businesses",
    })


@owner_required
def owner_business_form(request, pk=None):
    business = get_object_or_404(Business, pk=pk) if pk else None
    form = BusinessForm(request.POST or None, request.FILES or None, instance=business)
    if request.method == "POST" and form.is_valid():
        business = form.save()
        messages.success(request, f"{business.name} saved.")
        return redirect("menu:owner_businesses")

    return render(request, "menu/owner_form.html", {
        "form": form,
        "title": "Edit Business" if business else "Add Business",
        "subtitle": "Business profile, contact details, status, and logo.",
        "back_url": reverse("menu:owner_businesses"),
        "active_page": "businesses",
    })


@owner_required
def owner_categories(request):
    categories = Category.objects.select_related("business")
    businesses = Business.objects.all()
    business_id = request.GET.get("business", "").strip()
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    if business_id:
        categories = categories.filter(business_id=business_id)
    if query:
        categories = categories.filter(name__icontains=query)
    if status == "active":
        categories = categories.filter(is_active=True)
    elif status == "inactive":
        categories = categories.filter(is_active=False)

    return render(request, "menu/owner_categories.html", {
        "categories": categories,
        "businesses": businesses,
        "business_id": business_id,
        "query": query,
        "status": status,
        "active_page": "categories",
    })


@owner_required
def owner_category_form(request, pk=None):
    category = get_object_or_404(Category, pk=pk) if pk else None
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        category = form.save()
        messages.success(request, f"{category.name} saved.")
        return redirect("menu:owner_categories")

    return render(request, "menu/owner_form.html", {
        "form": form,
        "title": "Edit Category" if category else "Add Category",
        "subtitle": "Assign the category to a business, set order, and control active status.",
        "back_url": reverse("menu:owner_categories"),
        "active_page": "categories",
    })


@owner_required
def owner_products(request):
    products = Product.objects.select_related("business", "category")
    businesses = Business.objects.all()
    categories = Category.objects.select_related("business")
    business_id = request.GET.get("business", "").strip()
    category_id = request.GET.get("category", "").strip()
    query = request.GET.get("q", "").strip()
    availability = request.GET.get("availability", "").strip()

    if business_id:
        products = products.filter(business_id=business_id)
        categories = categories.filter(business_id=business_id)
    if category_id:
        products = products.filter(category_id=category_id)
    if query:
        products = products.filter(name__icontains=query)
    if availability == "available":
        products = products.filter(is_available=True)
    elif availability == "unavailable":
        products = products.filter(is_available=False)

    return render(request, "menu/owner_products.html", {
        "products": products,
        "businesses": businesses,
        "categories": categories,
        "business_id": business_id,
        "category_id": category_id,
        "query": query,
        "availability": availability,
        "active_page": "products",
    })


@owner_required
def owner_product_form(request, pk=None):
    product = get_object_or_404(Product, pk=pk) if pk else None
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(request, f"{product.name} saved.")
        return redirect("menu:owner_products")

    return render(request, "menu/owner_form.html", {
        "form": form,
        "title": "Edit Product" if product else "Add Product",
        "subtitle": "Manage product details, price, image, availability, and display order.",
        "back_url": reverse("menu:owner_products"),
        "active_page": "products",
    })


@owner_required
def owner_qr_locations(request):
    qr_locations = QRLocation.objects.select_related("business")
    businesses = Business.objects.all()
    business_id = request.GET.get("business", "").strip()
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    if business_id:
        qr_locations = qr_locations.filter(business_id=business_id)
    if query:
        qr_locations = qr_locations.filter(code__icontains=query)
    if status == "active":
        qr_locations = qr_locations.filter(is_active=True)
    elif status == "inactive":
        qr_locations = qr_locations.filter(is_active=False)

    return render(request, "menu/owner_qr_locations.html", {
        "qr_locations": qr_locations,
        "businesses": businesses,
        "business_id": business_id,
        "query": query,
        "status": status,
        "active_page": "qr_locations",
    })


@owner_required
def owner_qr_location_form(request, pk=None):
    qr_location = get_object_or_404(QRLocation, pk=pk) if pk else None
    form = QRLocationForm(request.POST or None, instance=qr_location)
    if request.method == "POST" and form.is_valid():
        qr_location = form.save()
        messages.success(request, f"{qr_location.label} saved.")
        return redirect("menu:owner_qr_locations")

    return render(request, "menu/owner_form.html", {
        "form": form,
        "title": "Edit QR Location" if qr_location else "Add QR Location",
        "subtitle": "Create QR-linked entry points such as table-1, counter, or ktv-room-2.",
        "back_url": reverse("menu:owner_qr_locations"),
        "active_page": "qr_locations",
    })


@login_required
def client_dashboard(request):
    business = get_client_business(request)
    if not business:
        return render_client_no_business(request)

    categories = Category.objects.filter(business=business)
    products = Product.objects.filter(business=business)
    qr_locations = QRLocation.objects.filter(business=business)
    preview_location = qr_locations.filter(is_active=True).first()

    return render(request, "menu/client_dashboard.html", {
        "business": business,
        "preview_url": reverse("menu:customer_menu", args=[preview_location.code]) if preview_location else None,
        "recent_products": products.select_related("category").order_by("-created_at")[:6],
        "stats": [
            {"label": "Categories", "value": categories.count()},
            {"label": "Products", "value": products.count()},
            {"label": "Available", "value": products.filter(is_available=True).count()},
            {"label": "Unavailable", "value": products.filter(is_available=False).count()},
            {"label": "QR Locations", "value": qr_locations.count()},
        ],
        "active_page": "dashboard",
    })


@login_required
def client_profile(request):
    business = get_client_business(request)
    if not business:
        return render_client_no_business(request)

    form = ClientBusinessProfileForm(request.POST or None, request.FILES or None, instance=business)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Business profile saved.")
        return redirect("menu:client_profile")

    return render(request, "menu/client_profile.html", {
        "business": business,
        "form": form,
        "title": "Business Profile",
        "subtitle": "Update the information customers see and how your business is identified.",
        "readonly_status": "Active" if business.is_active else "Inactive",
        "back_url": reverse("menu:client_dashboard"),
        "active_page": "profile",
    })


@login_required
def client_categories(request):
    business = get_client_business(request)
    if not business:
        return render_client_no_business(request)

    categories = Category.objects.filter(business=business)
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    if query:
        categories = categories.filter(name__icontains=query)
    if status == "active":
        categories = categories.filter(is_active=True)
    elif status == "inactive":
        categories = categories.filter(is_active=False)

    return render(request, "menu/client_categories.html", {
        "business": business,
        "categories": categories,
        "query": query,
        "status": status,
        "active_page": "categories",
    })


@login_required
def client_category_form(request, pk=None):
    business = get_client_business(request)
    if not business:
        return render_client_no_business(request)

    category = get_object_or_404(Category, pk=pk, business=business) if pk else None
    form = ClientCategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        category = form.save(commit=False)
        category.business = business
        category.save()
        messages.success(request, f"{category.name} saved.")
        return redirect("menu:client_categories")

    return render(request, "menu/client_form.html", {
        "business": business,
        "form": form,
        "title": "Edit Category" if category else "Add Category",
        "subtitle": "Create and sort the sections customers browse in your menu.",
        "back_url": reverse("menu:client_categories"),
        "active_page": "categories",
    })


@login_required
def client_products(request):
    business = get_client_business(request)
    if not business:
        return render_client_no_business(request)

    products = Product.objects.filter(business=business).select_related("category")
    categories = Category.objects.filter(business=business)
    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    availability = request.GET.get("availability", "").strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_id:
        products = products.filter(category_id=category_id)
    if availability == "available":
        products = products.filter(is_available=True)
    elif availability == "unavailable":
        products = products.filter(is_available=False)

    return render(request, "menu/client_products.html", {
        "business": business,
        "products": products,
        "categories": categories,
        "query": query,
        "category_id": category_id,
        "availability": availability,
        "active_page": "products",
    })


@login_required
def client_product_form(request, pk=None):
    business = get_client_business(request)
    if not business:
        return render_client_no_business(request)

    product = get_object_or_404(Product, pk=pk, business=business) if pk else None
    form = ClientProductForm(request.POST or None, request.FILES or None, instance=product, business=business)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(request, f"{product.name} saved.")
        return redirect("menu:client_products")

    return render(request, "menu/client_form.html", {
        "business": business,
        "form": form,
        "title": "Edit Product" if product else "Add Product",
        "subtitle": "Keep pricing, images, descriptions, and availability up to date.",
        "back_url": reverse("menu:client_products"),
        "active_page": "products",
    })


@login_required
def client_toggle_product_availability(request, pk):
    business = get_client_business(request)
    if not business:
        return render_client_no_business(request)
    product = get_object_or_404(Product, pk=pk, business=business)
    if request.method == "POST":
        product.is_available = not product.is_available
        product.save(update_fields=["is_available", "updated_at"])
        messages.success(request, f"{product.name} is now {'available' if product.is_available else 'unavailable'}.")
    return redirect("menu:client_products")


@login_required
def client_qr_locations(request):
    business = get_client_business(request)
    if not business:
        return render_client_no_business(request)

    qr_locations = QRLocation.objects.filter(business=business)
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    if query:
        qr_locations = qr_locations.filter(Q(code__icontains=query) | Q(label__icontains=query))
    if status == "active":
        qr_locations = qr_locations.filter(is_active=True)
    elif status == "inactive":
        qr_locations = qr_locations.filter(is_active=False)

    return render(request, "menu/client_qr_locations.html", {
        "business": business,
        "qr_locations": qr_locations,
        "query": query,
        "status": status,
        "active_page": "qr_locations",
    })


@login_required
def client_qr_location_form(request, pk=None):
    business = get_client_business(request)
    if not business:
        return render_client_no_business(request)

    qr_location = get_object_or_404(QRLocation, pk=pk, business=business) if pk else None
    form = ClientQRLocationForm(request.POST or None, instance=qr_location, business=business)
    if request.method == "POST" and form.is_valid():
        qr_location = form.save()
        messages.success(request, f"{qr_location.label} saved.")
        return redirect("menu:client_qr_locations")

    return render(request, "menu/client_form.html", {
        "business": business,
        "form": form,
        "title": "Edit QR Location" if qr_location else "Add QR Location",
        "subtitle": "Create QR menu entry points for tables, counters, rooms, or service areas.",
        "back_url": reverse("menu:client_qr_locations"),
        "active_page": "qr_locations",
    })


def get_client_business(request):
    return Business.objects.filter(owner=request.user).order_by("name").first()


def render_client_no_business(request):
    return render(request, "menu/client_no_business.html", {
        "active_page": "dashboard",
    })


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

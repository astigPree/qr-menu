from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "menu"

urlpatterns = [
    path(
        "owner/login/",
        auth_views.LoginView.as_view(
            template_name="menu/owner_login.html",
            redirect_authenticated_user=False,
            next_page="menu:owner_dashboard",
            extra_context={"login_role": "System Owner"},
        ),
        name="owner_login",
    ),
    path(
        "owner/logout/",
        auth_views.LogoutView.as_view(next_page="menu:owner_login"),
        name="owner_logout",
    ),
    path(
        "client/login/",
        auth_views.LoginView.as_view(
            template_name="menu/client_login.html",
            redirect_authenticated_user=True,
        ),
        name="client_login",
    ),
    path(
        "client/logout/",
        auth_views.LogoutView.as_view(next_page="menu:client_login"),
        name="client_logout",
    ),
    path("client/", views.client_dashboard, name="client_dashboard"),
    path("client/profile/", views.client_profile, name="client_profile"),
    path("client/categories/", views.client_categories, name="client_categories"),
    path("client/categories/new/", views.client_category_form, name="client_category_add"),
    path("client/categories/<int:pk>/edit/", views.client_category_form, name="client_category_edit"),
    path("client/products/", views.client_products, name="client_products"),
    path("client/products/new/", views.client_product_form, name="client_product_add"),
    path("client/products/<int:pk>/edit/", views.client_product_form, name="client_product_edit"),
    path("client/products/<int:pk>/toggle-availability/", views.client_toggle_product_availability, name="client_product_toggle"),
    path("client/qr-locations/", views.client_qr_locations, name="client_qr_locations"),
    path("client/qr-locations/new/", views.client_qr_location_form, name="client_qr_location_add"),
    path("client/qr-locations/<int:pk>/edit/", views.client_qr_location_form, name="client_qr_location_edit"),
    path("owner/", views.owner_dashboard, name="owner_dashboard"),
    path("owner/businesses/", views.owner_businesses, name="owner_businesses"),
    path("owner/businesses/new/", views.owner_business_form, name="owner_business_add"),
    path("owner/businesses/<int:pk>/edit/", views.owner_business_form, name="owner_business_edit"),
    path("owner/categories/", views.owner_categories, name="owner_categories"),
    path("owner/categories/new/", views.owner_category_form, name="owner_category_add"),
    path("owner/categories/<int:pk>/edit/", views.owner_category_form, name="owner_category_edit"),
    path("owner/products/", views.owner_products, name="owner_products"),
    path("owner/products/new/", views.owner_product_form, name="owner_product_add"),
    path("owner/products/<int:pk>/edit/", views.owner_product_form, name="owner_product_edit"),
    path("owner/qr-locations/", views.owner_qr_locations, name="owner_qr_locations"),
    path("owner/qr-locations/new/", views.owner_qr_location_form, name="owner_qr_location_add"),
    path("owner/qr-locations/<int:pk>/edit/", views.owner_qr_location_form, name="owner_qr_location_edit"),
    path("m/<slug:code>", views.customer_menu, name="customer_menu"),
    path("m/<slug:code>/", views.customer_menu, name="customer_menu_slash"),
    path("", views.landing_page, name="landing"),
]

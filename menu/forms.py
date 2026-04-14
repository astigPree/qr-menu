from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Business, Category, Product, QRLocation


class OwnerFormMixin:
    def apply_owner_widgets(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            else:
                widget.attrs.setdefault("class", "form-control")


class BusinessForm(OwnerFormMixin, forms.ModelForm):
    owner_username = forms.CharField(
        label="Owner username",
        max_length=150,
        required=False,
        help_text="Create or update the client login username for this business.",
    )
    owner_password = forms.CharField(
        label="Owner password",
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Required when creating a new business owner account. Leave blank on edit to keep the current password.",
    )
    owner_password_confirm = forms.CharField(
        label="Confirm owner password",
        required=False,
        widget=forms.PasswordInput(render_value=False),
    )

    class Meta:
        model = Business
        fields = [
            "name",
            "slug",
            "contact_person",
            "contact_number",
            "email",
            "address",
            "description",
            "business_type",
            "logo",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner_instance = self.instance.owner if self.instance and self.instance.pk else None
        if self.owner_instance:
            self.fields["owner_username"].initial = self.owner_instance.username
        if not self.instance.pk:
            self.fields["owner_password"].required = True
            self.fields["owner_password_confirm"].required = True
        self.apply_owner_widgets()
        self.fields["address"].widget.attrs.update({"rows": 3})
        self.fields["description"].widget.attrs.update({"rows": 3})
        self.fields["logo"].widget.attrs.update({"accept": "image/*"})

    def clean_owner_username(self):
        username = self.cleaned_data.get("owner_username", "").strip()
        User = get_user_model()
        if not username:
            return username
        existing_user = User.objects.filter(username=username).first()
        if existing_user and existing_user != self.owner_instance:
            raise forms.ValidationError("This username is already used by another account.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("owner_username")
        password = cleaned_data.get("owner_password")
        password_confirm = cleaned_data.get("owner_password_confirm")

        if not self.instance.pk and not username:
            self.add_error("owner_username", "Owner username is required for a new business.")
        if password or password_confirm:
            if password != password_confirm:
                self.add_error("owner_password_confirm", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        business = super().save(commit=False)
        username = self.cleaned_data.get("owner_username")
        password = self.cleaned_data.get("owner_password")

        if username:
            User = get_user_model()
            user = self.owner_instance or User(username=username)
            user.username = username
            user.email = business.email
            user.first_name = business.contact_person
            user.is_staff = False
            if password:
                user.set_password(password)
            if commit:
                user.save()
            business.owner = user

        if commit:
            business.save()
            self.save_m2m()
        return business


class CategoryForm(OwnerFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ["business", "name", "sort_order", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_owner_widgets()


class ProductForm(OwnerFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "business",
            "category",
            "name",
            "description",
            "full_description",
            "price",
            "image",
            "is_available",
            "is_featured",
            "sort_order",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        business_id = None
        if self.data.get("business"):
            business_id = self.data.get("business")
        elif self.instance.pk:
            business_id = self.instance.business_id

        if business_id:
            category_filter = Category.objects.filter(business_id=business_id)
            if self.instance.pk and self.instance.category_id:
                self.fields["category"].queryset = category_filter.filter(
                    Q(is_active=True) | Q(pk=self.instance.category_id)
                ).order_by("sort_order", "name")
            else:
                self.fields["category"].queryset = category_filter.filter(
                    is_active=True,
                ).order_by("sort_order", "name")
        else:
            self.fields["category"].queryset = Category.objects.filter(
                is_active=True,
            ).select_related("business").order_by("business__name", "sort_order", "name")

        self.apply_owner_widgets()
        self.fields["description"].widget.attrs.update({"rows": 2})
        self.fields["full_description"].widget.attrs.update({"rows": 4})
        self.fields["image"].widget.attrs.update({"accept": "image/*"})


class QRLocationForm(OwnerFormMixin, forms.ModelForm):
    class Meta:
        model = QRLocation
        fields = ["business", "code", "label", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_owner_widgets()


class ClientBusinessProfileForm(OwnerFormMixin, forms.ModelForm):
    class Meta:
        model = Business
        fields = [
            "name",
            "contact_person",
            "contact_number",
            "email",
            "address",
            "description",
            "business_type",
            "logo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_owner_widgets()
        self.fields["address"].widget.attrs.update({"rows": 3})
        self.fields["description"].widget.attrs.update({"rows": 3})
        self.fields["logo"].widget.attrs.update({"accept": "image/*"})


class ClientCategoryForm(OwnerFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "sort_order", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_owner_widgets()


class ClientProductForm(OwnerFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "name",
            "description",
            "full_description",
            "price",
            "image",
            "is_available",
            "is_featured",
            "sort_order",
        ]

    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop("business")
        super().__init__(*args, **kwargs)
        category_filter = Category.objects.filter(business=self.business)
        if self.instance.pk and self.instance.category_id:
            self.fields["category"].queryset = category_filter.filter(
                Q(is_active=True) | Q(pk=self.instance.category_id)
            ).order_by("sort_order", "name")
        else:
            self.fields["category"].queryset = category_filter.filter(
                is_active=True,
            ).order_by("sort_order", "name")
        self.apply_owner_widgets()
        self.fields["description"].widget.attrs.update({"rows": 2})
        self.fields["full_description"].widget.attrs.update({"rows": 4})
        self.fields["image"].widget.attrs.update({"accept": "image/*"})

    def save(self, commit=True):
        product = super().save(commit=False)
        product.business = self.business
        if commit:
            product.save()
            self.save_m2m()
        return product


class ClientQRLocationForm(OwnerFormMixin, forms.ModelForm):
    class Meta:
        model = QRLocation
        fields = ["code", "label", "is_active"]

    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop("business")
        super().__init__(*args, **kwargs)
        self.apply_owner_widgets()

    def save(self, commit=True):
        qr_location = super().save(commit=False)
        qr_location.business = self.business
        if commit:
            qr_location.save()
            self.save_m2m()
        return qr_location

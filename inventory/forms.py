from django import forms
from .models import Category, Product, StockLog, Vendor, Campus, CampusInventory


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Books, Khata, Diary...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description...'
            }),
        }


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'mobile', 'address', 'bank_account']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Vendor name...'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '01XXXXXXXXX'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Vendor address...'
            }),
            'bank_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank name, Account number...'
            }),
        }


class CampusForm(forms.ModelForm):
    class Meta:
        model = Campus
        fields = ['name', 'address', 'admin', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Campus name...'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Campus address...'
            }),
            'admin': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CampusInventoryForm(forms.ModelForm):
    class Meta:
        model = CampusInventory
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Enter quantity...'
            }),
        }

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty is None or qty < 0:
            raise forms.ValidationError("Quantity cannot be negative.")
        return qty


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'vendor', 'purchase_price', 'selling_price',
                  'opening_stock', 'low_stock_threshold', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product name...'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'purchase_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'selling_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'opening_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'low_stock_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor'].required = False
        self.fields['vendor'].empty_label = "— Select Vendor (Optional) —"

    def clean(self):
        cleaned_data = super().clean()
        purchase_price = cleaned_data.get('purchase_price')
        selling_price = cleaned_data.get('selling_price')
        if purchase_price and selling_price:
            if selling_price < purchase_price:
                raise forms.ValidationError(
                    "⚠️ Selling price cannot be less than purchase price!"
                )
        return cleaned_data


class StockInForm(forms.ModelForm):
    class Meta:
        model = StockLog
        fields = ['product', 'vendor', 'quantity', 'note']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Enter quantity...'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional note...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor'].required = True
        self.fields['vendor'].empty_label = "— Select Vendor —"

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty and qty <= 0:
            raise forms.ValidationError("Quantity must be at least 1.")
        return qty


class StockOutForm(forms.ModelForm):
    class Meta:
        model = StockLog
        fields = ['product', 'quantity', 'note']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Enter quantity...'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional note...'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        if product and quantity:
            if quantity > product.quantity:
                raise forms.ValidationError(
                    f"❌ Insufficient stock! Available: {product.quantity} units."
                )
        return cleaned_data


class StockFilterForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        empty_label="All Products",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    vendor = forms.ModelChoiceField(
        queryset=Vendor.objects.all(),
        required=False,
        empty_label="All Vendors",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    transaction_type = forms.ChoiceField(
        choices=[('', 'All Types'), ('IN', 'Stock IN'), ('OUT', 'Stock OUT')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
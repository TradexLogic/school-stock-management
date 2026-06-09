import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import HttpResponse

from .models import (Category, Product, StockLog, Vendor,
                     Campus, CampusInventory, ActivityLog, CampusStockLog)
from .forms import (CategoryForm, ProductForm, StockInForm,
                    StockOutForm, StockFilterForm, VendorForm,
                    CampusForm, CampusInventoryForm)


# ── HELPER FUNCTIONS ─────────────────────────────────────────

def is_super_admin(user):
    return user.is_superuser or user.is_staff


def log_activity(user, action):
    ActivityLog.objects.create(user=user, action=action)


# ── DASHBOARD ────────────────────────────────────────────────

@login_required
def dashboard(request):
    if is_super_admin(request.user):
        total_products = Product.objects.count()
        total_categories = Category.objects.count()
        total_vendors = Vendor.objects.count()
        total_campuses = Campus.objects.count()
        total_stock_qty = Product.objects.aggregate(
            total=Sum('quantity'))['total'] or 0

        all_products = Product.objects.all()
        low_stock_products = [p for p in all_products if p.is_low_stock][:5]
        low_stock_count = sum(1 for p in all_products if p.is_low_stock)
        out_of_stock_count = Product.objects.filter(quantity=0).count()

        stock_purchase_value = sum(
            p.quantity * p.purchase_price for p in all_products)
        stock_selling_value = sum(
            p.quantity * p.selling_price for p in all_products)

        recent_transactions = StockLog.objects.select_related(
            'product', 'product__category', 'created_by', 'vendor'
        ).order_by('-created_at')[:10]

        today = timezone.now().date()
        today_in = StockLog.objects.filter(
            created_at__date=today, transaction_type='IN'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        today_out = StockLog.objects.filter(
            created_at__date=today, transaction_type='OUT'
        ).aggregate(total=Sum('quantity'))['total'] or 0

        campuses = Campus.objects.all()

        return render(request, 'inventory/dashboard_super.html', {
            'total_products': total_products,
            'total_categories': total_categories,
            'total_vendors': total_vendors,
            'total_campuses': total_campuses,
            'total_stock_qty': total_stock_qty,
            'low_stock_products': low_stock_products,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'stock_purchase_value': stock_purchase_value,
            'stock_selling_value': stock_selling_value,
            'recent_transactions': recent_transactions,
            'today_in': today_in,
            'today_out': today_out,
            'campuses': campuses,
            'page_title': 'Super Admin Dashboard',
        })

    else:
        try:
            campus = request.user.campus
        except Exception:
            messages.error(request, '❌ No campus assigned to your account.')
            return render(request, 'inventory/no_campus.html', {
                'page_title': 'No Campus Assigned'
            })

        inventories = CampusInventory.objects.filter(
            campus=campus
        ).select_related('product', 'product__category')

        total_products = inventories.filter(quantity__gt=0).count()
        total_stock_qty = inventories.aggregate(
            total=Sum('quantity'))['total'] or 0
        total_selling_value = sum(
            i.quantity * i.product.selling_price for i in inventories)
        low_stock = [i for i in inventories
                     if i.quantity <= i.product.low_stock_threshold]

        return render(request, 'inventory/dashboard_campus.html', {
            'campus': campus,
            'inventories': inventories,
            'total_products': total_products,
            'total_stock_qty': total_stock_qty,
            'total_selling_value': total_selling_value,
            'low_stock': low_stock,
            'page_title': f'{campus.name} Dashboard',
        })


# ── CAMPUS VIEWS ─────────────────────────────────────────────

@login_required
def campus_list(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    campuses = Campus.objects.all()
    return render(request, 'inventory/campus_list.html', {
        'campuses': campuses,
        'page_title': 'Campuses',
    })


@login_required
def campus_create(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    if request.method == 'POST':
        form = CampusForm(request.POST)
        if form.is_valid():
            campus = form.save()
            log_activity(request.user, f'Created campus: {campus.name}')
            messages.success(request, f'✅ Campus "{campus.name}" created!')
            return redirect('campus_list')
    else:
        form = CampusForm()
    return render(request, 'inventory/campus_form.html', {
        'form': form,
        'page_title': 'Add Campus',
        'form_title': 'Add New Campus',
    })


@login_required
def campus_edit(request, pk):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    campus = get_object_or_404(Campus, pk=pk)
    if request.method == 'POST':
        form = CampusForm(request.POST, instance=campus)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Campus "{campus.name}" updated!')
            return redirect('campus_list')
    else:
        form = CampusForm(instance=campus)
    return render(request, 'inventory/campus_form.html', {
        'form': form,
        'page_title': 'Edit Campus',
        'form_title': f'Edit: {campus.name}',
    })


@login_required
def campus_detail(request, pk):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    campus = get_object_or_404(Campus, pk=pk)
    inventories = CampusInventory.objects.filter(
        campus=campus
    ).select_related('product', 'product__category')
    total_qty = inventories.aggregate(t=Sum('quantity'))['t'] or 0
    total_value = sum(
        i.quantity * i.product.selling_price for i in inventories)
    return render(request, 'inventory/campus_detail.html', {
        'campus': campus,
        'inventories': inventories,
        'total_qty': total_qty,
        'total_value': total_value,
        'page_title': campus.name,
    })


# ── CAMPUS INVENTORY INPUT ────────────────────────────────────

@login_required
def campus_inventory_input(request):
    if is_super_admin(request.user):
        return redirect('inventory_overview')

    try:
        campus = request.user.campus
    except Exception:
        messages.error(request, '❌ No campus assigned!')
        return redirect('dashboard')

    if request.method == 'POST':
        product_id = request.POST.get('product')
        quantity_str = request.POST.get('quantity')

        if not product_id or quantity_str is None:
            messages.error(request, '❌ Product and quantity are required!')
        else:
            try:
                quantity = int(quantity_str)
                if quantity < 0:
                    messages.error(request, '❌ Quantity cannot be negative!')
                else:
                    product = Product.objects.get(pk=product_id)

                    inv, created = CampusInventory.objects.get_or_create(
                        campus=campus,
                        product=product,
                        defaults={
                            'quantity': 0,
                            'updated_by': request.user
                        }
                    )

                    old_qty = inv.quantity

                    if quantity > old_qty:
                        CampusStockLog.objects.create(
                            campus=campus,
                            product=product,
                            transaction_type='IN',
                            quantity=quantity - old_qty,
                            note='Stock IN',
                            created_by=request.user
                        )
                    elif quantity < old_qty:
                        CampusStockLog.objects.create(
                            campus=campus,
                            product=product,
                            transaction_type='OUT',
                            quantity=old_qty - quantity,
                            note='Stock adjusted',
                            created_by=request.user
                        )

                    inv.quantity = quantity
                    inv.updated_by = request.user
                    inv.save()

                    log_activity(
                        request.user,
                        f'Stock IN: {product.name} = {quantity} at {campus.name}'
                    )
                    messages.success(
                        request,
                        f'✅ "{product.name}" updated to {quantity} units!'
                    )
                    return redirect('campus_inventory_input')

            except Product.DoesNotExist:
                messages.error(request, '❌ Product not found!')
            except ValueError:
                messages.error(request, '❌ Invalid quantity!')
            except Exception as e:
                import traceback
                traceback.print_exc()
                messages.error(request, f'❌ Error: {str(e)}')

    products = Product.objects.select_related('category').order_by('name')
    inventories = CampusInventory.objects.filter(
        campus=campus
    ).select_related('product', 'product__category')

    return render(request, 'inventory/campus_inventory_input.html', {
        'products': products,
        'campus': campus,
        'inventories': inventories,
        'page_title': 'Stock IN',
    })


# ── CAMPUS STOCK OUT ──────────────────────────────────────────

@login_required
def campus_stock_out(request):
    if is_super_admin(request.user):
        return redirect('stock_out')

    try:
        campus = request.user.campus
    except Exception:
        messages.error(request, '❌ No campus assigned!')
        return redirect('dashboard')

    if request.method == 'POST':
        product_id = request.POST.get('product')
        quantity_str = request.POST.get('quantity')
        note = request.POST.get('note', '')

        if not product_id or not quantity_str:
            messages.error(request, '❌ Product and quantity are required!')
        else:
            try:
                quantity = int(quantity_str)
                if quantity <= 0:
                    messages.error(request, '❌ Quantity must be at least 1!')
                else:
                    inv = CampusInventory.objects.get(
                        campus=campus, product_id=product_id
                    )
                    if quantity > inv.quantity:
                        messages.error(
                            request,
                            f'❌ Insufficient stock! Available: {inv.quantity} units.'
                        )
                    else:
                        inv.quantity -= quantity
                        inv.updated_by = request.user
                        inv.save()

                        CampusStockLog.objects.create(
                            campus=campus,
                            product=inv.product,
                            transaction_type='OUT',
                            quantity=quantity,
                            note=note,
                            created_by=request.user
                        )
                        log_activity(
                            request.user,
                            f'Stock OUT: {inv.product.name} x{quantity} from {campus.name}'
                        )
                        messages.success(
                            request,
                            f'✅ {quantity} units of "{inv.product.name}" issued!'
                        )
                        return redirect('campus_stock_out')

            except CampusInventory.DoesNotExist:
                messages.error(
                    request, '❌ Product not found in your campus inventory!')
            except ValueError:
                messages.error(request, '❌ Invalid quantity!')
            except Exception as e:
                import traceback
                traceback.print_exc()
                messages.error(request, f'❌ Error: {str(e)}')

    inventories = CampusInventory.objects.filter(
        campus=campus, quantity__gt=0
    ).select_related('product', 'product__category')

    return render(request, 'inventory/campus_stock_out.html', {
        'campus': campus,
        'inventories': inventories,
        'page_title': 'Stock OUT',
    })


# ── CATEGORY VIEWS ────────────────────────────────────────────

@login_required
def category_list(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    query = request.GET.get('q', '')
    categories = Category.objects.annotate(
        product_count_ann=Count('products')
    ).order_by('name')
    if query:
        categories = categories.filter(name__icontains=query)
    paginator = Paginator(categories, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'inventory/category_list.html', {
        'page_obj': page_obj,
        'query': query,
        'page_title': 'Categories',
    })


@login_required
def category_create(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            log_activity(request.user, f'Created category: {category.name}')
            messages.success(request, f'✅ Category "{category.name}" created!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'inventory/category_form.html', {
        'form': form,
        'page_title': 'Add Category',
        'form_title': 'Add New Category',
    })


@login_required
def category_edit(request, pk):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Category "{category.name}" updated!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'inventory/category_form.html', {
        'form': form,
        'page_title': 'Edit Category',
        'form_title': f'Edit: {category.name}',
    })


@login_required
def category_delete(request, pk):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        if category.products.exists():
            messages.error(request, '❌ Cannot delete — has products!')
            return redirect('category_list')
        name = category.name
        category.delete()
        messages.success(request, f'✅ Category "{name}" deleted!')
        return redirect('category_list')
    return render(request, 'inventory/confirm_delete.html', {
        'object': category,
        'object_type': 'Category',
        'page_title': 'Delete Category',
    })


# ── VENDOR VIEWS ──────────────────────────────────────────────

@login_required
def vendor_list(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    query = request.GET.get('q', '')
    vendors = Vendor.objects.all().order_by('name')
    if query:
        vendors = vendors.filter(
            Q(name__icontains=query) | Q(mobile__icontains=query)
        )
    paginator = Paginator(vendors, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'inventory/vendor_list.html', {
        'page_obj': page_obj,
        'query': query,
        'page_title': 'Vendors',
    })


@login_required
def vendor_create(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            vendor = form.save()
            messages.success(request, f'✅ Vendor "{vendor.name}" created!')
            return redirect('vendor_list')
    else:
        form = VendorForm()
    return render(request, 'inventory/vendor_form.html', {
        'form': form,
        'page_title': 'Add Vendor',
        'form_title': 'Add New Vendor',
    })


@login_required
def vendor_edit(request, pk):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Vendor "{vendor.name}" updated!')
            return redirect('vendor_list')
    else:
        form = VendorForm(instance=vendor)
    return render(request, 'inventory/vendor_form.html', {
        'form': form,
        'page_title': 'Edit Vendor',
        'form_title': f'Edit: {vendor.name}',
    })


@login_required
def vendor_delete(request, pk):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        name = vendor.name
        vendor.delete()
        messages.success(request, f'✅ Vendor "{name}" deleted!')
        return redirect('vendor_list')
    return render(request, 'inventory/confirm_delete.html', {
        'object': vendor,
        'object_type': 'Vendor',
        'page_title': 'Delete Vendor',
    })


@login_required
def vendor_detail(request, pk):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    vendor = get_object_or_404(Vendor, pk=pk)
    logs = vendor.stock_logs.select_related(
        'product', 'product__category', 'created_by'
    ).order_by('-created_at')
    total_amount = sum(
        log.quantity * log.product.purchase_price for log in logs)
    total_quantity = logs.aggregate(t=Sum('quantity'))['t'] or 0
    paginator = Paginator(logs, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'inventory/vendor_detail.html', {
        'vendor': vendor,
        'page_obj': page_obj,
        'total_amount': total_amount,
        'total_quantity': total_quantity,
        'page_title': vendor.name,
    })


# ── PRODUCT VIEWS ─────────────────────────────────────────────

@login_required
def product_list(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    stock_filter = request.GET.get('stock', '')
    products = Product.objects.select_related('category').order_by('name')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(category__name__icontains=query)
        )
    if category_filter:
        products = products.filter(category_id=category_filter)
    if stock_filter == 'out':
        products = products.filter(quantity=0)
    elif stock_filter == 'low':
        all_prods = list(products)
        products = [p for p in all_prods if p.is_low_stock and p.quantity > 0]
    elif stock_filter == 'ok':
        all_prods = list(products)
        products = [p for p in all_prods if not p.is_low_stock]
    paginator = Paginator(products, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.all()
    return render(request, 'inventory/product_list.html', {
        'page_obj': page_obj,
        'query': query,
        'category_filter': category_filter,
        'stock_filter': stock_filter,
        'categories': categories,
        'page_title': 'Products',
    })


@login_required
def product_detail(request, pk):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    product = get_object_or_404(Product, pk=pk)
    stock_history = product.stock_logs.select_related(
        'created_by', 'vendor'
    ).order_by('-created_at')[:20]
    total_in = product.stock_logs.filter(
        transaction_type='IN'
    ).aggregate(total=Sum('quantity'))['total'] or 0
    total_out = product.stock_logs.filter(
        transaction_type='OUT'
    ).aggregate(total=Sum('quantity'))['total'] or 0
    return render(request, 'inventory/product_detail.html', {
        'product': product,
        'stock_history': stock_history,
        'total_in': total_in,
        'total_out': total_out,
        'page_title': product.name,
    })


@login_required
def product_create(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            opening = form.cleaned_data.get('opening_stock', 0)
            product.opening_stock = opening
            product.quantity = opening
            product.save()
            log_activity(request.user, f'Created product: {product.name}')
            messages.success(request, f'✅ Product "{product.name}" created!')
            return redirect('product_list')
        else:
            messages.error(request, '❌ Please fix the errors below.')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {
        'form': form,
        'page_title': 'Add Product',
        'form_title': 'Add New Product',
    })


@login_required
def product_edit(request, pk):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Product "{product.name}" updated!')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {
        'form': form,
        'page_title': 'Edit Product',
        'form_title': f'Edit: {product.name}',
    })


@login_required
def product_delete(request, pk):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'✅ Product "{name}" deleted!')
        return redirect('product_list')
    return render(request, 'inventory/confirm_delete.html', {
        'object': product,
        'object_type': 'Product',
        'page_title': 'Delete Product',
    })


# ── STOCK VIEWS ───────────────────────────────────────────────

@login_required
def stock_log_list(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    query = request.GET.get('q', '')
    type_filter = request.GET.get('type', '')
    logs = StockLog.objects.select_related(
        'product', 'product__category', 'created_by', 'vendor'
    ).order_by('-created_at')
    if query:
        logs = logs.filter(
            Q(product__name__icontains=query) |
            Q(voucher_number__icontains=query) |
            Q(vendor__name__icontains=query)
        )
    if type_filter in ['IN', 'OUT']:
        logs = logs.filter(transaction_type=type_filter)
    paginator = Paginator(logs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'inventory/stock_log_list.html', {
        'page_obj': page_obj,
        'query': query,
        'type_filter': type_filter,
        'page_title': 'Stock Transactions',
    })


@login_required
def stock_in(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    if request.method == 'POST':
        form = StockInForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.transaction_type = 'IN'
            log.created_by = request.user
            try:
                log.save()
                log_activity(
                    request.user,
                    f'Stock IN: {log.product.name} x{log.quantity} | {log.voucher_number}'
                )
                messages.success(
                    request,
                    f'✅ Stock IN successful! Voucher: {log.voucher_number}'
                )
                return redirect('voucher_detail', pk=log.pk)
            except Exception as e:
                messages.error(request, f'❌ Error: {e}')
    else:
        form = StockInForm()
    return render(request, 'inventory/stock_form.html', {
        'form': form,
        'form_type': 'IN',
        'page_title': 'Stock IN',
        'form_title': '📥 Add Stock IN',
        'btn_class': 'success',
    })


@login_required
def stock_out(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    if request.method == 'POST':
        form = StockOutForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.transaction_type = 'OUT'
            log.created_by = request.user
            try:
                log.save()
                log_activity(
                    request.user,
                    f'Stock OUT: {log.product.name} x{log.quantity} | {log.voucher_number}'
                )
                messages.success(
                    request,
                    f'✅ Stock OUT successful! Voucher: {log.voucher_number}'
                )
                return redirect('voucher_detail', pk=log.pk)
            except Exception as e:
                messages.error(request, f'❌ Error: {e}')
    else:
        form = StockOutForm()
    return render(request, 'inventory/stock_form.html', {
        'form': form,
        'form_type': 'OUT',
        'page_title': 'Stock OUT',
        'form_title': '📤 Stock OUT',
        'btn_class': 'danger',
    })


# ── VOUCHER ───────────────────────────────────────────────────

@login_required
def voucher_detail(request, pk):
    log = get_object_or_404(
        StockLog.objects.select_related(
            'product', 'product__category', 'vendor', 'created_by'
        ), pk=pk)
    return render(request, 'inventory/voucher_detail.html', {
        'log': log,
        'is_super_admin': is_super_admin(request.user),
        'page_title': f'Voucher — {log.voucher_number}',
    })


# ── REPORTS ───────────────────────────────────────────────────

@login_required
def reports(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    form = StockFilterForm(request.GET or None)
    logs = StockLog.objects.select_related(
        'product', 'product__category', 'created_by', 'vendor'
    ).order_by('-created_at')
    if form.is_valid():
        product = form.cleaned_data.get('product')
        vendor = form.cleaned_data.get('vendor')
        transaction_type = form.cleaned_data.get('transaction_type')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        if product:
            logs = logs.filter(product=product)
        if vendor:
            logs = logs.filter(vendor=vendor)
        if transaction_type:
            logs = logs.filter(transaction_type=transaction_type)
        if date_from:
            logs = logs.filter(created_at__date__gte=date_from)
        if date_to:
            logs = logs.filter(created_at__date__lte=date_to)
    total_in_qty = logs.filter(
        transaction_type='IN').aggregate(t=Sum('quantity'))['t'] or 0
    total_out_qty = logs.filter(
        transaction_type='OUT').aggregate(t=Sum('quantity'))['t'] or 0
    all_products = Product.objects.all()
    total_purchase_value = sum(
        p.quantity * p.purchase_price for p in all_products)
    total_selling_value = sum(
        p.quantity * p.selling_price for p in all_products)
    potential_profit = total_selling_value - total_purchase_value
    category_stats = []
    for cat in Category.objects.all():
        cat_products = cat.products.all()
        cat_qty = sum(p.quantity for p in cat_products)
        cat_value = sum(p.quantity * p.purchase_price for p in cat_products)
        category_stats.append({
            'name': cat.name,
            'product_count': cat_products.count(),
            'total_qty': cat_qty,
            'total_value': cat_value,
        })
    paginator = Paginator(logs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'inventory/reports.html', {
        'form': form,
        'page_obj': page_obj,
        'total_in_qty': total_in_qty,
        'total_out_qty': total_out_qty,
        'total_purchase_value': total_purchase_value,
        'total_selling_value': total_selling_value,
        'potential_profit': potential_profit,
        'category_stats': category_stats,
        'page_title': 'Reports',
    })


@login_required
def stock_opening_report(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    category_filter = request.GET.get('category', '')
    products = Product.objects.select_related(
        'category').order_by('category__name', 'name')
    if category_filter:
        products = products.filter(category_id=category_filter)
    categories = Category.objects.all()
    total_opening = sum(p.opening_stock for p in products)
    return render(request, 'inventory/stock_opening_report.html', {
        'products': products,
        'categories': categories,
        'category_filter': category_filter,
        'total_opening': total_opening,
        'page_title': 'Opening Stock Report',
    })


@login_required
def stock_in_report(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    form = StockFilterForm(request.GET or None)
    logs = StockLog.objects.filter(
        transaction_type='IN'
    ).select_related(
        'product', 'product__category', 'vendor', 'created_by'
    ).order_by('-created_at')
    if form.is_valid():
        product = form.cleaned_data.get('product')
        vendor = form.cleaned_data.get('vendor')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        if product:
            logs = logs.filter(product=product)
        if vendor:
            logs = logs.filter(vendor=vendor)
        if date_from:
            logs = logs.filter(created_at__date__gte=date_from)
        if date_to:
            logs = logs.filter(created_at__date__lte=date_to)
    total_qty = logs.aggregate(t=Sum('quantity'))['t'] or 0
    total_value = sum(
        log.quantity * log.product.purchase_price for log in logs)
    paginator = Paginator(logs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'inventory/stock_in_report.html', {
        'form': form,
        'page_obj': page_obj,
        'total_qty': total_qty,
        'total_value': total_value,
        'page_title': 'Stock IN Report',
    })


@login_required
def stock_out_report(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    form = StockFilterForm(request.GET or None)
    logs = StockLog.objects.filter(
        transaction_type='OUT'
    ).select_related(
        'product', 'product__category', 'created_by'
    ).order_by('-created_at')
    if form.is_valid():
        product = form.cleaned_data.get('product')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        if product:
            logs = logs.filter(product=product)
        if date_from:
            logs = logs.filter(created_at__date__gte=date_from)
        if date_to:
            logs = logs.filter(created_at__date__lte=date_to)
    total_qty = logs.aggregate(t=Sum('quantity'))['t'] or 0
    total_value = sum(
        log.quantity * log.product.selling_price for log in logs)
    paginator = Paginator(logs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'inventory/stock_out_report.html', {
        'form': form,
        'page_obj': page_obj,
        'total_qty': total_qty,
        'total_value': total_value,
        'page_title': 'Stock OUT Report',
    })


@login_required
def vendor_report(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    vendor_id = request.GET.get('vendor', '')
    vendors = Vendor.objects.all()
    selected_vendor = None
    logs = StockLog.objects.none()
    total_amount = 0
    total_qty = 0
    if vendor_id:
        selected_vendor = get_object_or_404(Vendor, pk=vendor_id)
        logs = StockLog.objects.filter(
            vendor=selected_vendor, transaction_type='IN'
        ).select_related(
            'product', 'product__category', 'created_by'
        ).order_by('-created_at')
        total_qty = logs.aggregate(t=Sum('quantity'))['t'] or 0
        total_amount = sum(
            log.quantity * log.product.purchase_price for log in logs)
    return render(request, 'inventory/vendor_report.html', {
        'vendors': vendors,
        'selected_vendor': selected_vendor,
        'logs': logs,
        'total_amount': total_amount,
        'total_qty': total_qty,
        'vendor_id': vendor_id,
        'page_title': 'Vendor Report',
    })


# ── INVENTORY OVERVIEW ────────────────────────────────────────

@login_required
def inventory_overview(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    products = Product.objects.select_related(
        'category').order_by('category__name', 'name')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(category__name__icontains=query)
        )
    if category_filter:
        products = products.filter(category_id=category_filter)
    categories = Category.objects.all()
    total_products = products.count()
    total_stock = sum(p.quantity for p in products)
    total_value = sum(p.quantity * p.purchase_price for p in products)
    paginator = Paginator(products, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'inventory/inventory_overview.html', {
        'page_obj': page_obj,
        'products': products,
        'categories': categories,
        'query': query,
        'category_filter': category_filter,
        'total_products': total_products,
        'total_stock': total_stock,
        'total_value': total_value,
        'page_title': 'Inventory Overview',
    })


@login_required
def download_excel(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    products = Product.objects.select_related(
        'category').order_by('category__name', 'name')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(category__name__icontains=query))
    if category_filter:
        products = products.filter(category_id=category_filter)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="inventory.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['#', 'Product Name', 'Category', 'Price (৳)', 'Stock Quantity'])
    for i, product in enumerate(products, 1):
        writer.writerow([
            i, product.name, product.category.name,
            product.selling_price, product.quantity
        ])
    return response


@login_required
def download_pdf(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    products = Product.objects.select_related(
        'category').order_by('category__name', 'name')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(category__name__icontains=query))
    if category_filter:
        products = products.filter(category_id=category_filter)
    total_stock = sum(p.quantity for p in products)
    return render(request, 'inventory/inventory_pdf.html', {
        'products': products,
        'total_stock': total_stock,
        'page_title': 'Inventory Report',
    })


# ── ACTIVITY LOG ──────────────────────────────────────────────

@login_required
def activity_log(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    logs = ActivityLog.objects.select_related('user').order_by('-created_at')
    paginator = Paginator(logs, 30)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'inventory/activity_log.html', {
        'page_obj': page_obj,
        'page_title': 'Activity Log',
    })


# ── CAMPUS TRANSACTION REPORT ─────────────────────────────────

@login_required
def campus_transaction_report(request):
    if is_super_admin(request.user):
        campus_id = request.GET.get('campus', '')
        campuses = Campus.objects.all()
        logs = CampusStockLog.objects.select_related(
            'campus', 'product', 'product__category', 'created_by'
        ).order_by('-created_at')
        if campus_id:
            logs = logs.filter(campus_id=campus_id)
        type_filter = request.GET.get('type', '')
        if type_filter in ['IN', 'OUT']:
            logs = logs.filter(transaction_type=type_filter)
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        if date_from:
            logs = logs.filter(created_at__date__gte=date_from)
        if date_to:
            logs = logs.filter(created_at__date__lte=date_to)
        total_in = logs.filter(
            transaction_type='IN').aggregate(t=Sum('quantity'))['t'] or 0
        total_out = logs.filter(
            transaction_type='OUT').aggregate(t=Sum('quantity'))['t'] or 0
        paginator = Paginator(logs, 20)
        page_obj = paginator.get_page(request.GET.get('page'))
        return render(request, 'inventory/campus_transaction_report.html', {
            'page_obj': page_obj,
            'campuses': campuses,
            'campus_id': campus_id,
            'type_filter': type_filter,
            'date_from': date_from,
            'date_to': date_to,
            'total_in': total_in,
            'total_out': total_out,
            'page_title': 'Campus Transaction Report',
        })
    else:
        try:
            campus = request.user.campus
        except Exception:
            messages.error(request, '❌ No campus assigned!')
            return redirect('dashboard')
        logs = CampusStockLog.objects.filter(
            campus=campus
        ).select_related(
            'product', 'product__category', 'created_by'
        ).order_by('-created_at')
        type_filter = request.GET.get('type', '')
        if type_filter in ['IN', 'OUT']:
            logs = logs.filter(transaction_type=type_filter)
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        if date_from:
            logs = logs.filter(created_at__date__gte=date_from)
        if date_to:
            logs = logs.filter(created_at__date__lte=date_to)
        total_in = logs.filter(
            transaction_type='IN').aggregate(t=Sum('quantity'))['t'] or 0
        total_out = logs.filter(
            transaction_type='OUT').aggregate(t=Sum('quantity'))['t'] or 0
        paginator = Paginator(logs, 20)
        page_obj = paginator.get_page(request.GET.get('page'))
        return render(request, 'inventory/campus_transaction_report.html', {
            'page_obj': page_obj,
            'campus': campus,
            'type_filter': type_filter,
            'date_from': date_from,
            'date_to': date_to,
            'total_in': total_in,
            'total_out': total_out,
            'page_title': 'Transaction Report',
        })


# ── CAMPUS STOCK DASHBOARD ────────────────────────────────────

@login_required
def campus_stock_dashboard(request):
    if not is_super_admin(request.user):
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    search = request.GET.get('q', '')
    campuses = Campus.objects.all()
    products = Product.objects.select_related('category').order_by('name')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(category__name__icontains=search)
        )
    product_campus_data = []
    for product in products:
        campus_stocks = []
        for campus in campuses:
            try:
                inv = CampusInventory.objects.get(
                    campus=campus, product=product)
                qty = inv.quantity
            except CampusInventory.DoesNotExist:
                qty = 0
            campus_stocks.append({
                'campus': campus,
                'quantity': qty
            })
        total = sum(cs['quantity'] for cs in campus_stocks)
        product_campus_data.append({
            'product': product,
            'campus_stocks': campus_stocks,
            'total': total
        })
    return render(request, 'inventory/campus_stock_dashboard.html', {
        'campuses': campuses,
        'product_campus_data': product_campus_data,
        'search': search,
        'page_title': 'Campus Stock Dashboard',
    })
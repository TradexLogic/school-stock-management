from django.urls import path
from . import views

urlpatterns = [

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Campus (Super Admin Only)
    path('campuses/', views.campus_list, name='campus_list'),
    path('campuses/add/', views.campus_create, name='campus_create'),
    path('campuses/<int:pk>/', views.campus_detail, name='campus_detail'),
    path('campuses/<int:pk>/edit/', views.campus_edit, name='campus_edit'),

    # Campus Inventory Input (Campus Admin)
    path('my-inventory/', views.campus_inventory_input, name='campus_inventory_input'),
    path('my-inventory/out/', views.campus_stock_out, name='campus_stock_out'),

    # Categories (Super Admin Only)
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Vendors (Super Admin Only)
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/add/', views.vendor_create, name='vendor_create'),
    path('vendors/<int:pk>/', views.vendor_detail, name='vendor_detail'),
    path('vendors/<int:pk>/edit/', views.vendor_edit, name='vendor_edit'),
    path('vendors/<int:pk>/delete/', views.vendor_delete, name='vendor_delete'),

    # Products (Super Admin Only)
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Stock (Super Admin Only)
    path('stock/', views.stock_log_list, name='stock_log_list'),
    path('stock/in/', views.stock_in, name='stock_in'),
    path('stock/out/', views.stock_out, name='stock_out'),

    # Voucher
    path('voucher/<int:pk>/', views.voucher_detail, name='voucher_detail'),

    # Reports (Super Admin Only)
    path('reports/', views.reports, name='reports'),
    path('reports/opening/', views.stock_opening_report, name='stock_opening_report'),
    path('reports/stock-in/', views.stock_in_report, name='stock_in_report'),
    path('reports/stock-out/', views.stock_out_report, name='stock_out_report'),
    path('reports/vendor/', views.vendor_report, name='vendor_report'),

    # Inventory Overview (Super Admin Only)
    path('inventory/', views.inventory_overview, name='inventory_overview'),
    path('inventory/download/excel/', views.download_excel, name='download_excel'),
    path('inventory/download/pdf/', views.download_pdf, name='download_pdf'),

    # Activity Log (Super Admin Only)
    path('activity-log/', views.activity_log, name='activity_log'),
    # Campus Reports & Dashboard
    path('campus-transactions/', views.campus_transaction_report, name='campus_transaction_report'),
    path('campus-stock-dashboard/', views.campus_stock_dashboard, name='campus_stock_dashboard'),
]
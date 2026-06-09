from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

admin.site.site_header = "স্কুল স্টক ম্যানেজমেন্ট - Admin"
admin.site.site_title = "স্কুল স্টক"
admin.site.index_title = "Admin Panel"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('inventory.urls')),
]
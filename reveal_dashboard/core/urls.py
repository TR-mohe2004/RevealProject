# core/urls.py (النسخة الصحيحة بدون تكرار)

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # المصادقة
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # الصفحات الرئيسية
    path('', views.dashboard_view, name='dashboard'),
    path('orders/', views.orders_view, name='orders'),
    path('stock/', views.stock_view, name='stock'),
    path('reports/', views.reports_view, name='reports'),
    path('settings/', views.settings_view, name='settings'),

    # إدارة المنتجات
    path('products/', views.products_view, name='products'),
    path('products/add/', views.add_product_view, name='add_product'),
    path('products/edit/<str:product_id>/', views.edit_product_view, name='edit_product'),
    path('products/delete/<str:product_id>/', views.delete_product_view, name='delete_product'),

    # إدارة المستخدمين
    path('customers/', views.customers_view, name='customers'),
    path('customers/add/', views.add_user_view, name='add_user'),
    path('customers/delete/<str:user_id>/', views.delete_user_view, name='delete_user'),

    # ✨✨ إدارة المحافظ (قسم واحد فقط وكامل) ✨✨
    path('wallet/', views.wallet_recharge_view, name='wallet_recharge'),
    path('wallet/create/', views.create_wallet_view, name='create_wallet'),
    path('wallet/charge/', views.charge_wallet_view, name='charge_wallet'),
    path('wallet/refund/', views.refund_wallet_view, name='refund_wallet'),
]

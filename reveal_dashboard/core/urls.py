from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # الصفحة الرئيسية (لوحة التحكم)
    path('', views.dashboard_view, name='dashboard'),
    
    # باقي الصفحات
    path('orders/', views.orders_view, name='orders'),
    path('products/', views.products_view, name='products'),
    path('stock/', views.stock_view, name='stock'),
    path('customers/', views.customers_view, name='customers'),
    path('reports/', views.reports_view, name='reports'),
    path('settings/', views.settings_view, name='settings'),
    path('login/', views.login_view, name='login'),
    path('wallet/', views.wallet_recharge_view, name='wallet_recharge'),
    path('wallet/create/', views.create_wallet_view, name='create_wallet'),
    path('wallet/charge/', views.charge_wallet_action, name='charge_wallet_action'),
    path('wallet/edit/', views.edit_wallet_view, name='edit_wallet'),
    path('wallet/history/', views.wallet_history_view, name='wallet_history'),
    path('products/', views.products_view, name='products'), # الصفحة الرئيسية للمنتجات
    path('products/add/', views.add_product_view, name='add_product'),
    path('products/edit/<str:product_id>/', views.edit_product_view, name='edit_product'),
    path('products/delete/<str:product_id>/', views.delete_product_view, name='delete_product'),

]



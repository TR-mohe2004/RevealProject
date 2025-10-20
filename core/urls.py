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
    path('wallet/', views.wallet_recharge_view, name='wallet_recharge'),
    path('settings/', views.settings_view, name='settings'),
    path('login/', views.login_view, name='login'),
]


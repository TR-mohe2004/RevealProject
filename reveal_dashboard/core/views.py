from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# ملاحظة: سنقوم بتفعيل @login_required لاحقًا على كل الصفحات
# لحمايتها من الوصول غير المصرح به.

def dashboard_view(request):
    """عرض صفحة لوحة التحكم الرئيسية."""
    return render(request, 'core/dashboard.html')

def orders_view(request):
    """عرض صفحة إدارة الطلبات."""
    return render(request, 'core/orders.html')

def products_view(request):
    """عرض صفحة إدارة المنتجات."""
    return render(request, 'core/products.html')

def stock_view(request):
    """عرض صفحة إدارة المخزون."""
    return render(request, 'core/stock.html')

def customers_view(request):
    """عرض صفحة إدارة العملاء."""
    return render(request, 'core/customers.html')

def reports_view(request):
    """عرض صفحة التقارير."""
    return render(request, 'core/reports.html')

def wallet_recharge_view(request):
    """عرض صفحة شحن المحفظة."""
    # ملاحظة: هذه الصفحة قد يتم دمجها لاحقًا مع صفحة العملاء
    return render(request, 'core/wallet_recharge.html')

def settings_view(request):
    """عرض صفحة الإعدادات."""
    return render(request, 'core/settings.html')

def login_view(request):
    """عرض صفحة تسجيل الدخول."""
    return render(request, 'login.html')
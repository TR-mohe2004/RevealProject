# core/views.py (النسخة الكاملة والمستعادة)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from firebase_admin import auth as firebase_auth, firestore
import pyrebase
from datetime import datetime
from django.contrib.auth.models import User

# --- تهيئة Firebase ---
firebase = pyrebase.initialize_app(settings.PYREBASE_CONFIG)
auth = firebase.auth()
db = firestore.client()
storage = firebase.storage()

# --- الدوال المساعدة ---
def get_settings():
    """جلب إعدادات النظام من Firestore أو استخدام الافتراضيات."""
    try:
        settings_doc = db.collection('config').document('system_settings').get()
        if settings_doc.exists:
            return settings_doc.to_dict()
        else:
            default_settings = {
                'system_name': 'منظومة ريفيل',
                'welcome_message': 'مرحباً بك في لوحة التحكم',
                'min_charge_amount': 10.0,
                'currency_symbol': 'د.ل',
                'allow_registration': True,
            }
            # لا نحتاج لإعادة كتابة الإعدادات الافتراضية هنا، فقط نرجعها
            return default_settings
    except Exception:
        return {
            'system_name': 'منظومة ريفيل',
            'welcome_message': 'مرحباً بك في لوحة التحكم',
            'min_charge_amount': 10.0,
            'currency_symbol': 'د.ل',
            'allow_registration': True,
        }

# --- دوال المصادقة ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            django_user = authenticate(request, username=user['localId'], password=password)
            
            if django_user is None:
                django_user = User.objects.create_user(username=user['localId'], email=email, password=password)
            
            login(request, django_user)
            return redirect('core:dashboard')
            
        except Exception:
            error_message = "خطأ في تسجيل الدخول. تحقق من البريد الإلكتروني وكلمة المرور."
            messages.error(request, error_message)
            
    return render(request, 'core/login.html')

@login_required(login_url='core:login')
def logout_view(request):
    logout(request)
    messages.success(request, "تم تسجيل الخروج بنجاح.")
    return redirect('core:login')

# --- دوال الصفحات الرئيسية ---
@login_required(login_url='core:login')
def dashboard_view(request):
    context = {'settings': get_settings()}
    return render(request, 'core/dashboard.html', context)

@login_required(login_url='core:login')
def orders_view(request):
    orders_stream = db.collection('orders').order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
    
    new_orders = []
    preparing_orders = []
    ready_orders = []
    
    for order in orders_stream:
        data = order.to_dict()
        data['id'] = order.id
        
        status = data.get('status', 'new')
        
        if status == 'new':
            new_orders.append(data)
        elif status == 'preparing':
            preparing_orders.append(data)
        elif status == 'ready':
            ready_orders.append(data)
            
    context = {
        'settings': get_settings(),
        'new_orders': new_orders,
        'preparing_orders': preparing_orders,
        'ready_orders': ready_orders,
    }
    return render(request, 'core/orders.html', context)

@login_required(login_url='core:login')
def stock_view(request):
    # سيتم تحديث هذه الدالة لاحقاً لتوفير بيانات المخزون
    products_stream = db.collection('products').stream()
    products = [{'id': product.id, **product.to_dict()} for product in products_stream]
    context = {'settings': get_settings(), 'products': products}
    return render(request, 'core/stock.html', context)

@login_required(login_url='core:login')
def reports_view(request):
    settings = get_settings()
    product_count = db.collection('products').stream()
    wallet_count = db.collection('wallets').stream()
    
    total_system_balance = sum(wallet.to_dict().get('balance', 0.0) for wallet in wallet_count)
        
    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    transactions_today_query = db.collection('transactions').where('timestamp', '>=', start_of_day).order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
    
    total_deposits_today = 0.0
    total_refunds_today = 0.0
    deposits_count_today = 0
    latest_transactions = []
    
    for trans in transactions_today_query:
        data = trans.to_dict()
        data['id'] = trans.id
        latest_transactions.append(data)
        
        if data.get('type') == 'deposit':
            total_deposits_today += data.get('amount', 0.0)
            deposits_count_today += 1
        elif data.get('type') == 'refund':
            total_refunds_today += data.get('amount', 0.0)

    context = {
        'settings': settings,
        'product_count': len(list(product_count)),
        'wallet_count': len(list(db.collection('wallets').stream())),
        'total_system_balance': total_system_balance,
        'total_deposits_today': total_deposits_today,
        'total_refunds_today': total_refunds_today,
        'deposits_count_today': deposits_count_today,
        'latest_transactions': latest_transactions[:10],
    }
    return render(request, 'core/reports.html', context)

@login_required(login_url='core:login')
def settings_view(request):
    settings_ref = db.collection('config').document('system_settings')
    
    if request.method == 'POST':
        try:
            updated_settings = {
                'system_name': request.POST.get('system_name', 'منظومة ريفيل'),
                'welcome_message': request.POST.get('welcome_message', 'مرحباً بك'),
                'min_charge_amount': float(request.POST.get('min_charge_amount', 10.0)),
                'currency_symbol': request.POST.get('currency_symbol', 'د.ل'),
                'allow_registration': 'allow_registration' in request.POST,
            }
            settings_ref.set(updated_settings, merge=True)
            messages.success(request, "تم حفظ الإعدادات بنجاح.")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء حفظ الإعدادات: {e}")
        
        return redirect('core:settings')

    context = {'settings': get_settings()}
    return render(request, 'core/settings.html', context)

# --- دوال إدارة المنتجات (تمت استعادتها سابقاً) ---
@login_required(login_url='core:login')
def products_view(request):
    products_stream = db.collection('products').stream()
    products = []
    for product in products_stream:
        data = product.to_dict()
        data['id'] = product.id
        products.append(data)
    
    context = {'products': products, 'settings': get_settings()}
    return render(request, 'core/products.html', context)

@login_required(login_url='core:login')
def add_product_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = float(request.POST.get('price'))
        category = request.POST.get('category')
        is_available = 'is_available' in request.POST
        image_file = request.FILES.get('image')
        
        image_url = None
        if image_file:
            storage_path = f"products/{name}_{datetime.now().timestamp()}"
            storage.child(storage_path).put(image_file)
            image_url = storage.child(storage_path).get_url(None)
            
        product_data = {
            'name': name, 'price': price, 'category': category,
            'is_available': is_available, 'image_url': image_url,
            'created_at': datetime.now()
        }
        
        db.collection('products').add(product_data)
        messages.success(request, f"تم إضافة المنتج {name} بنجاح.")
        
    return redirect('core:products')

@login_required(login_url='core:login')
def edit_product_view(request, product_id):
    product_ref = db.collection('products').document(product_id)
    
    if request.method == 'POST':
        try:
            updated_data = {
                'name': request.POST.get('name'),
                'price': float(request.POST.get('price')),
                'category': request.POST.get('category'),
                'is_available': 'is_available' in request.POST,
            }
            
            image_file = request.FILES.get('image')
            if image_file:
                storage_path = f"products/{updated_data['name']}_{datetime.now().timestamp()}"
                storage.child(storage_path).put(image_file)
                updated_data['image_url'] = storage.child(storage_path).get_url(None)

            product_ref.update(updated_data)
            messages.success(request, "تم تحديث المنتج بنجاح.")
            return redirect('core:products')
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء تحديث المنتج: {e}")
            return redirect('core:edit_product', product_id=product_id)

    else:
        product_doc = product_ref.get()
        if not product_doc.exists:
            messages.error(request, "المنتج غير موجود.")
            return redirect('core:products')
        
        product_data = product_doc.to_dict()
        product_data['id'] = product_doc.id
        
        context = {
            'product': product_data,
            'settings': get_settings()
        }
        return render(request, 'core/edit_product.html', context)

@login_required(login_url='core:login')
def delete_product_view(request, product_id):
    try:
        db.collection('products').document(product_id).delete()
        messages.success(request, "تم حذف المنتج بنجاح.")
    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء حذف المنتج: {e}")
    return redirect('core:products')

# --- دوال إدارة المحافظ (تمت استعادتها) ---
@login_required(login_url='core:login')
def wallet_recharge_view(request):
    query = request.GET.get('q')
    wallets_ref = db.collection('wallets')
    wallets = []
    
    if query:
        wallet_by_id = wallets_ref.document(query).get()
        if wallet_by_id.exists:
            data = wallet_by_id.to_dict()
            data['id'] = wallet_by_id.id
            wallets.append(data)
        
        if not wallets:
            all_wallets = wallets_ref.stream()
            for wallet in all_wallets:
                data = wallet.to_dict()
                data['id'] = wallet.id
                if query.lower() in data.get('owner_name', '').lower():
                    wallets.append(data)
    else:
        wallets_stream = wallets_ref.stream()
        for wallet in wallets_stream:
            data = wallet.to_dict()
            data['id'] = wallet.id
            wallets.append(data)
            
    context = {'wallets': wallets, 'settings': get_settings()}
    return render(request, 'core/wallet_recharge.html', context)

@login_required(login_url='core:login')
def create_wallet_view(request):
    if request.method == 'POST':
        owner_name = request.POST.get('owner_name')
        user_type = request.POST.get('user_type')
        
        wallet_data = {
            'owner_name': owner_name, 'user_type': user_type,
            'balance': 0.0, 'created_at': datetime.now()
        }
        
        db.collection('wallets').add(wallet_data)
        messages.success(request, f"تم إنشاء محفظة جديدة باسم {owner_name} بنجاح.")
        
    return redirect('core:wallet_recharge')

@login_required(login_url='core:login')
def charge_wallet_view(request):
    if request.method == 'POST':
        wallet_code = request.POST.get('wallet_code')
        amount = float(request.POST.get('amount'))
        
        wallet_ref = db.collection('wallets').document(wallet_code)
        wallet_doc = wallet_ref.get()
        
        if wallet_doc.exists:
            wallet_data = wallet_doc.to_dict()
            new_balance = wallet_data.get('balance', 0.0) + amount
            wallet_ref.update({'balance': new_balance})
            
            db.collection('transactions').add({
                'wallet_id': wallet_code, 'wallet_owner': wallet_data.get('owner_name'),
                'type': 'deposit', 'amount': amount, 'new_balance': new_balance,
                'timestamp': datetime.now()
            })
            
            messages.success(request, f"تم شحن محفظة {wallet_data.get('owner_name')} بمبلغ {amount} د.ل. الرصيد الجديد: {new_balance} د.ل")
        else:
            messages.error(request, "المحفظة غير موجودة.")
            
    return redirect('core:wallet_recharge')

@login_required(login_url='core:login')
def refund_wallet_view(request):
    if request.method == 'POST':
        wallet_code = request.POST.get('wallet_code')
        amount = float(request.POST.get('amount'))
        
        wallet_ref = db.collection('wallets').document(wallet_code)
        wallet_doc = wallet_ref.get()
        
        if wallet_doc.exists:
            wallet_data = wallet_doc.to_dict()
            new_balance = wallet_data.get('balance', 0.0) - amount
            wallet_ref.update({'balance': new_balance})
            
            db.collection('transactions').add({
                'wallet_id': wallet_code, 'wallet_owner': wallet_data.get('owner_name'),
                'type': 'refund', 'amount': amount, 'new_balance': new_balance,
                'timestamp': datetime.now()
            })
            
            messages.success(request, f"تم استرجاع مبلغ {amount} د.ل من محفظة {wallet_data.get('owner_name')}. الرصيد الجديد: {new_balance} د.ل")
        else:
            messages.error(request, "المحفظة غير موجودة.")
            
    return redirect('core:wallet_recharge')

# --- دوال إدارة الطلبات ---

@login_required(login_url='core:login')
def change_order_status(request, order_id, new_status):
    if request.method == 'GET':
        order_ref = db.collection('orders').document(order_id)
        order_doc = order_ref.get()
        
        if order_doc.exists:
            try:
                order_ref.update({'status': new_status, 'updated_at': datetime.now()})
                
                status_messages = {
                    'preparing': 'تم قبول الطلب بنجاح وتحويله إلى "قيد التجهيز".',
                    'ready': 'تم تجهيز الطلب بنجاح وتحويله إلى "جاهز للاستلام".',
                    'completed': 'تم إتمام الطلب وأرشفته بنجاح.'
                }
                messages.success(request, status_messages.get(new_status, 'تم تحديث حالة الطلب بنجاح.'))
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء تحديث حالة الطلب: {e}")
        else:
            messages.error(request, "الطلب غير موجود.")
            
    return redirect('core:orders')

@login_required(login_url='core:login')
def accept_order(request, order_id):
    return change_order_status(request, order_id, 'preparing')

@login_required(login_url='core:login')
def ready_order(request, order_id):
    return change_order_status(request, order_id, 'ready')

@login_required(login_url='core:login')
def complete_order(request, order_id):
    return change_order_status(request, order_id, 'completed')

# --- دوال إدارة العملاء (تمت استعادتها) ---
@login_required(login_url='core:login')
def customers_view(request):
    users = []
    try:
        for user in firebase_auth.list_users().users:
            user_doc = db.collection('users').document(user.uid).get()
            user_data = user_doc.to_dict() if user_doc.exists else {}
            
            users.append({
                'uid': user.uid, 'email': user.email,
                'role': user_data.get('role', 'غير محدد'),
                'created_at': user.creation_timestamp
            })
    except Exception as e:
        messages.error(request, f"خطأ في جلب المستخدمين: {e}")
        
    context = {'users': users, 'settings': get_settings()}
    return render(request, 'core/customers.html', context)

@login_required(login_url='core:login')
def add_user_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        try:
            user = firebase_auth.create_user(email=email, password=password)
            db.collection('users').document(user.uid).set({
                'email': email, 'role': role, 'created_at': datetime.now()
            })
            messages.success(request, f"تم إنشاء المستخدم {email} بنجاح ({role}).")
        except Exception as e:
            messages.error(request, f"خطأ في إضافة المستخدم: {e}")
            
    return redirect('core:customers')

@login_required(login_url='core:login')
def delete_user_view(request, user_id):
    try:
        firebase_auth.delete_user(user_id)
        db.collection('users').document(user_id).delete()
        messages.success(request, "تم حذف المستخدم بنجاح.")
    except Exception as e:
        messages.error(request, f"خطأ في حذف المستخدم: {e}")
        
    return redirect('core:customers')

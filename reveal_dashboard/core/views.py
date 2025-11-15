# core/views.py (النسخة النهائية الكاملة والحقيقية)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from google.cloud import firestore
from firebase_admin import storage, auth
import random
from datetime import datetime
import uuid
import pyrebase

from django.conf import settings
db = settings.FIRESTORE_DB

try:
    if hasattr(settings, 'PYREBASE_CONFIG') and not firebase_admin._apps:
        firebase_pyrebase = pyrebase.initialize_app(settings.PYREBASE_CONFIG)
        auth_pyrebase = firebase_pyrebase.auth()
    elif firebase_admin._apps:
        # إذا كان التطبيق مهيأ بالفعل، احصل على نسخة pyrebase
        firebase_pyrebase = pyrebase.initialize_app(settings.PYREBASE_CONFIG)
        auth_pyrebase = firebase_pyrebase.auth()
    else:
        auth_pyrebase = None
except Exception:
    # هذا يمنع الانهيار إذا تم إعادة تحميل الخادم
    if 'firebase_pyrebase' not in locals() and hasattr(settings, 'PYREBASE_CONFIG'):
        firebase_pyrebase = pyrebase.initialize_app(settings.PYREBASE_CONFIG)
        auth_pyrebase = firebase_pyrebase.auth()
    else:
        auth_pyrebase = None


# ==========================================================
# == المصادقة وتسجيل الدخول/الخروج
# ==========================================================
def login_view(request):
    if request.user.is_authenticated: return redirect('core:dashboard')
    if request.method == 'POST':
        email, password = request.POST.get('email'), request.POST.get('password')
        try:
            user_auth = auth_pyrebase.sign_in_with_email_and_password(email, password)
            user, created = User.objects.get_or_create(username=email)
            if created: user.set_unusable_password(); user.save()
            login(request, user)
            return redirect('core:dashboard')
        except Exception:
            messages.error(request, "فشل تسجيل الدخول. تأكد من البريد الإلكتروني وكلمة المرور.")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "تم تسجيل الخروج بنجاح.")
    return redirect('core:login')


# ==========================================================
# == الصفحات الأساسية
# ==========================================================
@login_required(login_url='core:login')
def dashboard_view(request): return render(request, 'core/dashboard.html')

@login_required(login_url='core:login')
def orders_view(request): return render(request, 'core/orders.html')

@login_required(login_url='core:login')
def stock_view(request): return render(request, 'core/stock.html')


# ==========================================================
# == إدارة المنتجات
# ==========================================================
@login_required(login_url='core:login')
def products_view(request):
    context = {}
    try:
        products_ref = db.collection('products').order_by('name')
        products_docs = products_ref.stream()
        context['products'] = [{'id': doc.id, **doc.to_dict()} for doc in products_docs]
    except Exception as e:
        messages.error(request, f"حدث خطأ: {e}")
        context['products'] = []
    return render(request, 'core/products.html', context)

@login_required(login_url='core:login')
def add_product_view(request):
    if request.method == 'POST':
        try:
            product_data = {
                'name': request.POST.get('name'), 'price': float(request.POST.get('price')),
                'category': request.POST.get('category', 'عام'), 'is_available': 'is_available' in request.POST,
                'created_at': datetime.utcnow(), 'image_url': ''
            }
            image_file = request.FILES.get('image')
            if image_file:
                file_name = f"products/{uuid.uuid4()}_{image_file.name}"
                bucket = storage.bucket()
                blob = bucket.blob(file_name)
                blob.upload_from_file(image_file, content_type=image_file.content_type)
                blob.make_public()
                product_data['image_url'] = blob.public_url
            db.collection('products').add(product_data)
            messages.success(request, "تمت إضافة المنتج بنجاح.")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء إضافة المنتج: {e}")
    return redirect('core:products')

@login_required(login_url='core:login')
def edit_product_view(request, product_id):
    # (منطق التعديل الكامل سيضاف هنا لاحقاً)
    messages.info(request, "ميزة تعديل المنتج قيد التطوير.")
    return redirect('core:products')

@login_required(login_url='core:login')
def delete_product_view(request, product_id):
    try:
        db.collection('products').document(product_id).delete()
        messages.success(request, "تم حذف المنتج بنجاح.")
    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء حذف المنتج: {e}")
    return redirect('core:products')


# ==========================================================
# == إدارة المستخدمين (العملاء)
# ==========================================================
@login_required(login_url='core:login')
def customers_view(request):
    context = {}
    try:
        users_docs = db.collection('users').stream()
        context['users'] = [{'uid': doc.id, **doc.to_dict()} for doc in users_docs]
    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء جلب المستخدمين: {e}")
        context['users'] = []
    return render(request, 'core/customers.html', context)

@login_required(login_url='core:login')
def add_user_view(request):
    if request.method == 'POST':
        email, password, role = request.POST.get('email'), request.POST.get('password'), request.POST.get('role', 'cashier')
        try:
            user_record = auth.create_user(email=email, password=password)
            user_data = {'email': email, 'role': role, 'created_at': datetime.utcnow()}
            db.collection('users').document(user_record.uid).set(user_data)
            messages.success(request, "تم إنشاء المستخدم بنجاح.")
        except Exception as e:
            messages.error(request, f"فشل إنشاء المستخدم: {e}")
    return redirect('core:customers')

@login_required(login_url='core:login')
def delete_user_view(request, user_id):
    try:
        # لا تسمح للمستخدم بحذف نفسه
        if auth.get_user_by_email(request.user.username).uid == user_id:
            messages.error(request, "لا يمكنك حذف حسابك الخاص.")
            return redirect('core:customers')
        auth.delete_user(user_id)
        db.collection('users').document(user_id).delete()
        messages.success(request, "تم حذف المستخدم بنجاح.")
    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء حذف المستخدم: {e}")
    return redirect('core:customers')


# ==========================================================
# == إدارة المحافظ
# ==========================================================
def generate_unique_code():
    while True:
        code = str(random.randint(1000, 9999))
        if not db.collection('wallets').document(code).get().exists: return code

@login_required(login_url='core:login')
def wallet_recharge_view(request):
    context = {}
    wallets_ref = db.collection('wallets')
    search_query = request.GET.get('q', '').strip()
    if search_query:
        wallets_by_name = wallets_ref.where('owner_name', '>=', search_query).where('owner_name', '<=', search_query + '\uf8ff').stream()
        all_wallets = [{'id': doc.id, **doc.to_dict()} for doc in wallets_by_name]
        if search_query.isdigit():
            wallet_by_code = wallets_ref.document(search_query).get()
            if wallet_by_code.exists and not any(w['id'] == wallet_by_code.id for w in all_wallets):
                all_wallets.append({'id': wallet_by_code.id, **wallet_by_code.to_dict()})
    else:
        all_docs = wallets_ref.order_by('owner_name').stream()
        all_wallets = [{'id': doc.id, **doc.to_dict()} for doc in all_docs]
    context['wallets'] = all_wallets
    context['search_query'] = search_query
    return render(request, 'core/wallet_recharge.html', context)

@login_required(login_url='core:login')
def create_wallet_view(request):
    if request.method == 'POST':
        owner_name, user_type = request.POST.get('owner_name'), request.POST.get('user_type')
        new_code = generate_unique_code()
        wallet_data = {'owner_name': owner_name, 'user_type': user_type, 'balance': 0.0, 'created_at': datetime.utcnow()}
        db.collection('wallets').document(new_code).set(wallet_data)
        messages.success(request, f"تم إنشاء محفظة لـ {owner_name} بالكود: {new_code}")
    return redirect('core:wallet_recharge')

@login_required(login_url='core:login')
def charge_wallet_view(request):
    wallet_code = request.POST.get('wallet_code')
    redirect_url = f"/wallet/?q={wallet_code}" if wallet_code else 'core:wallet_recharge'
    if request.method == 'POST':
        try:
            settings_doc = db.collection('config').document('system_settings').get()
            min_charge_limit = settings_doc.to_dict().get('min_charge_limit', 10.0) if settings_doc.exists else 10.0
            amount = float(request.POST.get('amount', 0))
            if amount < min_charge_limit:
                messages.error(request, f"خطأ: أقل مبلغ للشحن هو {min_charge_limit} د.ل.")
                return redirect(redirect_url)
            wallet_ref = db.collection('wallets').document(wallet_code)
            @firestore.transactional
            def update_in_transaction(transaction, wallet_ref, amount):
                snapshot = wallet_ref.get(transaction=transaction)
                if not snapshot.exists: raise ValueError("المحفظة غير موجودة!")
                new_balance = snapshot.to_dict().get('balance', 0) + amount
                transaction.update(wallet_ref, {'balance': new_balance})
                log_ref = wallet_ref.collection('transaction_history').document()
                log_data = {'type': 'deposit', 'amount': amount, 'new_balance': new_balance, 'timestamp': datetime.utcnow(), 'description': f"إيداع من قبل {request.user.username}"}
                transaction.set(log_ref, log_data)
                return new_balance
            transaction = db.transaction()
            final_balance = update_in_transaction(transaction, wallet_ref, amount)
            messages.success(request, f"تم شحن المحفظة بنجاح. الرصيد الجديد: {final_balance:.2f} د.ل.")
        except ValueError as ve: messages.error(request, str(ve))
        except Exception as e: messages.error(request, f"حدث خطأ: {e}")
    return redirect(redirect_url)

@login_required(login_url='core:login')
def refund_wallet_view(request):
    wallet_code = request.POST.get('wallet_code')
    redirect_url = f"/wallet/?q={wallet_code}" if wallet_code else 'core:wallet_recharge'
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount', 0))
            if amount <= 0:
                messages.error(request, "مبلغ الاسترجاع يجب أن يكون أكبر من صفر.")
                return redirect(redirect_url)
            wallet_ref = db.collection('wallets').document(wallet_code)
            @firestore.transactional
            def update_in_transaction(transaction, wallet_ref, amount):
                snapshot = wallet_ref.get(transaction=transaction)
                if not snapshot.exists: raise ValueError("المحفظة غير موجودة!")
                current_balance = snapshot.to_dict().get('balance', 0)
                if amount > current_balance: raise ValueError(f"الرصيد غير كافٍ. الرصيد الحالي: {current_balance:.2f} د.ل.")
                new_balance = current_balance - amount
                transaction.update(wallet_ref, {'balance': new_balance})
                log_ref = wallet_ref.collection('transaction_history').document()
                log_data = {'type': 'refund', 'amount': amount, 'new_balance': new_balance, 'timestamp': datetime.utcnow(), 'description': f"استرجاع من قبل {request.user.username}"}
                transaction.set(log_ref, log_data)
                return new_balance
            transaction = db.transaction()
            final_balance = update_in_transaction(transaction, wallet_ref, amount)
            messages.success(request, f"تم استرجاع {amount:.2f} د.ل بنجاح. الرصيد الجديد: {final_balance:.2f} د.ل.")
        except ValueError as ve: messages.error(request, str(ve))
        except Exception as e: messages.error(request, f"حدث خطأ: {e}")
    return redirect(redirect_url)


# ==========================================================
# == التقارير والإعدادات
# ==========================================================
@login_required(login_url='core:login')
def reports_view(request):
    context = {}
    try:
        product_count = db.collection('products').count().get()[0][0].value
        wallets_ref = db.collection('wallets')
        all_wallets_docs = list(wallets_ref.stream())
        wallet_count = len(all_wallets_docs)
        total_system_balance = sum(doc.to_dict().get('balance', 0) for doc in all_wallets_docs)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        total_deposits_today, deposits_count_today, total_refunds_today = 0, 0, 0
        latest_transactions = []
        for wallet_doc in all_wallets_docs:
            history_ref = wallet_doc.reference.collection('transaction_history').where('timestamp', '>=', today_start)
            for trans_doc in history_ref.stream():
                transaction = trans_doc.to_dict()
                transaction['wallet_owner'] = wallet_doc.to_dict().get('owner_name', 'غير معروف')
                latest_transactions.append(transaction)
                if transaction.get('type') == 'deposit':
                    total_deposits_today += transaction.get('amount', 0)
                    deposits_count_today += 1
                elif transaction.get('type') == 'refund':
                    total_refunds_today += transaction.get('amount', 0)
        latest_transactions.sort(key=lambda x: x['timestamp'], reverse=True)
        context = {
            'product_count': product_count, 'wallet_count': wallet_count, 'total_system_balance': total_system_balance,
            'total_deposits_today': total_deposits_today, 'deposits_count_today': deposits_count_today,
            'total_refunds_today': total_refunds_today, 'latest_transactions': latest_transactions[:10]
        }
    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء إنشاء التقرير: {e}")
        context = {
            'product_count': 0, 'wallet_count': 0, 'total_system_balance': 0, 'total_deposits_today': 0,
            'deposits_count_today': 0, 'total_refunds_today': 0, 'latest_transactions': []
        }
    return render(request, 'core/reports.html', context)

@login_required(login_url='core:login')
def settings_view(request):
    settings_doc_ref = db.collection('config').document('system_settings')
    if request.method == 'POST':
        try:
            updated_settings = {
                'system_name': request.POST.get('system_name', 'منظومة ريفيل'),
                'welcome_message': request.POST.get('welcome_message', 'مرحباً بك.'),
                'min_charge_limit': float(request.POST.get('min_charge_limit', 10.0))
            }
            settings_doc_ref.set(updated_settings, merge=True)
            messages.success(request, "تم حفظ الإعدادات بنجاح.")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء حفظ الإعدادات: {e}")
        return redirect('core:settings')
    try:
        settings_doc = settings_doc_ref.get()
        current_settings = settings_doc.to_dict() if settings_doc.exists else {
            'system_name': 'منظومة ريفيل', 'welcome_message': 'مرحباً بك في لوحة التحكم.', 'min_charge_limit': 10.0
        }
    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء قراءة الإعدادات: {e}")
        current_settings = {}
    context = {'settings': current_settings}
    return render(request, 'core/settings.html', context)

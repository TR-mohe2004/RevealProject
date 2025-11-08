from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import random
from datetime import datetime
import uuid # لاستيراد مكتبة توليد الأسماء الفريدة للصور

# --- تهيئة Firebase ---
from django.conf import settings
from firebase_admin import firestore, storage # استيراد storage للتعامل مع الصور

db = settings.FIRESTORE_DB

# ==========================================================
# == الدوال الأساسية للوحة التحكم
# ==========================================================

# @login_required
def dashboard_view(request):
    """
    عرض لوحة التحكم الرئيسية مع إحصائيات حقيقية من Firestore.
    """
    try:
        # 1. إحصاء عدد المنتجات
        products_ref = db.collection('products')
        product_count_agg = products_ref.count()
        product_count = product_count_agg.get()[0][0].value

        # 2. إحصاء عدد المحافظ (العملاء)
        wallets_ref = db.collection('wallets')
        wallets_count_agg = wallets_ref.count()
        wallets_count = wallets_count_agg.get()[0][0].value

        # 3. جلب آخر 5 منتجات مضافة
        latest_products_query = products_ref.order_by('created_at', direction=firestore.Query.DESCENDING).limit(5)
        latest_products_docs = latest_products_query.stream()
        latest_products = [{'id': doc.id, **doc.to_dict()} for doc in latest_products_docs]

        # 4. إحصائيات الطلبات (سيتم تفعيلها عند بناء قسم الطلبات)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        orders_ref = db.collection('orders')
        
        new_orders_query = orders_ref.where('created_at', '>=', today_start)
        new_orders_count_agg = new_orders_query.count()
        new_orders_count = new_orders_count_agg.get()[0][0].value

        total_sales_today = 0
        new_orders_docs = new_orders_query.stream()
        for order in new_orders_docs:
            total_sales_today += order.to_dict().get('total_price', 0)

    except Exception as e:
        product_count = 0
        try:
            wallets_count = db.collection('wallets').count().get()[0][0].value
        except:
            wallets_count = 0
        new_orders_count = 0
        total_sales_today = 0.0
        latest_products = []

    context = {
        'product_count': product_count,
        'wallets_count': wallets_count,
        'new_orders_count': new_orders_count,
        'total_sales_today': total_sales_today,
        'latest_products': latest_products,
    }
    return render(request, 'core/dashboard.html', context)

# @login_required
def orders_view(request):
    return render(request, 'core/orders.html')

# @login_required
def stock_view(request):
    return render(request, 'core/stock.html')

# @login_required
def customers_view(request):
    return render(request, 'core/customers.html')

# @login_required
def reports_view(request):
    return render(request, 'core/reports.html')

# @login_required
def settings_view(request):
    return render(request, 'core/settings.html')

def login_view(request):
    return render(request, 'login.html')

# ==========================================================
# == دوال إدارة المنتجات (مع ميزة رفع الصور)
# ==========================================================

# @login_required
def products_view(request):
    context = {}
    try:
        products_ref = db.collection('products').order_by('name')
        products_docs = products_ref.stream()
        context['products'] = [{'id': doc.id, **doc.to_dict()} for doc in products_docs]

        product_id_to_edit = request.GET.get('edit')
        if product_id_to_edit:
            product_doc = db.collection('products').document(product_id_to_edit).get()
            if product_doc.exists:
                context['product_to_edit'] = {'id': product_doc.id, **product_doc.to_dict()}

    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء جلب المنتجات: {e}")
        context['products'] = []

    return render(request, 'core/products.html', context)

# @login_required
def add_product_view(request):
    if request.method == 'POST':
        try:
            product_data = {
                'name': request.POST.get('name'),
                'price': float(request.POST.get('price')),
                'description': request.POST.get('description', ''),
                'is_available': 'is_available' in request.POST,
                'created_at': datetime.utcnow(),
                'image_url': ''
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
            messages.success(request, f"تمت إضافة المنتج '{product_data['name']}' بنجاح.")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء إضافة المنتج: {e}")
    return redirect('core:products')

# @login_required
def edit_product_view(request, product_id):
    if request.method == 'POST':
        try:
            product_ref = db.collection('products').document(product_id)
            update_data = {
                'name': request.POST.get('name'),
                'price': float(request.POST.get('price')),
                'description': request.POST.get('description', ''),
                'is_available': 'is_available' in request.POST,
            }

            image_file = request.FILES.get('image')
            if image_file:
                file_name = f"products/{uuid.uuid4()}_{image_file.name}"
                bucket = storage.bucket()
                blob = bucket.blob(file_name)
                blob.upload_from_file(image_file, content_type=image_file.content_type)
                blob.make_public()
                update_data['image_url'] = blob.public_url
            
            product_ref.update(update_data)
            messages.success(request, "تم تحديث المنتج بنجاح.")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء تحديث المنتج: {e}")
    return redirect('core:products')

# @login_required
def delete_product_view(request, product_id):
    try:
        db.collection('products').document(product_id).delete()
        messages.success(request, "تم حذف المنتج بنجاح.")
    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء حذف المنتج: {e}")
    return redirect('core:products')

# ==========================================================
# == دوال المحفظة (متوافقة مع FIREBASE)
# ==========================================================

def generate_unique_firestore_code():
    wallets_ref = db.collection('wallets')
    while True:
        code = str(random.randint(1000, 9999))
        if not wallets_ref.document(code).get().exists:
            return code

# @login_required
def wallet_recharge_view(request):
    context = {}
    wallet_code = request.GET.get('code')
    if wallet_code:
        wallet_ref = db.collection('wallets').document(wallet_code)
        wallet_doc = wallet_ref.get()
        
        if wallet_doc.exists:
            wallet_data = wallet_doc.to_dict()
            wallet_data['code'] = wallet_doc.id
            context['wallet'] = wallet_data
        else:
            messages.warning(request, f"لم يتم العثور على محفظة بالكود '{wallet_code}'.")
    
    return render(request, 'core/wallet_recharge.html', context)

# @login_required
def create_wallet_view(request):
    if request.method == 'POST':
        owner_name = request.POST.get('owner_name')
        user_type = request.POST.get('user_type')

        if owner_name and user_type:
            new_code = generate_unique_firestore_code()
            wallet_data = {
                'owner_name': owner_name,
                'user_type': user_type,
                'balance': 0.00,
                'created_at': datetime.utcnow()
            }
            db.collection('wallets').document(new_code).set(wallet_data)
            messages.success(request, f"تم إنشاء محفظة لـ '{owner_name}' بنجاح. الكود الخاص به هو: {new_code}")
    return redirect('core:wallet_recharge')

# @login_required
def charge_wallet_action(request):
    wallet_code = None
    if request.method == 'POST':
        wallet_code = request.POST.get('wallet_code')
        amount_str = request.POST.get('amount')

        if not (wallet_code and amount_str):
            messages.error(request, "بيانات غير مكتملة.")
            return redirect('core:wallet_recharge')

        try:
            amount = float(amount_str)
            if amount <= 0:
                messages.error(request, "مبلغ الشحن يجب أن يكون أكبر من صفر.")
                return redirect(f"/wallet/?code={wallet_code}")

            wallet_ref = db.collection('wallets').document(wallet_code)
            
            @firestore.transactional
            def update_in_transaction(transaction, wallet_ref, amount):
                wallet_doc = wallet_ref.get(transaction=transaction)
                if not wallet_doc.exists:
                    raise Exception("المحفظة غير موجودة.")

                current_balance = wallet_doc.to_dict().get('balance', 0)
                new_balance = current_balance + amount
                
                transaction.update(wallet_ref, {'balance': new_balance})
                
                log_ref = wallet_ref.collection('transaction_history').document()
                log_data = {
                    'type': 'deposit', 'amount': amount, 'new_balance': new_balance,
                    'timestamp': datetime.utcnow(), 'description': 'إيداع رصيد من قبل مسؤول النظام'
                }
                transaction.set(log_ref, log_data)
                return new_balance

            transaction = db.transaction()
            final_balance = update_in_transaction(transaction, wallet_ref, amount)
            messages.success(request, f"تم شحن المحفظة بنجاح. الرصيد الجديد: {final_balance:.2f} د.ل")

        except Exception as e:
            messages.error(request, f"حدث خطأ: {e}")

    return redirect(f"/wallet/?code={wallet_code}" if wallet_code else 'core:wallet_recharge')

# @login_required
def edit_wallet_view(request):
    wallet_code = None
    if request.method == 'POST':
        wallet_code = request.POST.get('wallet_code')
        new_owner_name = request.POST.get('owner_name')
        new_user_type = request.POST.get('user_type')

        if not (wallet_code and new_owner_name and new_user_type):
            messages.error(request, "بيانات التعديل غير مكتملة.")
            return redirect('core:wallet_recharge')

        try:
            wallet_ref = db.collection('wallets').document(wallet_code)
            update_data = {'owner_name': new_owner_name, 'user_type': new_user_type}
            wallet_ref.update(update_data)
            messages.success(request, f"تم تحديث بيانات المحفظة '{new_owner_name}' بنجاح.")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء التحديث: {e}")

    return redirect(f"/wallet/?code={wallet_code}" if wallet_code else 'core:wallet_recharge')

# @login_required
def wallet_history_view(request, wallet_code):
    context = {}
    try:
        wallet_ref = db.collection('wallets').document(wallet_code)
        wallet_doc = wallet_ref.get()

        if wallet_doc.exists:
            wallet_data = wallet_doc.to_dict()
            wallet_data['code'] = wallet_doc.id
            context['wallet'] = wallet_data

            history_ref = wallet_ref.collection('transaction_history').order_by('timestamp', direction=firestore.Query.DESCENDING)
            history_docs = history_ref.stream()
            context['history'] = [doc.to_dict() for doc in history_docs]
        else:
            messages.error(request, "المحفظة المطلوبة غير موجودة.")
            return redirect('core:wallet_recharge')
    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء جلب السجل: {e}")
        return redirect('core:wallet_recharge')

    return render(request, 'core/wallet_history.html', context)

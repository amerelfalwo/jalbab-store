from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, HeroImage, Category, Order, OrderItem, ContactMessage

from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .cart import Cart
from django.db import transaction
from django.db.models import F
from .forms import CheckoutForm, ContactForm

def home(request):
    hero = HeroImage.get_active()

    latest_products = (
        Product.objects
        .filter(is_active=True)
        .select_related('category')
        .order_by('-created_at')[:8]
    )
    discounted_products = (
        Product.objects
        .filter(is_active=True, is_discounted=True)
        .select_related('category')
        .order_by('-updated_at')[:8]
    )

    categories = Category.objects.all()

    context = {
        'hero': hero,
        'latest_products': latest_products,
        'discounted_products': discounted_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)

def product_list(request, category_slug=None):
    """
    صفحة المنتجات:
    - تعرض كل المنتجات المُفعّلة.
    - تفلتر حسب التصنيف إن وُجد category_slug.
    - تدعم الترتيب عبر ?sort=
    """
    categories = Category.objects.all()
    current_category = None
    # جلب المنتجات الأساسية
    products = (
        Product.objects
        .filter(is_active=True)
        .select_related('category')
    )
        # الفلترة حسب التصنيف
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    # الترتيب
    sort = request.GET.get('sort', 'newest')
    sort_options = {
        'newest':     '-created_at',
        'price_asc':  'price',
        'price_desc': '-price',
        'name':       'name',
    }
    products = products.order_by(sort_options.get(sort, '-created_at'))

    context = {
        'products': products,
        'categories': categories,
        'current_category': current_category,
        'current_sort': sort,
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, slug):
    """صفحة تفاصيل منتج واحد."""
    product = get_object_or_404(
        Product.objects.select_related('category'),
        slug=slug,
        is_active=True,
    )

    # منتجات مشابهة من نفس التصنيف (باستثناء المنتج الحالي)
    related_products = (
        Product.objects
        .filter(is_active=True, category=product.category)
        .exclude(pk=product.pk)
        .select_related('category')
        .order_by('-created_at')[:4]
    )

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


# ==========================================
# السلة (Cart)
# ==========================================

def cart_detail(request):
    """صفحة عرض السلة."""
    cart = Cart(request)
    return render(request, 'store/cart.html', {
        'cart': cart,
        'cart_items': list(cart),
        'cart_total': cart.get_total_price(),
    })


@require_POST
def cart_add(request, product_id):
    """إضافة منتج إلى السلة."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if not product.is_in_stock:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(
                {'success': False, 'message': 'المنتج غير متوفر حاليًا.'},
                status=400,
            )
        messages.error(request, 'المنتج غير متوفر حاليًا.')
        return redirect('store:product_detail', slug=product.slug)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    added_qty = cart.add(product, quantity)

    # رد AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'تمت إضافة "{product.name}" إلى السلة.',
            'cart_count': len(cart),
            'cart_total': str(cart.get_total_price()),
        })

    # رد عادي
    messages.success(request, f'تمت إضافة "{product.name}" إلى السلة.')
    return redirect('store:cart_detail')


@require_POST
def cart_update(request, product_id):
    """تحديث كمية منتج في السلة."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    new_qty = cart.update(product, quantity)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'quantity': new_qty,
            'subtotal': str(product.price * new_qty) if new_qty > 0 else '0',
            'cart_count': len(cart),
            'cart_total': str(cart.get_total_price()),
        })

    if new_qty == 0:
        messages.info(request, f'تم حذف "{product.name}" من السلة.')
    else:
        messages.success(request, 'تم تحديث الكمية.')
    return redirect('store:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """حذف منتج من السلة."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'cart_total': str(cart.get_total_price()),
        })

    messages.success(request, f'تم حذف "{product.name}" من السلة.')
    return redirect('store:cart_detail')

# ==========================================
# إتمام الطلب (Checkout)
# ==========================================

def checkout(request):
    """صفحة إتمام الطلب وحفظه."""
    cart = Cart(request)

    # إذا كانت السلة فارغة → إعادة توجيه لصفحة السلة
    if cart.is_empty():
        messages.warning(request, 'سلتك فارغة. يُرجى إضافة منتجات أولًا.')
        return redirect('store:cart_detail')

    cart_items = list(cart)

    # التحقق من المخزون قبل عرض الصفحة
    stock_issues = []
    for item in cart_items:
        if item['quantity'] > item['product'].stock:
            stock_issues.append(item['product'].name)

    if stock_issues:
        messages.error(
            request,
            f'الكمية المطلوبة من المنتجات التالية غير متوفرة: {", ".join(stock_issues)}. '
            f'يُرجى تعديل السلة.'
        )
        return redirect('store:cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1) إعادة جلب المنتجات داخل المعاملة (لتجنب race conditions)
                    product_ids = [item['product'].id for item in cart_items]
                    products = (
                        Product.objects
                        .select_for_update()      # قفل الصفوف حتى نهاية المعاملة
                        .filter(id__in=product_ids)
                    )
                    products_map = {p.id: p for p in products}

                    # 2) التحقق النهائي من المخزون
                    for item in cart_items:
                        product = products_map.get(item['product'].id)
                        if not product or item['quantity'] > product.stock:
                            raise ValueError(
                                f'الكمية المطلوبة من "{item["product"].name}" غير متوفرة.'
                            )

                    # 3) إنشاء الطلب
                    order = Order.objects.create(
                        full_name=form.cleaned_data['full_name'],
                        phone=form.cleaned_data['phone'],
                        governorate=form.cleaned_data['governorate'],
                        city=form.cleaned_data['city'],
                        address=form.cleaned_data['address'],
                        notes=form.cleaned_data.get('notes', ''),
                        total_price=cart.get_total_price(),
                    )

                    # 4) إنشاء عناصر الطلب + تخفيض المخزون
                    for item in cart_items:
                        product = products_map[item['product'].id]

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            product_name=product.name,
                            price=product.price,
                            quantity=item['quantity'],
                        )

                        # تخفيض آمن باستخدام F() لتجنب race conditions
                        product.stock = F('stock') - item['quantity']
                        product.save(update_fields=['stock'])

                    # 5) مسح السلة
                    cart.clear()

                # 6) نجاح → إعادة توجيه لصفحة النجاح
                messages.success(request, 'تم استلام طلبك بنجاح! سنتواصل معك قريبًا.')
                return redirect('store:order_success', order_number=order.order_number)

            except ValueError as e:
                messages.error(request, str(e))
                return redirect('store:cart_detail')
            except Exception as e:
                messages.error(request, 'حدث خطأ أثناء معالجة الطلب. يُرجى المحاولة مجددًا.')
                return redirect('store:cart_detail')
        # إذا كان النموذج غير صالح → نكمل لعرض الأخطاء
    else:
        form = CheckoutForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'cart_total': cart.get_total_price(),
        'cart_count': len(cart),
    }
    return render(request, 'store/checkout.html', context)


def order_success(request, order_number):
    """صفحة نجاح الطلب."""
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'store/order_success.html', {'order': order})


# ==========================================
# تواصل معنا
# ==========================================

def contact(request):
    """صفحة التواصل + حفظ الرسائل."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data.get('phone', ''),
                message=form.cleaned_data['message'],
            )
            messages.success(
                request,
                'تم إرسال رسالتك بنجاح! سنتواصل معك في أقرب وقت.'
            )
            return redirect('store:contact')
    else:
        form = ContactForm()

    return render(request, 'store/contact.html', {'form': form})
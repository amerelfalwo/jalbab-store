"""
كلاس السلة — يعتمد على Session بدلًا من قاعدة البيانات.
يحفظ: { product_id (str): quantity (int) }
"""
from decimal import Decimal
from django.conf import settings
from .models import Product


class Cart:
    """سلة مشتريات مبنية على session."""

    SESSION_KEY = 'cart'

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(self.SESSION_KEY)
        if cart is None:
            cart = self.session[self.SESSION_KEY] = {}
        self.cart = cart

    # ---------- عمليات أساسية ----------

    def add(self, product, quantity=1):
        """
        إضافة منتج للسلة أو زيادة كميته.
        quantity مقيّدة بالمخزون المتاح.
        """
        product_id = str(product.id)
        quantity = int(quantity)

        current_qty = self.cart.get(product_id, 0)
        new_qty = current_qty + quantity

        # لا نتجاوز المخزون
        if new_qty > product.stock:
            new_qty = product.stock

        # لا نضيف كمية سالبة
        if new_qty < 1:
            new_qty = 1

        self.cart[product_id] = new_qty
        self.save()
        return new_qty

    def update(self, product, quantity):
        """تحديث كمية منتج موجود. إذا صارت 0 → حذفه."""
        product_id = str(product.id)
        quantity = int(quantity)

        if quantity <= 0:
            self.remove(product)
            return 0

        if quantity > product.stock:
            quantity = product.stock

        self.cart[product_id] = quantity
        self.save()
        return quantity

    def remove(self, product):
        """حذف منتج من السلة."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        """إفراغ السلة بالكامل."""
        self.session[self.SESSION_KEY] = {}
        self.session.modified = True

    def save(self):
        """تحديث الجلسة."""
        self.session[self.SESSION_KEY] = self.cart
        self.session.modified = True

    # ---------- قراءة ----------

    def __len__(self):
        """عدد القطع الكلي في السلة."""
        return sum(self.cart.values())

    def __iter__(self):
        """
        يُرجع عناصر السلة مع كائنات المنتج الفعلية.
        كل عنصر: { 'product': Product, 'quantity': int, 'subtotal': Decimal }
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids).select_related('category')
        products_map = {str(p.id): p for p in products}

        # إزالة المنتجات المحذوفة/غير المُفعّلة من السلة
        for product_id in list(self.cart.keys()):
            if product_id not in products_map:
                del self.cart[product_id]
        self.save()

        for product_id, quantity in self.cart.items():
            product = products_map.get(product_id)
            if not product:
                continue
            subtotal = product.price * quantity
            yield {
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            }

    def get_total_price(self):
        """إجمالي السلة بالجنيه."""
        total = Decimal('0.00')
        for item in self:
            total += item['subtotal']
        return total

    def get_total_items(self):
        """عدد القطع (مثل __len__ لكن واضح)."""
        return sum(self.cart.values())

    def is_empty(self):
        return len(self.cart) == 0
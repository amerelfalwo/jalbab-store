from django.db import models

# Create your models here.
"""
موديلات متجر جلباب
--------------------
- Category       : تصنيفات المنتجات (نقاب، عبايات، طرح)
- Product        : المنتجات
- Order          : الطلبات
- OrderItem      : عناصر الطلب (Snapshot للاسم والسعر)
- ContactMessage : رسائل نموذج التواصل
- HeroImage      : صورة الـ Hero الديناميكية
"""

from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator


# ==========================================
# 1) Category — التصنيفات
# ==========================================
class Category(models.Model):
    name = models.CharField("اسم التصنيف", max_length=100, unique=True)
    slug = models.SlugField("المُعرّف", max_length=120, unique=True, allow_unicode=True)
    description = models.TextField("الوصف", blank=True)
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)

    class Meta:
        verbose_name = "تصنيف"
        verbose_name_plural = "التصنيفات"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # توليد slug تلقائيًا من الاسم إذا لم يُحدّد
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product_list_by_category', args=[self.slug])


# ==========================================
# 2) Product — المنتجات
# ==========================================
class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,   # لا نحذف تصنيفًا فيه منتجات
        related_name='products',
        verbose_name="التصنيف"
    )
    name = models.CharField("اسم المنتج", max_length=200)
    slug = models.SlugField("المُعرّف", max_length=220, unique=True, allow_unicode=True)
    description = models.TextField("الوصف")
    image = models.ImageField("الصورة", upload_to='products/')

    price = models.DecimalField(
        "السعر الحالي (جنيه)",
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    old_price = models.DecimalField(
        "السعر قبل الخصم (جنيه)",
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text="اتركه فارغًا إذا لم يكن هناك خصم."
    )

    stock = models.PositiveIntegerField("المخزون", default=0)
    is_new = models.BooleanField("منتج جديد؟", default=False)
    is_discounted = models.BooleanField("عليه خصم؟", default=False)
    is_active = models.BooleanField("مُفعّل للعرض؟", default=True)

    created_at = models.DateTimeField("تاريخ الإضافة", auto_now_add=True)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # توليد slug تلقائيًا إذا لم يُحدّد
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            slug = base_slug
            counter = 1
            # ضمان عدم التكرار
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # مزامنة تلقائية لحقل is_discounted مع وجود old_price
        self.is_discounted = bool(
            self.old_price and self.old_price > self.price
        )
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

    # ------ خصائص مساعدة ------
    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def discount_percentage(self):
        """نسبة الخصم لاستخدامها في الـ Badge."""
        if self.is_discounted and self.old_price and self.old_price > 0:
            discount = (self.old_price - self.price) / self.old_price * 100
            return int(round(discount))
        return 0


# ==========================================
# 3) Order — الطلبات
# ==========================================
class Order(models.Model):
    STATUS_CHOICES = [
        ('new',         'جديد'),
        ('preparing',   'قيد التجهيز'),
        ('shipped',     'تم الشحن'),
        ('delivered',   'تم التسليم'),
        ('cancelled',   'ملغي'),
    ]

    order_number = models.CharField("رقم الطلب", max_length=20, unique=True, editable=False)

    # بيانات العميل
    full_name = models.CharField("الاسم الكامل", max_length=150)
    phone = models.CharField("رقم الهاتف", max_length=20)
    governorate = models.CharField("المحافظة", max_length=50)
    city = models.CharField("المدينة / المنطقة", max_length=100)
    address = models.TextField("العنوان بالتفصيل")
    notes = models.TextField("ملاحظات إضافية", blank=True)

    # بيانات الطلب
    status = models.CharField(
        "حالة الطلب", max_length=20,
        choices=STATUS_CHOICES, default='new'
    )
    total_price = models.DecimalField(
        "إجمالي الطلب (جنيه)",
        max_digits=10, decimal_places=2, default=0
    )

    created_at = models.DateTimeField("تاريخ الطلب", auto_now_add=True)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)

    class Meta:
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"
        ordering = ['-created_at']

    def __str__(self):
        return f"طلب #{self.order_number} — {self.full_name}"

    def save(self, *args, **kwargs):
        # توليد رقم طلب فريد من نوعه
        if not self.order_number:
            import uuid
            self.order_number = uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)

    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())


# ==========================================
# 4) OrderItem — عناصر الطلب
# ==========================================
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='items',
        on_delete=models.CASCADE,
        verbose_name="الطلب"
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="المنتج"
    )
    # Snapshot للاسم والسعر للحفاظ على بيانات الطلب
    product_name = models.CharField("اسم المنتج وقت الطلب", max_length=200)
    price = models.DecimalField("السعر وقت الطلب", max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField("الكمية", default=1)

    class Meta:
        verbose_name = "عنصر طلب"
        verbose_name_plural = "عناصر الطلب"

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity


# ==========================================
# 5) ContactMessage — رسائل التواصل
# ==========================================
class ContactMessage(models.Model):
    name = models.CharField("الاسم", max_length=150)
    email = models.EmailField("البريد الإلكتروني")
    phone = models.CharField("رقم الهاتف", max_length=20, blank=True)
    message = models.TextField("الرسالة")
    is_read = models.BooleanField("مقروءة؟", default=False)
    created_at = models.DateTimeField("تاريخ الإرسال", auto_now_add=True)

    class Meta:
        verbose_name = "رسالة تواصل"
        verbose_name_plural = "رسائل التواصل"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.email}"


# ==========================================
# 6) HeroImage — صورة الـ Hero الديناميكية
# ==========================================
class HeroImage(models.Model):
    title = models.CharField("العنوان الرئيسي", max_length=200, default="جلباب")
    subtitle = models.CharField(
        "الوصف القصير", max_length=300,
        default="أناقة إسلامية بلمسة عصرية"
    )
    image = models.ImageField("صورة الـ Hero", upload_to='hero/')
    button_text = models.CharField("نص زر التسوق", max_length=50, default="تسوق الآن")
    button_url = models.CharField(
        "رابط الزر", max_length=200,
        default="/products/",
        help_text="مثال: /products/ أو /products/nqab/"
    )
    is_active = models.BooleanField("مُفعّلة؟", default=True)
    created_at = models.DateTimeField("تاريخ الإضافة", auto_now_add=True)

    class Meta:
        verbose_name = "صورة رئيسية (Hero)"
        verbose_name_plural = "الصور الرئيسية (Hero)"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @classmethod
    def get_active(cls):
        """إرجاع الصورة النشطة الأولى (أو None)."""
        return cls.objects.filter(is_active=True).first()
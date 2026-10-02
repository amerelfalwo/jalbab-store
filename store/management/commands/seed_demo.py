"""
زرع بيانات تجريبية كاملة (تصنيفات، منتجات مع صور، وصورة Hero).
الاستخدام: python manage.py seed_demo
"""
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from store.models import Category, Product, HeroImage


def create_placeholder_image(text, width=800, height=600, bg_color=(45, 55, 72), text_color=(255, 255, 255)):
    image = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)
    
    # رسم مربع زخرفي بسيط في المنتصف
    margin = 40
    draw.rectangle([margin, margin, width - margin, height - margin], outline=(200, 200, 200), width=3)
    
    # كتابة النص (بشكل مغاير ببساطة)
    # نظراً لأن الخط الافتراضي بسيط، سنستخدم الخيار الافتراضي
    bbox = draw.textbbox((0, 0), text)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    # تكرار النص أو توزيعه
    draw.text(((width - text_w) / 2, (height - text_h) / 2), text, fill=text_color)
    
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = "إضافة بيانات وهمية للمتجر للمعاينة"

    def handle(self, *args, **options):
        self.stdout.write("جاري إنشاء البيانات الوهمية...")

        # 1. إنشاء التصنيفات
        categories_data = [
            {'name': 'نقابات', 'description': 'نقابات ملكية وبنقاط خامة فاخرة وخفيفة.'},
            {'name': 'عبايات', 'description': 'عبايات أنيقة مناسبة لجميع الأوقات.'},
            {'name': 'طرح وخمر', 'description': 'طرح وطرح طويلة وخمر بخامات ناعمة ومريحة.'},
        ]

        categories = {}
        for cat_info in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=cat_info['name'],
                defaults={
                    'slug': slugify(cat_info['name'], allow_unicode=True),
                    'description': cat_info['description'],
                }
            )
            categories[cat_info['name']] = cat

        # 2. إنشاء Hero Image
        if not HeroImage.objects.exists():
            hero = HeroImage(
                title="تشكيلة جلباب الجديدة",
                subtitle="أناقة إسلامية بلمسة عصرية وخامات عالية الجودة",
                button_text="تسوقي الآن",
                button_url="/products/",
                is_active=True
            )
            hero_img = create_placeholder_image("JALBAB STORE - HERO", width=1200, height=500, bg_color=(30, 41, 59))
            hero.image.save("hero_banner.jpg", hero_img, save=True)
            self.stdout.write(self.style.SUCCESS("✓ تم إنشاء صورة الهيرو (Hero)"))

        # 3. إنشاء منتجات وهمية
        products_data = [
            # نقابات
            {
                'category': categories['نقابات'],
                'name': 'نقاب ماليزي مقوى ثلاث طبقات',
                'price': 250,
                'old_price': 300,
                'stock': 15,
                'is_new': True,
                'description': 'نقاب ماليزي مقوى مصنوع من أجود أنواع الشيفون الكوري الناعم، مريح جداً للعين والتنفس.',
                'color': (51, 65, 85)
            },
            {
                'category': categories['نقابات'],
                'name': 'نقاب تندة قصير برباط ناعم',
                'price': 180,
                'old_price': None,
                'stock': 25,
                'is_new': False,
                'description': 'نقاب تندة بتصميم عملي وخفيف للاستخدام اليومي، مطاط خفيف خالي من الضغط.',
                'color': (71, 85, 105)
            },
            {
                'category': categories['نقابات'],
                'name': 'نقاب مائل مائل ملكي طازج',
                'price': 220,
                'old_price': 260,
                'stock': 10,
                'is_new': True,
                'description': 'تصميم ملكي رائع يمنحك مظهراً راقياً ومحتشماً.',
                'color': (30, 41, 59)
            },
            # عبايات
            {
                'category': categories['عبايات'],
                'name': 'عباية سوداء كلاسيك خامة كريب كوري',
                'price': 750,
                'old_price': 900,
                'stock': 8,
                'is_new': True,
                'description': 'عباية سوداء بقصة واسعة ومريحة، مصنوعة من قماش الكريب الكوري الفاخر مقاوم للتجعد.',
                'color': (15, 23, 42)
            },
            {
                'category': categories['عبايات'],
                'name': 'عباية بشت واسعة لأوقات الصيف',
                'price': 680,
                'old_price': 800,
                'stock': 12,
                'is_new': False,
                'description': 'عباية بشت انسيابية وخفيفة الوزن ومناسبة للأجواء الحارة.',
                'color': (51, 65, 85)
            },
            {
                'category': categories['عبايات'],
                'name': 'عباية كاجوال بأزرار أمامية',
                'price': 620,
                'old_price': None,
                'stock': 5,
                'is_new': True,
                'description': 'تصميم عصري يناسب الخروج والجامعة مع قصة عملية وألوان ثابتة.',
                'color': (71, 85, 105)
            },
            # طرح وخمر
            {
                'category': categories['طرح وخمر'],
                'name': 'خمار فرنسي طويل طبقتين',
                'price': 450,
                'old_price': 520,
                'stock': 20,
                'is_new': True,
                'description': 'خمار فرنسي ساتر وأنيق بطول ممتاز وتغطية كاملة.',
                'color': (30, 41, 59)
            },
            {
                'category': categories['طرح وخمر'],
                'name': 'طرحة شيفون كويتي عريضة',
                'price': 140,
                'old_price': 170,
                'stock': 30,
                'is_new': False,
                'description': 'طرحة شيفون كويتي ناعمة وتثبت بسهولة دون الانزلاق.',
                'color': (100, 116, 139)
            },
        ]

        for p_info in products_data:
            p_slug = slugify(p_info['name'], allow_unicode=True)
            if not Product.objects.filter(slug=p_slug).exists():
                product = Product(
                    category=p_info['category'],
                    name=p_info['name'],
                    slug=p_slug,
                    description=p_info['description'],
                    price=p_info['price'],
                    old_price=p_info['old_price'],
                    stock=p_info['stock'],
                    is_new=p_info['is_new'],
                    is_active=True
                )
                img_file = create_placeholder_image(
                    p_info['name'],
                    width=600,
                    height=700,
                    bg_color=p_info['color']
                )
                product.image.save(f"{p_slug}.jpg", img_file, save=True)
                self.stdout.write(self.style.SUCCESS(f"✓ تم إضافة المنتج: {product.name}"))

        self.stdout.write(self.style.SUCCESS("\n✨ اكتملت إضافة البيانات الوهمية بنجاح!"))

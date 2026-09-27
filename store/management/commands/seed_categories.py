"""
زرع التصنيفات الثلاثة الأساسية في قاعدة البيانات.
الاستخدام: python manage.py seed_categories
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category


class Command(BaseCommand):
    help = "إنشاء التصنيفات الأساسية (نقاب، عبايات، طرح)"

    def handle(self, *args, **options):
        categories = [
            {'name': 'نقاب',   'description': 'نقابات بأقمشة فاخرة وتصاميم أنيقة.'},
            {'name': 'عبايات', 'description': 'عبايات عصرية ورسمية بلمسة إسلامية.'},
            {'name': 'طرح',    'description': 'طرح بألوان وأقمشة متنوعة تناسب كل الأذواق.'},
        ]

        created_count = 0
        for cat in categories:
            obj, created = Category.objects.get_or_create(
                name=cat['name'],
                defaults={
                    'slug': slugify(cat['name'], allow_unicode=True),
                    'description': cat['description'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ تم إنشاء التصنيف: {obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"• التصنيف موجود بالفعل: {obj.name}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nاكتمل! تم إنشاء {created_count} تصنيف جديد."
        ))
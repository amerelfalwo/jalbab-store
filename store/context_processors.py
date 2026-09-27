"""
Context processors — متغيرات متاحة في كل القوالب.
"""
from .cart import Cart
from .models import Category

def cart_summary(request):
    """يُوفّر ملخص السلة (عدد القطع) لجميع القوالب."""
    cart = Cart(request)
    return {
        'cart_count': len(cart),
    }

def nav_categories(request):
    """يُوفّر التصنيفات للـ Navbar في جميع الصفحات."""
    return {
        'nav_categories': Category.objects.all(),
    }
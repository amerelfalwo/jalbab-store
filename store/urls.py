from django.urls import path, re_path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),

    path('products/', views.product_list, name='product_list'),
    # re_path يدعم Unicode (الحروف العربية في الـ slug)
    re_path(
        r'^products/(?P<category_slug>[-\w]+)/$',
        views.product_list,
        name='product_list_by_category'
    ),

    re_path(
        r'^product/(?P<slug>[-\w]+)/$',
        views.product_detail,
        name='product_detail'
    ),
        # -------- السلة (مؤقتة — ستُبنى فعليًا في المرحلة 7) --------
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    # إتمام الطلب
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<str:order_number>/', views.order_success, name='order_success'),    
    path('contact/', views.contact, name='contact'),

]
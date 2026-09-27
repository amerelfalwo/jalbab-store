"""
نماذج المتجر — Forms
"""
import re
from django import forms


# قائمة المحافظات المصرية (27 محافظة)
EGYPT_GOVERNORATES = [
    ('القاهرة', 'القاهرة'),
    ('الجيزة', 'الجيزة'),
    ('الإسكندرية', 'الإسكندرية'),
    ('الدقهلية', 'الدقهلية'),
    ('الشرقية', 'الشرقية'),
    ('القليوبية', 'القليوبية'),
    ('كفر الشيخ', 'كفر الشيخ'),
    ('الغربية', 'الغربية'),
    ('المنوفية', 'المنوفية'),
    ('البحيرة', 'البحيرة'),
    ('الإسماعيلية', 'الإسماعيلية'),
    ('بورسعيد', 'بورسعيد'),
    ('السويس', 'السويس'),
    ('شمال سيناء', 'شمال سيناء'),
    ('جنوب سيناء', 'جنوب سيناء'),
    ('الفيوم', 'الفيوم'),
    ('بني سويف', 'بني سويف'),
    ('المنيا', 'المنيا'),
    ('أسيوط', 'أسيوط'),
    ('سوهاج', 'سوهاج'),
    ('قنا', 'قنا'),
    ('الأقصر', 'الأقصر'),
    ('أسوان', 'أسوان'),
    ('البحر الأحمر', 'البحر الأحمر'),
    ('الوادي الجديد', 'الوادي الجديد'),
    ('مطروح', 'مطروح'),
    ('دمياط', 'دمياط'),
]


class CheckoutForm(forms.Form):
    """نموذج إتمام الطلب."""

    full_name = forms.CharField(
        label='الاسم الكامل',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'مثال: فاطمة أحمد محمد',
            'autocomplete': 'name',
        }),
    )

    phone = forms.CharField(
        label='رقم الهاتف',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'مثال: 01012345678',
            'autocomplete': 'tel',
            'inputmode': 'tel',
        }),
    )

    governorate = forms.ChoiceField(
        label='المحافظة',
        choices=[('', '— اختاري المحافظة —')] + EGYPT_GOVERNORATES,
        widget=forms.Select(attrs={'class': 'form-input'}),
    )

    city = forms.CharField(
        label='المدينة / المنطقة',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'مثال: مدينة نصر',
        }),
    )

    address = forms.CharField(
        label='العنوان بالتفصيل',
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'الشارع، رقم العمارة، الدور، رقم الشقة، علامة مميزة',
            'rows': 3,
        }),
    )

    notes = forms.CharField(
        label='ملاحظات إضافية (اختياري)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'مثال: يُرجى التواصل قبل التوصيل',
            'rows': 2,
        }),
    )

    # ---------- التحقق ----------

    def clean_full_name(self):
        name = self.cleaned_data['full_name'].strip()
        if len(name) < 3:
            raise forms.ValidationError('يُرجى إدخال الاسم الكامل (3 أحرف على الأقل).')
        if not re.search(r'[A-Za-z\u0600-\u06FF]', name):
            raise forms.ValidationError('الاسم يجب أن يحتوي على حروف.')
        return name

    def clean_phone(self):
        """التحقق من رقم هاتف مصري صحيح."""
        phone = self.cleaned_data['phone'].strip()

        # إزالة المسافات والشرطات
        phone = re.sub(r'[\s\-]', '', phone)

        # تحويل الأرقام العربية إلى إنجليزية إن وُجدت
        arabic_digits = '٠١٢٣٤٥٦٧٨٩'
        english_digits = '0123456789'
        for ar, en in zip(arabic_digits, english_digits):
            phone = phone.replace(ar, en)

        # صيغة مصرية: 01[0125]XXXXXXXX (11 رقمًا)
        pattern = r'^01[0125][0-9]{8}$'
        if not re.match(pattern, phone):
            raise forms.ValidationError(
                'يُرجى إدخال رقم هاتف مصري صحيح (11 رقمًا يبدأ بـ 010 أو 011 أو 012 أو 015).'
            )
        return phone

    def clean_city(self):
        city = self.cleaned_data['city'].strip()
        if len(city) < 2:
            raise forms.ValidationError('يُرجى إدخال اسم المدينة/المنطقة.')
        return city

    def clean_address(self):
        address = self.cleaned_data['address'].strip()
        if len(address) < 10:
            raise forms.ValidationError('يُرجى إدخال عنوان أكثر تفصيلًا (10 أحرف على الأقل).')
        return address

# ContactForm
class ContactForm(forms.Form):
    """نموذج التواصل."""

    name = forms.CharField(
        label='الاسم',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'اسمك الكريم',
            'autocomplete': 'name',
        }),
    )

    email = forms.EmailField(
        label='البريد الإلكتروني',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'example@email.com',
            'autocomplete': 'email',
        }),
    )

    phone = forms.CharField(
        label='رقم الهاتف (اختياري)',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '01xxxxxxxxx',
            'autocomplete': 'tel',
            'inputmode': 'tel',
        }),
    )

    message = forms.CharField(
        label='رسالتك',
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'اكتبي رسالتك هنا...',
            'rows': 5,
        }),
    )

    # ---------- التحقق ----------

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if len(name) < 3:
            raise forms.ValidationError('يُرجى إدخال الاسم (3 أحرف على الأقل).')
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            return ''
        # تحويل الأرقام العربية إلى إنجليزية
        arabic_digits = '٠١٢٣٤٥٦٧٨٩'
        english_digits = '0123456789'
        for ar, en in zip(arabic_digits, english_digits):
            phone = phone.replace(ar, en)
        phone = re.sub(r'[\s\-]', '', phone)
        # تحقق مصري إن كان الرقم مكتوبًا
        if not re.match(r'^01[0125][0-9]{8}$', phone):
            raise forms.ValidationError('يُرجى إدخال رقم هاتف مصري صحيح.')
        return phone

    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        if len(message) < 10:
            raise forms.ValidationError('يُرجى كتابة رسالة أكثر تفصيلًا (10 أحرف على الأقل).')
        return message
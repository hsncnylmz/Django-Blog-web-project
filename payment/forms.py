# payment_app/forms.py
from django import forms

class InvoiceForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    email = forms.EmailField(label='E-posta Adresi', required=False)
    phone_number = forms.CharField(label='Telefon Numarası', max_length=15, required=False)  
    
    # Fatura Bilgileri
    billing_title = forms.CharField(label='Fatura Başlığı', max_length=255, required=False)
    billing_address = forms.CharField(label='Fatura Adresi', max_length=255, required=False)
    city = forms.CharField(label='Şehir', max_length=255, required=False)
    postal_code = forms.CharField(label='Posta Kodu', max_length=10, required=False)
    country = forms.CharField(label='Ülke', max_length=255, required=False)
    
    # Ad ve Soyad
    first_name = forms.CharField(label='Ad', max_length=255, required=True)
    last_name = forms.CharField(label='Soyad', max_length=255, required=True)

    # Ek olarak, aşağıdaki gibi Django'nun özel widget'larını kullanarak bir ödeme yöntemi seçme alanı ekleyebilirsiniz.
    payment_method = forms.ChoiceField(
        label='Ödeme Yöntemi',
        choices=[
            ('eft', 'EFT / Havale'),
            ('iyzico', 'IYZICO'),
            # Diğer ödeme yöntemleri buraya eklenebilir
        ],
        widget=forms.RadioSelect,
        required=False
    )
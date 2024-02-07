# payment_app/models.py
from django.db import models
from paper.models import Paper

class Invoice(models.Model):
    # author bilgisi yerine ad soyad ve kullanıcı adı bilgisi eklendi
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=50, blank=True, null=True)  # iyzico'dan dönen işlem ID
    payment_status = models.CharField(max_length=20, blank=True, null=True)  # iyzico'dan dönen ödeme durumu
    email = models.EmailField(max_length=255, blank=True, null=True)  # Kullanıcının e-posta adresi
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Kullanıcının telefon numarası
    
    # Fatura Bilgileri
    billing_title = models.CharField(max_length=255, blank=True, null=True)  # Fatura başlığı
    billing_address = models.CharField(max_length=255, blank=True, null=True)  # Fatura adresi
    city = models.CharField(max_length=255, blank=True, null=True)  # Şehir
    postal_code = models.CharField(max_length=10, blank=True, null=True)  # Posta kodu
    country = models.CharField(max_length=255, blank=True, null=True)  # Ülke
    
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username}) - {self.paper.title} - Amount: {self.amount}"

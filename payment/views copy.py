# payment/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PaymentForm
from .models import Payment
from paper.models import Paper

def payment(request, paper_slug):
    paper = Paper.objects.get(slug=paper_slug)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']

            # Fatura Bilgileri
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            billing_title = form.cleaned_data['billing_title']
            billing_address = form.cleaned_data['billing_address']
            city = form.cleaned_data['city']
            postal_code = form.cleaned_data['postal_code']
            country = form.cleaned_data['country']

            # Ödeme işlemi başarılı olduğunu varsayalım
            # Gerçek bir ödeme entegrasyonu yapmadan önce, güvenli bir ödeme hizmeti kullanmalısınız

            # Ödeme kaydını oluştur
            payment = Payment.objects.create(
                author=request.user.profile,
                paper=paper,
                amount=amount,
                email=email,
                phone_number=phone_number,
                billing_title=billing_title,
                billing_address=billing_address,
                city=city,
                postal_code=postal_code,
                country=country
            )

            messages.success(request, f"{paper.title} başarıyla satın alındı. Ödeme ID: {payment.id}")
            return redirect('paper_detail', slug=paper_slug)

    else:
        form = PaymentForm()

    return render(request, 'payment/payment.html', {'form': form, 'paper': paper})

def payment_success(request):
    return render(request, 'payment/payment_success.html')

def payment_failure(request):
    return render(request, 'payment/payment_failure.html')

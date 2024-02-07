# invoice/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import InvoiceForm
from .models import Invoice
from paper.models import Paper
# payment iyzico/views.py
import iyzipay
import json
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import InvoiceForm
from .models import Paper

def invoice(request, paper_slug):
    paper = Paper.objects.get(slug=paper_slug)

def invoice(request, paper_slug):
    paper = Paper.objects.get(slug=paper_slug)

    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            # Formun doğruluğu onaylandığında burada formu işleyebilir ve gerekli işlemleri gerçekleştirebilirsiniz.
            # Örneğin, veritabanına kaydetme veya başka işlemler.

            # Varsayalım ki fatura verilerini depolamak için bir modeliniz var, buna Invoice diyelim
            # Bu örnek modeli ve kullanılan alanları gerçek model ve alanlarınızla değiştirebilirsiniz
            # Örneğin, Invoice.objects.create(paper=paper, amount=form.cleaned_data['amount'], ...)

            # Anasayfaya yönlendirme
            return redirect('payment:payment')

    else:
        # GET isteği durumunda, boş bir formu gönder
        form = InvoiceForm()

    return render(request, 'payment/invoice.html', {'paper': paper, 'form': form})


# def success(request):
#     return render(request, 'payment/payment_success.html')

# def fail(request):
#     return render(request, 'payment/payment_failure.html')

# payment iyzico/views.py

api_key = 'sandbox-VBdrbXQE60F4FyExrEPL3HxxYEKaMW95'
secret_key = 'sandbox-nlKE9Ed7Ace0uzXmtjIv9NOwRzDrXTte'
base_url = 'sandbox-api.iyzipay.com'

options ={
    'api_key': api_key,
    'secret_key':secret_key,
    'base_url':base_url
}

sozlukToken = list()

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# def index(request):
#     context = dict()
#     context['mesaj'] = 'django ile iyzico ödeme entegrasyonu'
#     template = 'index.html'

#     return render(request,template,context)

@csrf_exempt
def payment(request):
    context = dict()
    buyer={
        'id': 'BY789',
        'name': 'John',
        'surname': 'Doe',
        'gsmNumber': '+905350000000',
        'email': 'email@email.com',
        'identityNumber': '74300864791',
        'lastLoginDate': '2015-10-05 12:43:35',
        'registrationDate': '2013-04-21 15:12:09',
        'registrationAddress': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'ip': '85.34.78.112',
        'city': 'Istanbul',
        'country': 'Turkey',
        'zipCode': '34732'
    }

    address={
        'contactName': 'Jane Doe',
        'city': 'Istanbul',
        'country': 'Turkey',
        'address': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'zipCode': '34732'
    }

    basket_items=[
        {
            'id': 'BI101',
            'name': 'Binocular',
            'category1': 'Collectibles',
            'category2': 'Accessories',
            'itemType': 'PHYSICAL',
            'price': '0.3'
        },
        {
            'id': 'BI102',
            'name': 'Game code',
            'category1': 'Game',
            'category2': 'Online Game Items',
            'itemType': 'VIRTUAL',
            'price': '0.5'
        },
        {
            'id': 'BI103',
            'name': 'Usb',
            'category1': 'Electronics',
            'category2': 'Usb / Cable',
            'itemType': 'PHYSICAL',
            'price': '0.2'
        }
    ]

    request={
        'locale': 'tr',
        'conversationId': '123456789',
        'price': '1',
        'paidPrice': '5.0',
        'currency': 'TRY',
        'basketId': 'B67832',
        'paymentGroup': 'PRODUCT',
        "callbackUrl": "http://127.0.0.1:8000/payment/result/",
        "enabledInstallments": ['2', '3', '6', '9'],
        'buyer': buyer,
        'shippingAddress': address,
        'billingAddress': address,
        'basketItems': basket_items,
        # 'debitCardAllowed': True
    }
    checkout_form_initialize = iyzipay.CheckoutFormInitialize().create(request,options)
    page = checkout_form_initialize
    print('iyzico-sayfa')
    print(page)
    print('*'*50)
    content = checkout_form_initialize.read().decode('utf-8')
    print(content)
    print(type(content))
    print('*'*50)
    json_content = json.loads(content)
    print('*'*50)
    print(json_content['checkoutFormContent'])
    print('*'*50)
    print(json_content['token'])
    print('*'*50)
    sozlukToken.append(json_content['token'])
    return HttpResponse(json_content['checkoutFormContent'])

@require_http_methods(['POST'])
@csrf_exempt
def result(request):
    context = dict()

    url = request.META.get('home')

    request = {
        'locale':'tr',
        'conversationId':'123456789',
        'token':sozlukToken[0],
    }
    checkout_form_result = iyzipay.CheckoutForm().retrieve(request,options)
    print('*'*50)
    print('sonuc')
    print(type(checkout_form_result))
    print('*'*50)
    print(sozlukToken[0])
    result = checkout_form_result.read().decode('utf-8')
    sonuc = json.loads(result,object_pairs_hook=list)
    print('sonuc')
    print(sonuc[0][1])
    print(sonuc[5][1])
    for i in sonuc:
        print(i)
    print('*'*50)
    print('sozluk token')
    print(sozlukToken)
    print('*'*50)

    if sonuc[0][1] == 'success':
        context['success'] = 'başarılı işlem'
        return HttpResponseRedirect(reverse('payment:success'))  # Assuming 'payment' is the app namespace
    elif sonuc[0][1] == 'failure':
        context['failure'] = 'başarısız işlem'
        return HttpResponseRedirect(reverse('payment:fail'))  # Assuming 'payment' is the app namespace

    return HttpResponse(url)

def success(request):
    context = {'success_message': 'İşlem başarılı'}  # Update this message accordingly
    template = 'payment/success.html'

    return render(request, template, context)

def fail(request):
    context = {'fail_message': 'İşlem başarısız'}  # Update this message accordingly
    template = 'payment/failure.html'

    return render(request, template, context)
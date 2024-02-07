# paper views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from blog.models import Blog, Tag
from .models import Paper
from django.http import JsonResponse
from django.contrib import messages
from django.http import Http404
from .forms import PaperForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from payment.forms import InvoiceForm
from accountuser.models import UserProfile



def paper_list(request):
    papers = Paper.objects.all().order_by('-publish_date')
    tags = Tag.objects.all()
    latest_post = Blog.objects.filter(is_active=True, is_home=True).order_by('-publish_date').first()
    # Sayfalama için Paginator kullanımı
    paginator = Paginator(papers, 10)  # Her sayfada 10 makale gösterilecek
    page = request.GET.get('page')

    try:
        papers = paginator.page(page)
    except PageNotAnInteger:
        papers = paginator.page(1)
    except EmptyPage:
        papers = paginator.page(paginator.num_pages)

    context = {
        'papers': papers,
        'tags': tags,
        'latest_post': latest_post,
        'all_tags': Tag.objects.all(),
    }

    # Bu kısımda latest_papers fonksiyonunu çağırmalısınız
    latest_papers_data = latest_papers(request)
    context.update(latest_papers_data)

    return render(request, 'paper/paper_list.html', context)

def latest_papers(request):
    # Retrieve the latest papers from the database
    latest_papers = Paper.objects.order_by('-publish_date')[:5]  # Adjust the number as needed

    # Pass the latest_papers queryset to the template
    context = {'latest_papers': latest_papers}
    
    return context

def paper_detail(request, slug):
    paper = get_object_or_404(Paper, slug=slug)
    latest_posts = Blog.objects.order_by('-publish_date')[:3]
    latest_post = Blog.objects.filter(is_active=True, is_home=True).order_by('-publish_date').first()
    tags = Tag.objects.all()
    invoice_form = None
    user_profile = None
    show_full_content = True  # Varsayılan olarak tüm içeriği göster

    # Kullanıcının daha önce bu sayfayı ziyaret edip etmediğini kontrol et
    if not request.COOKIES.get(f'paper_viewed_{paper.id}', False):
        # Eğer ziyaret edilmemişse, views_count'u artır ve çereze işaretle
        paper.views_count += 1
        paper.save()

        # Çerez işaretleme
        response = render(request, 'paper/paper_detail.html', {
            'paper': paper,
            'show_full_content': show_full_content,
            'views_count': paper.views_count,
            'tags': paper.tags.all(),
            'upload_time': paper.publish_date,
            'file_exists': paper.file is not None,
            'user': request.user,
            'slug': slug,
            'latest_post': latest_post,
            'latest_posts': latest_posts,
            'invoice_form': invoice_form,
            'user_profile': user_profile,
            'all_tags': Tag.objects.all(),
        })
        response.set_cookie(f'paper_viewed_{paper.id}', True)
        return response

    # İçerik ücretli ise ve kullanıcı satın almamışsa
    if request.user.is_authenticated:
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=request.user)

        show_full_content = paper.paper_type != 'paid' or paper.is_purchased_by_user(user_profile)

        invoice_form = InvoiceForm()

        # if request.method == 'POST':
        #     invoice_form = InvoiceForm(request.POST)
        #     if invoice_form.is_valid():
        #         # Ödeme işlemi ve satın alma işlemleri burada gerçekleştirilebilir
        #         # Örneğin: invoice_success = True
        #         # if invoice_success:
        #         #     user_profile.purchased_papers.add(paper)
        #         #     return redirect('purchase_success')  # Satın alma başarılı sayfasına yönlendir

    context = {
        'paper': paper,
        'show_full_content': show_full_content,
        'views_count': paper.views_count,
        'tags': paper.tags.all(),
        'upload_time': paper.publish_date,
        'file_exists': paper.file is not None,
        'user': request.user,
        'slug': slug,
        'latest_posts': latest_posts,
        'invoice_form': invoice_form,
        'user_profile': user_profile,
        'latest_post': latest_post,
        'all_tags': Tag.objects.all(),
    }

    return render(request, 'paper/paper_detail.html', context)

def like_paper(request, slug):
    print(f"Like paper view triggered for slug: {slug}")
    paper_instance = get_object_or_404(Paper, slug=slug)
    paper_instance.like(request.user)
    data = {'likes': paper_instance.likes, 'dislikes': paper_instance.dislikes}
    return JsonResponse(data)

def dislike_paper(request, slug):
    print(f"Dislike paper view triggered for slug: {slug}")
    paper_instance = get_object_or_404(Paper, slug=slug)
    paper_instance.dislike(request.user)
    data = {'likes': paper_instance.likes, 'dislikes': paper_instance.dislikes}
    return JsonResponse(data)

@login_required
def create_paper(request):
    if request.method == 'POST':
        form = PaperForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Etiketleri kontrol et ve varsa kullan, yoksa oluştur
                tags = form.cleaned_data.get('tags', [])
                existing_tags = []

                for tag_list in tags:
                    tag_list = [tag.strip() for tag in tag_list.split(',') if tag.strip()]
                    for tag_name in tag_list:
                        tag, created = Tag.objects.get_or_create(name=tag_name)
                        existing_tags.append(tag)

                form.cleaned_data['tags'] = existing_tags  # Var olan veya yeni oluşturulan etiketleri formun tags alanına ekle
                form.save(user_profile=request.user.userprofile)
                
                messages.success(request, 'Paper successfully created!')
                return redirect('paper:paper_list')
            except ValueError as ve:
                messages.error(request, str(ve))
        else:
            messages.error(request, 'Error creating paper. Please check the form.')
    else:
        form = PaperForm()
    form_title = "Döküman Oluştur"
    return render(request, 'paper/create_paper.html', {'form': form, 'form_title': form_title})

@login_required
def edit_paper(request, slug):
    try:
        paper = Paper.objects.get(slug=slug)
    except Paper.DoesNotExist:
        raise Http404("Paper not found")
    
    if request.method == 'POST':
        form = PaperForm(request.POST, request.FILES, instance=paper)
        if form.is_valid():
            # Etiketleri kontrol et ve varsa kullan, yoksa oluştur
            tags = form.cleaned_data.get('tags', [])
            existing_tags = []

            for tag_list in tags:
                tag_list = [tag.strip() for tag in tag_list.split(',') if tag.strip()]
                for tag_name in tag_list:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    existing_tags.append(tag)

            form.cleaned_data['tags'] = existing_tags  # Var olan veya yeni oluşturulan etiketleri formun tags alanına ekle
            form.save()

            return redirect('paper:paper_list')
    else:
        form = PaperForm(instance=paper)

    return render(request, 'paper/edit_paper.html', {'form': form, 'form_title': 'Edit Paper'})


@login_required
def delete_paper(request, slug):
    user_profile = request.user.userprofile
    paper = get_object_or_404(Paper, slug=slug, author=user_profile)

    if request.method == 'POST':
        paper.delete()
        messages.success(request, 'Paper successfully deleted!')
        return redirect('paper:paper_list')

    return render(request, 'paper/delete_paper_confirm.html', {'paper': paper})
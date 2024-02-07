# blog views.py

from blog.models import Blog, Category, Tag, Comment, Reaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import BlogForm
from django.contrib import messages
from community.forms import CommentForm
from paper.models import Paper
from accountuser.models import UserProfile
from django.contrib.auth.decorators import login_required

# anonim kullanıcı yaratma
def is_anonymous(user):
    return user.is_anonymous

# arama yapma
def search_results(request):
    query = request.GET.get('q')

    # Başlıkta arama yapma
    blog_results_title = Blog.objects.filter(title__icontains=query)

    # Etiketlerde arama yapma
    blog_results_tags = Blog.objects.filter(tags__name__icontains=query)

    # Her iki sonucu birleştirme
    blog_results = blog_results_title | blog_results_tags

    paper_results = Paper.objects.filter(title__icontains=query)

    context = {
        'blog_results': blog_results,
        'paper_results': paper_results,
    }

    return render(request, 'search_results.html', context)

def blog_details(request, slug):
    blog = Blog.objects.get(slug=slug)
    latest_posts = Blog.objects.exclude(id=blog.id).order_by('-publish_date')[:3]
    latest_post = Blog.objects.filter(is_active=True, is_home=True).order_by('-publish_date').first()
    # Kullanıcının daha önce bu sayfayı ziyaret edip etmediğini kontrol et
    if not request.COOKIES.get(f'blog_viewed_{blog.id}', False):
        # Eğer ziyaret edilmemişse, views_count'u artır ve çereze işaretle
        blog.views_count += 1
        blog.save()
        response = render(request, "blog/blog-details.html", {
            'blog': blog,
            'comments': Comment.objects.filter(blog_comments=blog),
            'comment_form': CommentForm(user=request.user),
            'latest_posts': latest_posts,
            'latest_post': latest_post,
            'reaction_counts': Reaction.get_reaction_counts(blog),
            'all_tags': Tag.objects.all(),
        })
        # Çerezi işaretle
        response.set_cookie(f'blog_viewed_{blog.id}', True, max_age=24*60*60)  # 24 saat süresince çerez geçerli olacak
        return response

    if request.method == 'POST':
        comment_form = CommentForm(request.POST, user=request.user)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)

            # Kullanıcı kontrolü
            if request.user.is_authenticated:
                new_comment.user_profile = request.user.userprofile
            else:
                username = request.POST.get('name', '')
                email = request.POST.get('email', '')

                if not username and not email:
                    messages.error(request, 'Kullanıcı adı veya e-posta girmelisiniz.')
                    return redirect('blog_details', slug=slug)
                else:
                    new_comment.name = username
                    new_comment.email = email

            new_comment.save()
            new_comment.blog_comments.set([blog])
            return redirect('blog_details', slug=slug)

    else:
        comment_form = CommentForm(user=request.user)

    comments = Comment.objects.filter(blog_comments=blog)

    if request.method == 'POST' and 'reaction_type' in request.POST:
        reaction_type = request.POST.get('reaction_type')
        existing_reaction = Reaction.objects.filter(blog=blog, user=request.user).first()

        if existing_reaction:
            existing_reaction.reaction_type = reaction_type
            existing_reaction.save()
        else:
            Reaction.objects.create(blog=blog, user=request.user, reaction_type=reaction_type)

    reaction_counts = {
        'like_count': Reaction.objects.filter(blog=blog, reaction_type='like').count(),
        'dislike_count': Reaction.objects.filter(blog=blog, reaction_type='dislike').count(),
        'laugh_count': Reaction.objects.filter(blog=blog, reaction_type='laugh').count(),
        'surprise_count': Reaction.objects.filter(blog=blog, reaction_type='surprise').count(),
        'sad_count': Reaction.objects.filter(blog=blog, reaction_type='sad').count(),
    }

    return render(request, "blog/blog-details.html", {
        'blog': blog,
        'comments': Comment.objects.filter(blog_comments=blog),
        'comment_form': CommentForm(user=request.user),
        'latest_posts': latest_posts,
        'latest_post': latest_post,
        'reaction_counts': reaction_counts,
        'all_tags': Tag.objects.all(),
    })
    
def blog_reaction(request, slug):
    blog = Blog.objects.get(slug=slug)

    if request.method == 'POST' and 'reaction_type' in request.POST:
        reaction_type = request.POST.get('reaction_type')

        existing_reaction = Reaction.objects.filter(blog=blog, user=request.user).first()

        if existing_reaction:
            existing_reaction.reaction_type = reaction_type
            existing_reaction.save()
        else:
            Reaction.objects.create(blog=blog, user=request.user, reaction_type=reaction_type)

    # Reaksiyon sayılarını al ve JSON olarak geri döndür
    reaction_counts = Reaction.get_reaction_counts(blog)
    response_data = {'reaction_counts': reaction_counts}
    return JsonResponse(response_data)
    
def like_blog(request, slug):
    blog = Blog.objects.get(slug=slug)
    
    if request.method == 'POST':
        try:
            blog.like(request.user)
        except Exception as e:
            print(f"An error occurred while liking the blog: {e}")
            
    blog.like(request.user)
    data = {'likes': blog.likes, 'dislikes': blog.dislikes}
    return JsonResponse(data)

def dislike_blog(request, slug):
    blog = Blog.objects.get(slug=slug)
    blog.dislike(request.user)
    data = {'likes': blog.likes, 'dislikes': blog.dislikes}
    return JsonResponse(data)

def index(request):
    haber_tag = Tag.objects.get(name='haber')  # haber tag'ını bulun
    latest_post = Blog.objects.filter(is_active=True, is_home=True).order_by('-publish_date').first()

    context = {
        'blogs': Blog.objects.filter(is_active=True, is_home=True),
        'categories': Category.objects.all(),
        'all_tags': Tag.objects.all(),
        'haber_tag': haber_tag,
        'latest_post': latest_post,
    }

    # latest_papers fonksiyonunu çağır ve context'e ekle
    latest_papers_data = latest_papers(request)
    context.update(latest_papers_data)

    return render(request, "blog/index.html", context)

def blogs(request):
    context = {
        'blogs': Blog.objects.filter(is_active=True),
        'categories': Category.objects.all(),
        'all_tags': Tag.objects.all()
    }
    # latest_papers fonksiyonunu çağır ve context'e ekle
    latest_papers_data = latest_papers(request)
    context.update(latest_papers_data)

    return render(request, "blog/blogs.html", context)

def latest_papers(request):
    # Retrieve the latest papers from the database
    latest_papers = Paper.objects.order_by('-publish_date')[:5]  # Adjust the number as needed

    # Pass the latest_papers queryset to the template
    context = {'latest_papers': latest_papers}
    
    return context

def latest_posts(request):
    # En son 3 blog gönderisini al (örneğin)
    latest_blogs = Blog.objects.order_by('-publish_date')[:3]
    context = {'latest_blogs': latest_blogs}
    return render(request, "partials/_latest_posts.html", context)
    
def blogs_by_category(request, slug):
    context = {
        'blogs': Category.objects.get(slug=slug).blog_set.filter(is_active=True),
        'categories': Category.objects.all(),
        'selected_category': slug,
        'all_tags': Tag.objects.all()
    }
    return render(request, "blog/blogs.html", context)

def blogs_by_tag(request, slug):
    context = {
        'blogs': Tag.objects.get(name=slug).blog_set.filter(is_active=True),
        'tags': Tag.objects.all(),
        'haber': slug
    }
    return render(request, "blog/blogs_by_tag.html", context)

@login_required
def create_blog(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Kullanıcı bir UserProfile'a sahip değilse, bir tane oluştur
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = user_profile
            blog_post.save()
            form.save_m2m()  # ManyToManyField'ları kaydet

            return redirect('blog_details', slug=blog_post.slug)
    else:
        form = BlogForm()

    return render(request, 'blog/create_blog.html', {'form': form})

@login_required
def edit_blog(request, slug):
    user_profile = request.user.userprofile

    # Kullanıcının düzenlemek istediği blogu al veya 404 hatası fırlat
    blog_post = get_object_or_404(Blog, slug=slug, author=user_profile)

    # Kullanıcı kendi blogunu düzenliyorsa işlemi gerçekleştir
    if request.user == blog_post.author.user:
        if request.method == 'POST':
            form = BlogForm(request.POST, request.FILES, instance=blog_post)
            if form.is_valid():
                form.save()
                form.save_m2m()  # ManyToManyField'ları kaydet
                return redirect('blog_details', slug=blog_post.slug)
        else:
            form = BlogForm(instance=blog_post)

        return render(request, 'blog/edit_blog.html', {'form': form, 'blog_post': blog_post, 'user': request.user})
    else:
        # Kullanıcı kendi blogunu düzenlemiyor ise istediği sayfaya yönlendir
        return redirect('home')  # Veya başka bir sayfa

def delete_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    # Burada blogu silme işlemlerini gerçekleştir
    blog.delete()
    return redirect('home')  # Silme işleminden sonra kullanıcıyı bir sayfaya yönlendir
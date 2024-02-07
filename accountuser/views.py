from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from paper.models import Paper

def login_request(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        
        user = authenticate(request, username = username, password = password)
        
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return render(request, "account/login.html", {
                "error": "Kullanıcı veya parola yanlış!"
            })
        
    return render(request, "account/login.html")

def register_request(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]
        password = request.POST["password"]
        repassword = request.POST["repassword"]
        
        if password == repassword:
            if User.objects.filter(username=username).exists():
                return render(request, "account/register.html", 
                {
                    "error":"Kullanıcı adı kullanılıyor!",
                    "username":username,
                    "email":email,
                    "firstname":firstname,
                    "lastname":lastname
                })
            else:
                if User.objects.filter(email=email).exists():
                    return render(request, "account/register.html",
                    {
                        "error":"E-posta daha önce kullanılmış!",
                        "username":username,
                        "email":email,
                        "firstname":firstname,
                        "lastname":lastname
                    })
                else:
                    user = User.objects.create_user(username=username,email=email,first_name=firstname,last_name=lastname,password=password)
                    
                    # Kullanıcı oluşturulduktan sonra UserProfile oluştur ve kaydet
                    user_profile = UserProfile.objects.create(user=user)
                    user_profile.save()

                    return redirect("login") # kullanıcı oluşturulduktan sonra yönlendirilecek sayfa
        else:
            return render(request, "account/register.html", 
            {
                "error":"Girilen parolalar eşleşmiyor!",
                "username":username,
                "email":email,
                "firstname":firstname,
                "lastname":lastname
            })
        
    return render(request, "account/register.html")

def logout_request(request):
    logout(request)
    return redirect("home")

def profile(request, slug):
    try:
        user_profile_to_show = UserProfile.objects.get(slug=slug)
    except UserProfile.DoesNotExist:
        raise Http404("Kullanıcı profil bulunamadı")

    # Kullanıcının bloglarını al
    blog_list = user_profile_to_show.blog_set.all().order_by('-publish_date')
    # Sayfalama işlemi
    page = request.GET.get('page', 1)
    paginator = Paginator(blog_list, 5)  # Her sayfada 5 blog göster

    try:
        blogs = paginator.page(page)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages)
        
    # Kullanıcının paper'larını al
    paper_list = Paper.objects.filter(author=user_profile_to_show).order_by('-publish_date')

    # Sayfalama işlemi
    page = request.GET.get('page', 1)
    paginator = Paginator(paper_list, 5)  # Her sayfada 5 paper göster

    try:
        papers = paginator.page(page)
    except PageNotAnInteger:
        papers = paginator.page(1)
    except EmptyPage:
        papers = paginator.page(paginator.num_pages)

    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=request.user)

        roles = user_profile.get_roles()
        return render(request, 'account/profile.html', {'user_profile': user_profile_to_show, 'roles': roles, 'blogs': blogs, 'papers': papers})
    else:
        return render(request, 'account/profile.html', {'user_profile': user_profile_to_show, 'blogs': blogs, 'papers': papers})

@login_required
def edit_profile(request, slug):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile', slug=user_profile.slug)
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'account/edit_profile.html', {'form': form, 'user_profile': user_profile})

# account/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from allauth.socialaccount.models import SocialAccount


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    google_account = models.OneToOneField(SocialAccount, null=True, blank=True, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, verbose_name='Biyografi')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Profil Fotoğrafı')
    cover_photo = models.ImageField(upload_to='cover_photos/', blank=True, null=True, verbose_name='Kapak Fotoğrafı')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Doğum Tarihi')
    location = models.CharField(max_length=100, blank=True, verbose_name='Konum')
    website = models.URLField(blank=True, verbose_name='Website')
    twitter = models.CharField(max_length=100, blank=True, verbose_name='Twitter Kullanıcı Adı')
    github = models.CharField(max_length=200, blank=True, verbose_name='Github Kullanıcı Adı')
    linkedin = models.CharField(max_length=200, blank=True, verbose_name='Linkedin Kullanıcı Adı')  
    instagram = models.CharField(max_length=100, blank=True, verbose_name='Instagram Kullanıcı Adı')
    interests = models.TextField(blank=True, verbose_name='İlgi Alanları')
    education = models.CharField(max_length=100, blank=True, verbose_name='Eğitim')
    job = models.CharField(max_length=100, blank=True, verbose_name='İş')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Oluşturulma Tarihi')
    # Roller
    is_user = models.BooleanField(default=False, verbose_name='Kullanıcı Olabilir')
    is_yazar = models.BooleanField(default=False, verbose_name='Yazar Olabilir')
    is_editor = models.BooleanField(default=False, verbose_name='Editör Olabilir')
    is_moderator = models.BooleanField(default=False, verbose_name='Moderatör Olabilir')
    is_head_editor = models.BooleanField(default=False, verbose_name='Baş Editör Olabilir')
    is_admin = models.BooleanField(default=False, verbose_name='Admin')
    is_premium = models.BooleanField(default=False, verbose_name='Premium Olabilir')
    ROLES = (
        ('user', 'Kullanıcı'),
        ('yazar', 'Yazar'),
        ('editor', 'Editör'),
        ('moderator', 'Moderatör'),
        ('head_editor', 'Baş Editör'),
        ('premium', 'Premium'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='user', verbose_name='Kullanıcı Rolü')
    def get_roles(self):
        role_display_mapping = {
            'user': 'Kullanıcı',
            'yazar': 'Yazar',
            'editor': 'Editör',
            'moderator': 'Moderatör',
            'head_editor': 'Baş Editör',
            'premium': 'Premium',
            'admin': 'Admin',
        }
        
        roles = [role_display_mapping[role] for role, _ in self.ROLES if getattr(self, f'is_{role}')]
        if not roles:
            roles = ['Kullanıcı']  # Eğer hiçbir rol eşleşmezse, varsayılan olarak 'Kullanıcı' rolünü ata
        return roles

    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    purchased_papers = models.ManyToManyField('paper.Paper', blank=True)

    def check_purchased_paper(self, paper):
        if self.user.is_staff or self.is_premium:
            return True
        return self.purchased_papers.filter(id=paper.id).exists()
    
    @property
    def is_premium(self):
        # Burada, kullanıcının premium olup olmadığını belirleyecek bir kontrol ekleyin.
        # Örneğin, kullanıcı bir ücret ödediyse veya belirli bir abonelik düzeyine geçtiyse,
        # bu özelliği True olarak işaretleyin.
        return self.premium_membership_active()

    def premium_membership_active(self):
        # Kullanıcının premium üyeliğinin aktif olup olmadığını kontrol eden bir fonksiyon.
        # Örneğin, bir ücret ödeme sisteminiz varsa ve kullanıcı premium bir üyelik aldıysa True döndürün.
        # Aksi takdirde, False döndürün.
        return self.user.is_superuser  # Admin olduğu zaman premium kabul ediliyor
    
    def create_slug(self, username):
        if not self.slug:  # Eğer slug alanı zaten doluysa, tekrar oluşturmaya gerek yok
            base_slug = slugify(username)
            unique_slug = base_slug
            num = 1

            while UserProfile.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1

            return unique_slug
        return self.slug
    
    def formatted_created_at(self):
        return self.created_at.strftime('%Y-%m-%d %H:%M:%S')

    def create_slug(self, username):
        return slugify(username)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Kullanıcı profili oluşturulurken, slug alanını kontrol et
            self.slug = self.create_slug(self.user.username)

        super(UserProfile, self).save(*args, **kwargs)
        
                # Google ile giriş yapan kullanıcının bilgilerini kaydet
        if self.user.socialaccount_set.filter(provider='google').exists():
            google_account = self.user.socialaccount_set.get(provider='google')
            self.google_account = google_account
            self.save()

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

# paper\models.py

import re
from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django_resized import ResizedImageField
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
from blog.models import Tag
from accountuser.models import UserProfile

def get_user_profile_model():
    from accountuser.models import UserProfile
    return UserProfile

def validate_file_size(value):
    filesize = value.size
    
    if filesize > 1048576:  # 1 MB limit
        raise ValidationError("Dosya boyutu 1 MB'tan büyük olamaz.")

def increase_views_count(request, paper):
    # Bir kullanıcının bir makaleyi ziyaret ettiğini belirlemek için session anahtarını kullanabilirsiniz
    paper_key = f'paper_{paper.id}_viewed'

    if paper_key not in request.session:
        # Eğer session anahtarı yoksa, bu kullanıcının ilk ziyareti demektir
        request.session[paper_key] = True

        # views_count'u artırın ve veritabanına kaydedin
        paper.views_count += 1
        paper.save()

    return paper.views_count

class Paper(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    content = RichTextField()
    code_content = RichTextField(blank=True, null=True)
    cover_image = ResizedImageField(size=[800, 600], quality=75, upload_to="paper/images/", blank=True, null=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    publish_date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(null=False, blank=True, db_index=True, unique=True, editable=False)
    file = models.FileField(
        upload_to="paper/files/",
        blank=True,
        null=True,
        validators=[
            validate_file_size,
            FileExtensionValidator(allowed_extensions=['pdf', 'zip', 'rar'])
        ]
    )
    views_count = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True)
    reading_time = models.PositiveIntegerField(default=0)  # Okuma süresi alanı ekledim
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    free = 'free'
    paid = 'paid'
    PAPER_TYPE_CHOICES = [
        (free, 'Ücretsiz'),
        (paid, 'Ücretli'),
    ]
    paper_type = models.CharField(
        max_length=10,
        choices=PAPER_TYPE_CHOICES,
        default=free,
        blank=True,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    
    def is_purchased_by_user(self, user_profile):
            return user_profile.purchased_papers.filter(id=self.id).exists()
    
    def check_purchased_paper(self, user_profile):
        # Eğer kullanıcı admin veya premium ise, her zaman True döndür
        if user_profile.user.is_staff or user_profile.is_premium:
            return True
        # Aksi takdirde, kullanıcının satın aldığı kağıtları kontrol et
        return user_profile.purchased_papers.filter(id=self.id).exists()
    
    def get_file_size(self):
        if self.file:
            return f"{self.file.size / (1024 * 1024):.2f} MB"
        return "Dosya yok"
    
    def like(self, user):
        try:
            rating = Rating.objects.get(paper=self, user=user)
            if not rating.liked:
                rating.liked = True
                rating.save()
                self.likes += 1
                self.dislikes -= 1
                self.save()
        except Rating.DoesNotExist:
            Rating.objects.create(paper=self, user=user, liked=True)
            self.likes += 1
            self.save()

    def dislike(self, user):
        try:
            rating = Rating.objects.get(paper=self, user=user)
            if rating.liked:
                rating.liked = False
                rating.save()
                self.likes -= 1
                self.dislikes += 1
                self.save()
        except Rating.DoesNotExist:
            Rating.objects.create(paper=self, user=user, liked=False)
            self.dislikes += 1
            self.save()

    def cancel_rating(self, user):
        try:
            rating = Rating.objects.get(paper=self, user=user)
            if rating.liked:
                self.likes -= 1
            else:
                self.dislikes -= 1
            rating.delete()
            self.save()
        except Rating.DoesNotExist:
            pass

    def get_rating_status(self, user):
        try:
            rating = Rating.objects.get(paper=self, user=user)
            return "Liked" if rating.liked else "Disliked"
        except Rating.DoesNotExist:
            return "Not Rating"
    
    def calculate_reading_time(self):
        plain_text_content = re.sub(r'<.*?>', '', self.content)
        word_count = len(re.findall(r'\b\w+\b', plain_text_content))
        return max(1, round(word_count / 200))

    def save(self, *args, **kwargs):
        # Eğer slug alanı boşsa, başlıktan otomatik oluştur
        if not self.slug:
            self.slug = slugify(self.title)

        # Okuma süresini güncelle
        self.reading_time = self.calculate_reading_time()

        # Etiketleri her birini tek seferde kaydet
        super().save(*args, **kwargs)
        for tag in self.tags.all():
            tag.save()

    def get_absolute_url(self):
        return reverse('paper_detail', args=[str(self.slug)])

    def __str__(self):
        return self.title
    
    
class Rating(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paper_ratings')
    liked = models.BooleanField(default=False)

    class Meta:
        unique_together = ['paper', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.paper.title} - Liked: {self.liked}"



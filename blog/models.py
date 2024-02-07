from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.utils import timezone
from django.urls import reverse
from accountuser.models import UserProfile
from django.contrib.auth.models import User
from community.models import Comment
import re

class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(null=False, blank=True, unique=True, db_index=True, editable=False)
    
    def save(self,*args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    usage_count = models.PositiveIntegerField(default=1)

    def count_related_blogs(self):
        return self.blog_set.count()

    def save(self, *args, **kwargs):
        if not self.id:
            # İlk kayıt, id atanmamışsa kaydet
            super().save(*args, **kwargs)
        else:
            # İlk kayıt değilse normal kaydetme işlemi
            self.usage_count = self.count_related_blogs()
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Blog(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="blogs")
    description = models.CharField(max_length=1000)
    content = RichTextField()
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    is_home = models.BooleanField(default=False)
    publish_date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(null=False, blank=True, unique=True, db_index=True, editable=False)
    categories = models.ManyToManyField(Category, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    reading_time = models.PositiveIntegerField(default=0, help_text="Dakika")
    tags = models.ManyToManyField(Tag, blank=True)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    votes = models.ManyToManyField(User, related_name='voted_blogs', through='Vote', blank=True)
    comments = models.ManyToManyField(Comment, related_name='blog_comments', blank=True)

    def like(self, user):
        try:
            vote = Vote.objects.get(blog=self, user=user)
            if not vote.liked:
                vote.liked = True
                vote.save()
                self.likes += 1
                self.dislikes -= 1
                self.save()
        except Vote.DoesNotExist:
            Vote.objects.create(blog=self, user=user, liked=True)
            self.likes += 1
            self.save()

    def dislike(self, user):
        try:
            vote = Vote.objects.get(blog=self, user=user)
            if vote.liked:
                vote.liked = False
                vote.save()
                self.likes -= 1
                self.dislikes += 1
                self.save()
        except Vote.DoesNotExist:
            Vote.objects.create(blog=self, user=user, liked=False)
            self.dislikes += 1
            self.save()

    def cancel_vote(self, user):
        try:
            vote = Vote.objects.get(blog=self, user=user)
            if vote.liked:
                self.likes -= 1
            else:
                self.dislikes -= 1
            vote.delete()
            self.save()
        except Vote.DoesNotExist:
            pass

    def get_vote_status(self, user):
        try:
            vote = Vote.objects.get(blog=self, user=user)
            return "Liked" if vote.liked else "Disliked"
        except Vote.DoesNotExist:
            return "Not Voted"

    class Meta:
        get_latest_by = 'publish_date'

    def get_absolute_url(self):
        return reverse('blog_detail', args=[str(self.slug)])
    
    def calculate_reading_time(self):
        plain_text_content = re.sub(r'<.*?>', '', self.content)
        word_count = len(re.findall(r'\b\w+\b', plain_text_content))
        return max(1, round(word_count / 200))
    
    def update_views_count(self, request):
        last_visit = request.session.get(f'last_visit_{self.id}')
        if not last_visit:
            self.views_count += 1
            self.save()
            request.session[f'last_visit_{self.id}'] = timezone.now().isoformat()
    
    def save(self, *args, **kwargs):
        # Eğer slug alanı boşsa, başlıktan otomatik oluştur
        if not self.slug:
            self.slug = slugify(self.title)

        # Diğer kaydetme işlemleri
        super().save(*args, **kwargs)

        # Etiketlerin her birini tek seferde kaydet
        for tag in self.tags.all():
            tag.save()

        # Okuma süresini güncelle
        self.reading_time = self.calculate_reading_time()
        super().save(update_fields=['reading_time'])
    
    def __str__(self):
        return self.title

class Vote(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked = models.BooleanField()

    class Meta:
        unique_together = ['blog', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.blog.title}"
    

class Reaction(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    LAUGH = 'laugh'
    SURPRISE = 'surprise'
    SAD = 'sad'
    
    REACTION_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
        (LAUGH, 'Laugh'),
        (SURPRISE, 'Surprise'),
        (SAD, 'Sad'),
    ]

    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)

    def __str__(self):
        return f"{self.user.username} reacted {self.get_reaction_type_display()} to {self.blog.title}"

    @classmethod
    def get_reaction_counts(cls, blog):
        reaction_counts = cls.objects.filter(blog=blog).values('reaction_type').annotate(count=models.Count('reaction_type'))

        counts = {
            'like_count': 0,
            'dislike_count': 0,
            'laugh_count': 0,
            'surprise_count': 0,
            'sad_count': 0,
        }

        for item in reaction_counts:
            reaction_type = item['reaction_type']
            count = item['count']
            counts[f'{reaction_type.lower()}_count'] = count

        return counts
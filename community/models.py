# blogapp/community/models.py

from django.db import models
from accountuser.models import UserProfile
from django.contrib.auth.models import User

class Comment(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    anonymous_user_photo = models.ImageField(upload_to='anonymous_user_photos/', null=True, blank=True)
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    content = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user_profile:
            return f"{self.user_profile.user.username} - {self.creation_date}"
        else:
            return f"Anonymous - {self.creation_date}"

    class Meta:
        ordering = ["-creation_date"]
        
class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='question_images/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='answer_images/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
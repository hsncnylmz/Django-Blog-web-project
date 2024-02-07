# blogapp/community/forms.py
import random
from django import forms
from .models import Comment, Question, Answer

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'content', 'image']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content', 'image']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'content', 'anonymous_user_photo']

    def __init__(self, *args, **kwargs):
        # Kullanıcı objesini al ve çıkar, kullanıcı kayıtlı değilse None
        self.user = kwargs.pop('user', None)
        super(CommentForm, self).__init__(*args, **kwargs)
        
        # Bu alanları kullanıcı kayıtlı değilse göster
        if not self.user or not self.user.is_authenticated:
            self.fields['name'] = forms.CharField(max_length=100, required=True)
            self.fields['email'] = forms.EmailField(required=True)
        else:
            # Kullanıcı girişi yapıldıysa ad ve e-posta alanlarını gizle
            self.fields['name'].widget = forms.HiddenInput()
            self.fields['email'].widget = forms.HiddenInput()

    def save(self, commit=True):
        comment = super(CommentForm, self).save(commit=False)
        
        # Kullanıcı kayıtlı değilse, isim ve e-posta bilgilerini set et
        if not self.user or not self.user.is_authenticated:
            comment.name = self.cleaned_data['name']
            comment.email = self.cleaned_data['email']
            
            # Eğer anonymous_user_photo alanı boşsa, rastgele bir görsel ataması yap
            if not comment.anonymous_user_photo:
                random_images = ['avatar-01.jpg', 'avatar-02.jpg', 'avatar-03.jpg', 'avatar-04.jpg', 'avatar-05.jpg', 'avatar-06.jpg', 'avatar-07.jpg', 'avatar-08.jpg', 'avatar-09.jpg']
                selected_image = random.choice(random_images)
                comment.anonymous_user_photo = f'anonymous_user_photos/{selected_image}'
            
        if commit:
            comment.save()
        return comment

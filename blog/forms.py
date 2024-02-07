from django import forms
from ckeditor.fields import RichTextField
from ckeditor.widgets import CKEditorWidget
from django.utils.text import slugify
from .models import Blog, Category, Tag

class BlogForm(forms.ModelForm):
    title = forms.CharField(label='Başlık', initial='Blogunuz için yaratıcı bir başlık seçin')
    description = forms.CharField(label='Açıklama', initial='Blog konusu hakkında açıklama')
    content = forms.CharField()

    # Yeni eklenen alanlar
    original_title = forms.CharField(widget=forms.HiddenInput(), required=False)
    original_description = forms.CharField(widget=forms.HiddenInput(), required=False)

    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'custom-class'}),
        required=False,
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'custom-class'}),
        required=False,
    )

    class Meta:
        model = Blog
        fields = ['content', 'title', 'image', 'description', 'categories', 'tags', 'is_active', 'is_home']

    def __init__(self, *args, **kwargs):
        super(BlogForm, self).__init__(*args, **kwargs)

        # original_title ve original_description alanlarını güncelle
        instance = kwargs.get('instance')
        if instance:
            self.fields['original_title'].initial = instance.title
            self.fields['original_description'].initial = instance.description

        # Diğer alanlara ait güncellemeler
        self.fields['content'].widget.attrs.update({'class': 'custom-class'})
        self.fields['categories'].widget.attrs.update({'class': 'custom-class'})
        self.fields['tags'].widget.attrs.update({'class': 'custom-class'})
        self.fields['title'].widget.attrs.update({'class': 'custom-class'})
        self.fields['description'].widget.attrs.update({'class': 'custom-class'})

    def save(self, commit=True):
        blog = super().save(commit=False)
        
        # Eğer başlık veya açıklama değiştiyse, yeni bir slug oluştur
        if (blog.title != self.cleaned_data['original_title']) or (blog.description != self.cleaned_data['original_description']):
            base_slug = slugify(blog.title)
            counter = 1
            while Blog.objects.filter(slug=blog.slug).exclude(pk=blog.pk).exists():
                blog.slug = f"{base_slug}-{counter}"
                counter += 1

        if commit:
            blog.save()
            self.save_m2m()  # ManyToManyField'ları kaydet

        return blog

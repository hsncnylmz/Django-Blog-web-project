# paper/forms.py

from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import Paper, Tag 

class PaperForm(forms.ModelForm):
    tags = forms.CharField(max_length=255, required=False, help_text="Etiketler (virgülle ayır)")
    price = forms.DecimalField(initial=0.00, required=False, min_value=0.00, help_text="Ücretli makalelerin fiyatı")
    # Burada paper_type alanını zorunlu olmayan (required=False) olarak ayarlıyoruz.
    paper_type = forms.ChoiceField(choices=Paper.PAPER_TYPE_CHOICES, required=False)
    
    class Meta:
        model = Paper
        fields = ['title', 'description', 'content', 'code_content', 'cover_image', 'file', 'is_active', 'tags', 'paper_type', 'price']
        widgets = {
            'content': CKEditorWidget(),
            'code_content': CKEditorWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # İsterseniz paper_type alanının seçeneklerini burada ayarlayabilirsiniz.
        # Örneğin:
        # self.fields['paper_type'].widget.choices = Paper.PAPER_TYPE_CHOICES

    def save(self, commit=True, user_profile=None):
        paper = super().save(commit=False)

        # Kullanıcı profili parametre olarak geçildiyse, author alanını ayarla
        if user_profile:
            paper.author = user_profile
        else:
            raise ValueError("Paper kaydetmek için kullanıcı profili sağlanmalıdır.")

        paper.save()

        # Tags alanındaki değerleri kontrol et ve varsa kullan, yoksa oluştur
        tags = self.cleaned_data.get('tags', None)

        # Eğer tags bir liste ise, direkt olarak bu listeyi kullan
        if tags is not None and isinstance(tags, list):
            tag_list = tags
        else:
            # Geçersiz bir değer veya boş bir değer varsa, boş bir liste kullan
            tag_list = [tag.strip() for tag in (tags or '').split(',') if tag.strip()]

        # Mevcut etiketleri kontrol et ve varsa kullan, yoksa oluştur
        for tag_name in tag_list:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            paper.tags.add(tag)

        # Mevcut etiketleri temizle
        paper.tags.clear()

        # Eğer makale ücretli ise, price alanındaki değeri ayarla
        if paper.paper_type == Paper.paid:
            paper.price = self.cleaned_data.get('price', 0.00)

        if commit:
            paper.save()
        return paper



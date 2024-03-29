# Generated by Django 5.0 on 2024-01-28 00:09

import ckeditor.fields
import django.core.validators
import django.db.models.deletion
import django_resized.forms
import paper.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accountuser', '__first__'),
        ('blog', '0010_alter_reaction_reaction_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=1000)),
                ('content', ckeditor.fields.RichTextField()),
                ('code_content', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('cover_image', django_resized.forms.ResizedImageField(blank=True, crop=None, force_format=None, keep_meta=True, null=True, quality=75, scale=None, size=[800, 600], upload_to='paper/images/')),
                ('is_active', models.BooleanField(default=False)),
                ('publish_date', models.DateTimeField(auto_now_add=True)),
                ('slug', models.SlugField(blank=True, editable=False, unique=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='paper/files/', validators=[paper.models.validate_file_size, django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'zip', 'rar'])])),
                ('views_count', models.PositiveIntegerField(default=0)),
                ('reading_time', models.PositiveIntegerField(default=0)),
                ('likes', models.PositiveIntegerField(default=0)),
                ('dislikes', models.PositiveIntegerField(default=0)),
                ('paper_type', models.CharField(blank=True, choices=[('free', 'Ücretsiz'), ('paid', 'Ücretli')], default='free', max_length=10)),
                ('price', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accountuser.userprofile')),
                ('tags', models.ManyToManyField(blank=True, to='blog.tag')),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liked', models.BooleanField(default=False)),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='paper.paper')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paper_ratings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('paper', 'user')},
            },
        ),
    ]

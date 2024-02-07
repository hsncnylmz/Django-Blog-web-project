# Generated by Django 5.0 on 2024-01-27 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_alter_reaction_reaction_type_alter_reaction_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reaction',
            name='reaction_type',
            field=models.CharField(choices=[('like', 'Like'), ('dislike', 'Dislike'), ('laugh', 'Laugh'), ('surprise', 'Surprise'), ('sad', 'Sad')], max_length=20),
        ),
    ]

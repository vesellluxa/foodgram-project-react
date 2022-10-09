# Generated by Django 3.2 on 2022-10-05 16:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0004_auto_20220731_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favourite',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.fooduser', verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.fooduser', verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.TextField(verbose_name='Картинка'),
        ),
        migrations.AlterField(
            model_name='shoppinglist',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.fooduser', verbose_name='Владелец'),
        ),
    ]
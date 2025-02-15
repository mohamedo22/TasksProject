# Generated by Django 5.1.4 on 2025-02-05 00:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='superadmin',
            name='profileImage',
            field=models.ImageField(default='profileImages/defaultUserProfile.png', upload_to=''),
        ),
        migrations.AlterField(
            model_name='taskimages',
            name='image',
            field=models.ImageField(upload_to=''),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profileImage',
            field=models.ImageField(default='profileImages/defaultUserProfile.png', null=True, upload_to=''),
        ),
    ]

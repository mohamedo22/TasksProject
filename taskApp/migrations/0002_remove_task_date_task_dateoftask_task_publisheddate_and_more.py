# Generated by Django 5.1.2 on 2024-12-09 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskApp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='date',
        ),
        migrations.AddField(
            model_name='task',
            name='dateOfTask',
            field=models.DateField(default=None),
        ),
        migrations.AddField(
            model_name='task',
            name='publishedDate',
            field=models.DateTimeField(auto_now_add=True, default=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profileImage',
            field=models.ImageField(default='profileImages/defaultUserProfile.png', upload_to='profileImages'),
        ),
    ]

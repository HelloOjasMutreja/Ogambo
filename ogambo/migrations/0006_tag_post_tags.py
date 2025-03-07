# Generated by Django 5.1.3 on 2024-11-27 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ogambo', '0005_vote_user_alter_vote_ip_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='posts', to='ogambo.tag'),
        ),
    ]

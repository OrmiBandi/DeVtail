# Generated by Django 4.2.7 on 2024-01-10 13:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name': '카테고리',
                'verbose_name_plural': '카테고리',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('is_secret', models.BooleanField(default=False)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
            ],
            options={
                'verbose_name': '댓글',
                'verbose_name_plural': '댓글',
            },
        ),
        migrations.CreateModel(
            name='Study',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goal', models.CharField(max_length=100)),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='study/imgs/%Y/%m/%d/')),
                ('start_at', models.DateField()),
                ('end_at', models.DateField()),
                ('introduce', models.TextField(blank=True, null=True)),
                ('topic', models.CharField(blank=True, max_length=100, null=True)),
                ('difficulty', models.CharField(choices=[('상', '상'), ('중', '중'), ('하', '하')], max_length=2)),
                ('current_member', models.IntegerField(default=0)),
                ('max_member', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='studies', to='studies.category')),
            ],
            options={
                'verbose_name': '스터디',
                'verbose_name_plural': '스터디',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='studies.study')),
            ],
            options={
                'verbose_name': '태그',
                'verbose_name_plural': '태그',
            },
        ),
        migrations.CreateModel(
            name='StudyMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_accepted', models.BooleanField(default=False)),
                ('is_manager', models.BooleanField(default=False)),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='studies.study')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='studies', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '스터디 멤버',
                'verbose_name_plural': '스터디 멤버',
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField(choices=[(1, '월요일'), (2, '화요일'), (3, '수요일'), (4, '목요일'), (5, '금요일'), (6, '토요일'), (7, '일요일')])),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='studies.study')),
            ],
            options={
                'verbose_name': '스터디 일정',
                'verbose_name_plural': '스터디 일정',
            },
        ),
        migrations.CreateModel(
            name='RefLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link_type', models.CharField(max_length=100)),
                ('url', models.CharField(max_length=100)),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ref_links', to='studies.study')),
            ],
            options={
                'verbose_name': '참조링크',
                'verbose_name_plural': '참조링크',
            },
        ),
        migrations.CreateModel(
            name='Recomment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('is_secret', models.BooleanField(default=False)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recomments', to='studies.comment')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recomments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '대댓글',
                'verbose_name_plural': '대댓글',
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('study', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='favorites', to='studies.study')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '스터디 즐겨찾기',
                'verbose_name_plural': '스터디 즐겨찾기',
            },
        ),
        migrations.AddField(
            model_name='comment',
            name='study',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='studies.study'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Blacklist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blacklists', to='studies.study')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blacklists', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '스터디 블랙리스트',
                'verbose_name_plural': '스터디 블랙리스트',
            },
        ),
    ]
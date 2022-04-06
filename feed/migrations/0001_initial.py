# Generated by Django 3.2.7 on 2021-09-23 14:32

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
            name="Entry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(help_text="Title of entry.", max_length=200),
                ),
                (
                    "link",
                    models.CharField(
                        help_text="Link of entry.", max_length=500, unique=True
                    ),
                ),
                (
                    "summary",
                    models.CharField(help_text="Summary of entry.", max_length=2000),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, help_text="Creation time of entry."
                    ),
                ),
                (
                    "published_at",
                    models.DateTimeField(help_text="Publish Time of entry."),
                ),
            ],
            options={
                "verbose_name_plural": "entries",
                "ordering": ("-published_at",),
            },
        ),
        migrations.CreateModel(
            name="Feed",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        default=None,
                        help_text="Title of feed.",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "link",
                    models.URLField(
                        db_index=True, help_text="Link of feed.", unique=True
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("A", "ACTIVE"), ("P", "PENDING"), ("E", "ERROR")],
                        db_index=True,
                        default="P",
                        help_text="Status of feed.",
                        max_length=1,
                    ),
                ),
                (
                    "priority",
                    models.SmallIntegerField(
                        choices=[(2, "HIGH"), (1, "LOW"), (0, "STOP")],
                        db_index=True,
                        default=2,
                        help_text="Priority of feed.",
                    ),
                ),
                (
                    "timeout",
                    models.SmallIntegerField(
                        choices=[
                            (1, 1),
                            (2, 2),
                            (3, 3),
                            (4, 4),
                            (5, 5),
                            (6, 6),
                            (7, 7),
                            (8, 8),
                            (9, 9),
                            (10, 10),
                        ],
                        default=2,
                        help_text="Timeout of fetching of feed.",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "updated_at",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("title",),
            },
        ),
        migrations.CreateModel(
            name="FollowFeed",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "feed",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="feed.feed"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "feed")},
            },
        ),
        migrations.AddField(
            model_name="feed",
            name="followers",
            field=models.ManyToManyField(
                related_name="feed_followed",
                through="feed.FollowFeed",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="EntryRead",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="feed.entry"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "entry")},
            },
        ),
        migrations.AddField(
            model_name="entry",
            name="feed",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="feed.feed"
            ),
        ),
        migrations.AddField(
            model_name="entry",
            name="reads",
            field=models.ManyToManyField(
                related_name="entries_read",
                through="feed.EntryRead",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]

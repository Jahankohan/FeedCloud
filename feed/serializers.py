from django.db import transaction
from rest_framework import serializers

from authnz.serializers import NestedUserSerializer
from feed.models import Feed


class FeedSerializers(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(
        max_length=100, min_length=3, required=False, allow_blank=True
    )
    link = serializers.URLField(max_length=200, min_length=5, required=True)
    timeout = serializers.ChoiceField(choices=Feed.timeout_choices, default=2)
    force_update = serializers.BooleanField(write_only=True, default=True)
    creator = NestedUserSerializer(read_only=True)
    status = serializers.CharField(read_only=True)
    priority = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if not self.instance:  # check for update or create
            data.pop("force_update")
        return data

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        if (
            not self.context["request"].user.is_staff
            and self.context.get("my_feeds")
            and not self.context["my_feeds"]
        ):
            # remove fields that we don't want regular user see
            # just show it to staffs and creator of feed
            staff_creator_only_fields = (
                "creator",
                "status",
                "priority",
                "created_at",
                "updated_at",
                "timeout",
            )
            for field in staff_creator_only_fields:
                instance.pop(field)
        return instance

    @transaction.atomic
    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        feed = Feed(**validated_data)
        feed.save()
        return feed

    @transaction.atomic
    def update(self, instance, validated_data):
        instance = Feed.objects.select_for_update().get(id=instance.id)
        update_fields = []
        if validated_data.get("title") and instance.title != validated_data["title"]:
            instance.title = validated_data["title"]
            update_fields.append("title")
        elif validated_data.get("title") == "":
            instance.title = ""
            update_fields.append("title")
        if validated_data.get("link") and instance.link != validated_data["link"]:
            instance.link = validated_data["link"]
            update_fields.append("link")
        if (
            validated_data.get("timeout")
            and instance.timeout != validated_data["timeout"]
        ):
            instance.timeout = validated_data["timeout"]
            update_fields.append("timeout")
        if "link" in update_fields or validated_data.get("force_update"):
            # with usage of django signals update_feed will be called and
            # it will call fetch_feed_entries background task
            instance.status = Feed.PENDING
            update_fields.append("status")
        instance.save(update_fields=update_fields)
        return instance


class NestedFeedEntrySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(read_only=True)


class EntrySerializers(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    link = serializers.URLField(read_only=True)
    summary = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    published_at = serializers.DateTimeField(read_only=True)
    feed = NestedFeedEntrySerializer(read_only=True)

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        if not self.context["request"].user.is_staff:
            # remove fields that we don't want regular user see
            staff_only_fields = ("created_at",)
            for field in staff_only_fields:
                instance.pop(field)
        return instance


class EntryListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    summary = serializers.CharField(read_only=True)
    feed = NestedFeedEntrySerializer(read_only=True)


class FollowListSerializer(serializers.Serializer):
    feeds = serializers.ListField(
        child=NestedFeedEntrySerializer(), min_length=1, max_length=20
    )

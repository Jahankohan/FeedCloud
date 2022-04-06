from django.urls import path

from feed import views as feed_views


urlpatterns = [
    path("feeds", feed_views.FeedCreateListView.as_view(), name="feeds"),
    path(
        "feeds/my_feeds", feed_views.FeedCreatedByMeListView.as_view(), name="my_feeds"
    ),
    path(
        "feeds/<int:instance_id>",
        feed_views.FeedUpdateView.as_view(),
        name="feeds_update",
    ),
    path(
        "feeds/followed/<int:feed_id>",
        feed_views.FeedUnFollowView.as_view(),
        name="feed_unfollow",
    ),
    path("feeds/followed", feed_views.FeedFollowView.as_view(), name="feed_follow"),
    path(
        "feeds/<int:feed_id>/entries",
        feed_views.EntryListView.as_view(),
        name="feed_entries",
    ),
    path("entries", feed_views.EntryListView.as_view(), name="entries"),
    path("entries/read", feed_views.EntryReadView.as_view(), name="entry_read"),
]

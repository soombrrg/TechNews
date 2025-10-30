from random import randint

import pytest
from django.urls import reverse
from django.utils.dateparse import parse_datetime

from main.api.serializers import (
    PostCreateUpdateSerializer,
    PostDetailSerializer,
    PostListSerializer,
)
from main.models import Post

pytestmark = [pytest.mark.django_db]


class TestPostList:
    def test_permission_for_not_authenticated(self, api, post):
        response = api.get(reverse("v1:posts:post-list"))
        assert response.get("results")[0]["title"] == post.title

        response = api.post(reverse("v1:posts:post-list"), expected_status_code=401)

    def test_get_fields(self, api, post):
        response = api.get(reverse("v1:posts:post-list"))
        response_results = response["results"]

        serializer = PostListSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response_results[0]

        assert response_results[0]["title"] == post.title

    def test_post_fields(self, api, auth_user):
        response = api.post(
            reverse("v1:posts:post-list"),
            data={"title": "Test title", "content": "Test content"},
            expected_status_code=201,
        )

        serializer = PostCreateUpdateSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response

        assert response["title"] == "Test title"
        assert response["content"] == "Test content"

    def test_get_w_users_draft(self, api, auth_user, mixer):
        """Test getting posts with drafted, when User is author"""
        post_1 = mixer.blend(Post, author=auth_user, publication_status=Post.PUBLISHED)
        post_2 = mixer.blend(Post, author=auth_user, publication_status=Post.DRAFT)

        response = api.get(reverse("v1:posts:post-list"))
        response_results = response["results"]

        # posts in view ordered by desc creation
        assert response_results[0]["id"] == post_2.id
        assert response_results[0]["title"] == post_2.title
        assert response_results[1]["id"] == post_1.id
        assert response_results[1]["title"] == post_1.title

        assert len(response_results) == 2

    def test_get_w_draft_not_users(self, api, auth_user, mixer):
        """Test not getting drafted post, when User is not author"""
        post_1 = mixer.blend(Post, publication_status=Post.PUBLISHED)
        post_2 = mixer.blend(Post, publication_status=Post.DRAFT)

        response = api.get(reverse("v1:posts:post-list"))
        response_results = response["results"]

        assert response_results[0]["title"] == post_1.title

        assert len(response_results) == 1


class TestPostDetail:
    def test_permission_for_not_authenticated(self, api, post):
        response = api.get(reverse("v1:posts:post-detail", kwargs={"slug": post.slug}))
        assert response["title"] == post.title

        response = api.api_client.patch(
            reverse("v1:posts:post-detail", kwargs={"slug": post.slug}),
            data={"content": "Test content"},
        )
        assert response.status_code == 401

    def test_permission_for_authenticated_but_not_author(self, api, auth_user, mixer):
        post_1 = mixer.blend(
            Post,
        )
        response = api.api_client.patch(
            reverse("v1:posts:post-detail", kwargs={"slug": post_1.slug}),
            data={"content": "Test content"},
        )
        assert response.status_code == 403

    def test_get_fields(self, api, post):
        response = api.get(reverse("v1:posts:post-detail", kwargs={"slug": post.slug}))

        serializer = PostDetailSerializer()
        expected_fields = serializer.fields
        for field in expected_fields:
            assert field in response

    def test_views_count_incr(self, api, post):
        response = api.get(reverse("v1:posts:post-detail", kwargs={"slug": post.slug}))
        assert response["views_count"] == post.views_count + 1

        response = api.get(reverse("v1:posts:post-detail", kwargs={"slug": post.slug}))
        assert response["views_count"] == post.views_count + 2

    @pytest.mark.parametrize("method", ["put", "patch"])
    @pytest.mark.parametrize(
        "data, validity",
        [
            (
                {
                    "title": "New title",
                    "content": "New content",
                    "publication_status": Post.PUBLISHED,
                },
                True,
            ),
            ({"publication_status": "not valid"}, False),
        ],
    )
    def test_update(self, api, auth_user, post, method, data, validity):
        if method == "put":
            response = api.api_client.put(
                reverse("v1:posts:post-detail", kwargs={"slug": post.slug}),
                data=data,
            )
        if method == "patch":
            response = api.api_client.put(
                reverse("v1:posts:post-detail", kwargs={"slug": post.slug}),
                data=data,
            )
        if validity:
            assert response.status_code == 200
            assert response.data["title"] == data["title"]
            assert response.data["content"] == data["content"]

            serializer = PostCreateUpdateSerializer()
            expected_fields = serializer.fields

            for field in expected_fields:
                assert field in response.data
        else:
            assert response.status_code == 400


@pytest.mark.parametrize("view_name", ["recent-posts", "popular-posts"])
class TestRecentAndPopularPosts:
    def test_not_valid_method(self, view_name, api, post):
        response = api.post(
            reverse(f"v1:posts:{view_name}"),
            expected_status_code=405,
        )

    def test_no_posts(self, view_name, api):
        response = api.get(reverse(f"v1:posts:{view_name}"))
        assert response == []

    def test_get_fields(self, view_name, api, mixer):
        post_1 = mixer.blend(Post, views_count=10, publication_status=Post.PUBLISHED)
        post_2 = mixer.blend(Post, views_count=5, publication_status=Post.PUBLISHED)
        post_3 = mixer.blend(Post, views_count=2, publication_status=Post.DRAFT)

        response = api.get(reverse(f"v1:posts:{view_name}"))

        # Test response fields
        posts_serializer = PostListSerializer()
        for field in posts_serializer.fields:
            assert field in response[0]
        if view_name == "popular-posts":
            # Posts in view ordered by desc "views_count"
            assert response[0]["id"] == post_1.id
            assert response[0]["title"] == post_1.title
            assert response[1]["id"] == post_2.id
            assert response[1]["title"] == post_2.title
        if view_name == "recent-posts":
            # Posts in view ordered by desc "created"
            assert response[0]["id"] == post_2.id
            assert response[0]["title"] == post_2.title
            assert response[1]["id"] == post_1.id
            assert response[1]["title"] == post_1.title

        assert len(response) == 2

    def test_get_more_then_10_posts(self, view_name, api, mixer):
        posts = []
        for i in range(40):
            posts.append(
                mixer.blend(
                    Post,
                    views_count=randint(0, 99999),
                    publication_status=Post.PUBLISHED,
                )
            )

        response = api.get(reverse(f"v1:posts:{view_name}"))

        # View should return only 10 post
        assert len(response) == 10

        ordered_posts = Post.objects.none()

        if view_name == "popular-posts":
            ordered_posts = Post.objects.order_by("-views_count")[:10]
        if view_name == "recent-posts":
            ordered_posts = Post.objects.order_by("-created")[:10]
        for i in range(10):
            assert response[i]["id"] == ordered_posts[i].pk
            assert response[i]["views_count"] == ordered_posts[i].views_count
            assert parse_datetime(response[i]["created"]) == ordered_posts[i].created


class TestUsersPosts:

    def test_permission_for_not_authenticated(self, api, post):
        response = api.get(reverse("v1:posts:my-posts"), expected_status_code=401)

        response = api.post(
            reverse("v1:posts:my-posts"),
            data={"content": "Test content"},
            expected_status_code=401,
        )

    def test_get_fields(self, api, auth_user, mixer):
        post_1 = mixer.blend(Post, publication_status=Post.PUBLISHED, author=auth_user)
        post_2 = mixer.blend(Post, publication_status=Post.DRAFT, author=auth_user)
        post_3 = mixer.blend(Post, publication_status=Post.DRAFT)

        response = api.get(reverse(f"v1:posts:my-posts"))
        response_results = response["results"]

        # Test response fields
        posts_serializer = PostListSerializer()
        for field in posts_serializer.fields:
            assert field in response_results[0]

        assert response_results[0]["id"] == post_2.id
        assert response_results[0]["title"] == post_2.title
        assert response_results[1]["id"] == post_1.id
        assert response_results[1]["title"] == post_1.title

        assert len(response_results) == response["count"] == 2
